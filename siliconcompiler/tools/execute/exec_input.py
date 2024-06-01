import glob
import os
import stat
from siliconcompiler.tools.execute.execute import setup as tool_setup
from siliconcompiler.tools._common import input_provides


def setup(chip):
    '''
    Execute the output of the previous step directly.
    This only works if the task receives a single file.
    '''
    tool_setup(chip)

    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    tool, task = chip._get_tool_task(step, index)

    chip.set('tool', tool, 'task', task, 'input', input_provides(chip, step, index),
             step=step, index=index)


def pre_process(chip):
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    tool, _ = chip._get_tool_task(step, index)

    exec = None
    for fin in glob.glob('inputs/*'):
        if fin.endswith('.pkg.json'):
            continue
        exec = os.path.abspath(fin)
        break

    if not exec:
        chip.error(f'{step}{index} did not receive an executable file')

    chip.set('tool', tool, 'exe', exec)

    os.chmod(exec, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
