import os
import subprocess
import re
import sys
import siliconcompiler

from siliconcompiler.schema import schema_path

################################
# Setup Tool (pre executable)
################################

def setup_tool(chip, step):
    ''' Per tool function that returns a dynamic options string based on
    the dictionary settings.
    '''

    # Standard Setup
    tool = 'ghdl'
    chip.add('eda', tool, step, 'threads', '4')
    chip.add('eda', tool, step, 'format', 'cmdline')
    chip.add('eda', tool, step, 'copy', 'false')
    chip.add('eda', tool, step, 'exe', 'yosys')
    chip.add('eda', tool, step, 'vendor', 'ghdl')

    # ghdl is invoked via Yosys by running a command with the format:
    #   yosys -m ghdl -p 'ghdl --std=08 --no-formal sources...; write_ilang ghdl.ilang'
    chip.add('eda', tool, step, 'option', '-m ghdl')
    chip.add('eda', tool, step, 'option', '-p \'ghdl')

    chip.add('eda', tool, step, 'option', '--std=08')
    chip.add('eda', tool, step, 'option', '--no-formal')

    # parameter overrides
    for value in chip.cfg['define']['value']:
        chip.add('eda', tool, step, 'option', '-g' + schema_path(value))

    # only use VHDL source files (*.vhd and *.vhdl)
    for value in chip.cfg['source']['value']:
        if value.endswith('.vhd') or value.endswith('.vhdl'):
            chip.add('eda', tool, step, 'option', schema_path(value))

    # determine the top modules for the VHDL import:
    # if the `undefined.morty` file is generated by a previous Verilog import,
    # then we use the undefined modules listed in that file as guesses for the
    # VHDL top modules.
    # if `undefined.morty` is not found, we assume the design top lists the
    # single VHDL top module, and return an error if it is not defined.
    modules = ""
    try:
        with open("inputs/undefined.morty", "r") as undefined_file:
            modules = undefined_file.read().strip()
    except FileNotFoundError:
        pass

    if modules == "":
        if len(chip.cfg['design']['value']) < 1:
            chip.logger.error('No top module set')
            return
        modules = chip.cfg['design']['value'][-1]

    # pass the list of top modules to GHDL for elaboration
    chip.add('eda', tool, step, 'option', '-e ' + modules)

    # generate a .ilang file (Yosys RTLIL) which can be read by Yosys during
    # synthesis along with the Verilog inputs
    chip.add('eda', tool, step, 'option', '; write_ilang ghdl.ilang\'')

################################
# Post_process (post executable)
################################

def post_process(chip, step):
    ''' Tool specific function to run after step execution
    '''

    # top module must be defined, either autodetected by morty during SV import
    # or defined manually by the user
    topmodule = chip.cfg['design']['value'][-1]
    # pass the RTLIL to the next step
    subprocess.run("cp ghdl.ilang " + "outputs/" + topmodule + ".ilang",
                   shell=True)

    # pass any pickled verilog file along as well
    # TODO: with a graph representation we may be able to remove this part so the
    # Verilog can be passed directly from the import step to the next step
    if os.path.isfile("inputs/" + topmodule + ".v"):
        subprocess.run("cp inputs/" + topmodule + ".v" + " outputs/", shell=True)

    return 0

##################################################
if __name__ == "__main__":

    # File being executed
    prefix = os.path.splitext(os.path.basename(__file__))[0]
    output = prefix + '.json'

    # create a chip instance
    chip = siliconcompiler.Chip(defaults=False)
    # load configuration
    setup_tool(chip, step='import')
    # write out results
    chip.writecfg(output)
