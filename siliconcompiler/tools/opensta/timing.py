import os
import re
from siliconcompiler import sc_open
from siliconcompiler.tools.opensta import setup as tool_setup
from siliconcompiler.tools.opensta import runtime_options as tool_runtime_options
from siliconcompiler.tools._common_asic import set_tool_task_var


def setup(chip):
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    tool, task = chip._get_tool_task(step, index)

    tool_setup(chip)

    chip.set('tool', tool, 'task', task, 'script', 'sc_timing.tcl',
             step=step, index=index, clobber=False)

    chip.set('tool', tool, 'task', task, 'threads', os.cpu_count(),
             step=step, index=index)

    # design = chip.top()

    set_tool_task_var(chip, param_key='top_n_paths',
                      default_value='10',
                      schelp='number of paths to report timing for')


def __report_map(chip, metric, basefile):
    corners = chip.getkeys('constraint', 'timing')
    mapping = {
        "power": [f"reports/power.{corner}.rpt" for corner in corners],
        "unconstrained": ["reports/unconstrained.rpt", "reports/unconstrained.topN.rpt"],
        "setuppaths": ["reports/setup.rpt", "reports/setup.topN.rpt"],
        "holdpaths": ["reports/hold.rpt", "reports/hold.topN.rpt"],
        "holdslack": ["reports/hold.rpt", "reports/hold.topN.rpt"],
        "setupslack": ["reports/setup.rpt", "reports/setup.topN.rpt"],
        "setuptns": ["reports/setup.rpt", "reports/setup.topN.rpt"],
        "holdtns": ["reports/hold.rpt", "reports/hold.topN.rpt"],
        "setupskew": ["reports/skew.setup.rpt", "reports/setup.rpt", "reports/setup.topN.rpt"],
        "holdskew": ["reports/skew.hold.rpt", "reports/hold.rpt", "reports/hold.topN.rpt"]
    }

    if metric in mapping:
        paths = [basefile]
        for path in mapping[metric]:
            if os.path.exists(path):
                paths.append(path)
        return paths
    return [basefile]


################################
# Post_process (post executable)
################################
def post_process(chip):
    '''
    Tool specific function to run after step execution
    '''

    # Check log file for errors and statistics
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    logfile = f"{step}.log"

    peakpower = []
    leakagepower = []
    # parsing log file
    with sc_open(logfile) as f:
        timescale = "s"
        metric = None
        for line in f:
            metricmatch = re.search(r'^SC_METRIC:\s+(\w+)', line)
            value = re.search(r'(\d*\.?\d)*', line)
            fmax = re.search(r'fmax = (\d*\.?\d*)', line)
            tns = re.search(r'^tns (.*)', line)
            slack = re.search(r'^worst slack (.*)', line)
            # skew = re.search(r'^\s*(.*)\s(.*) skew', line)
            power = re.search(r'^Total(.*)', line)
            if metricmatch:
                metric = metricmatch.group(1)
                continue

            if metric:
                if metric == 'timeunit':
                    timescale = f'{line.strip()}s'
                    metric = None
                if metric == 'fmax':
                    if fmax:
                        chip._record_metric(step, index, 'fmax', float(fmax.group(1)),
                                            __report_map(chip, 'fmax', logfile),
                                            source_unit='MHz')
                        metric = None
                elif metric == 'power':
                    if power:
                        powerlist = power.group(1).split()
                        leakage = powerlist[2]
                        total = powerlist[3]

                        peakpower.append(float(total))
                        leakagepower.append(float(leakage))

                        metric = None
                elif metric == 'cellarea':
                    chip._record_metric(step, index, 'cellarea', float(value.group(0)),
                                        __report_map(chip, 'cellarea', logfile),
                                        source_unit='um^2')
                    metric = None
                elif metric in ('logicdepth',
                                'cells',
                                'nets',
                                'buffers',
                                'registers',
                                'unconstrained',
                                'pins',
                                'setuppaths',
                                'holdpaths'):
                    chip._record_metric(step, index, metric, int(value.group(0)),
                                        __report_map(chip, metric, logfile))
                    metric = None
                elif metric in ('holdslack', 'setupslack'):
                    if slack:
                        chip._record_metric(step, index, metric, float(slack.group(1)),
                                            __report_map(chip, metric, logfile),
                                            source_unit=timescale)
                        metric = None
                elif metric in ('setuptns', 'holdtns'):
                    if tns:
                        chip._record_metric(step, index, metric, float(tns.group(1)),
                                            __report_map(chip, metric, logfile),
                                            source_unit=timescale)
                        metric = None
                elif metric in ('setupskew', 'holdskew'):
                    pass
                else:
                    metric = None

    if peakpower:
        chip._record_metric(step, index, 'peakpower', max(peakpower),
                            __report_map(chip, 'peakpower', logfile),
                            source_unit='W')
    if leakagepower:
        chip._record_metric(step, index, 'leakagepower', max(leakagepower),
                            __report_map(chip, 'leakagepower', logfile),
                            source_unit='W')

    drv_report = "reports/drv_violators.rpt"
    if os.path.exists(drv_report):
        drv_count = 0
        with sc_open(drv_report) as f:
            for line in f:
                if re.search(r'\(VIOLATED\)$', line):
                    drv_count += 1

        chip._record_metric(step, index, 'drvs', drv_count,
                            [drv_report, logfile])


################################
# Runtime options
################################
def runtime_options(chip):
    return tool_runtime_options(chip)
