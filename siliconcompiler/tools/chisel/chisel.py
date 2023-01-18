import os
import shutil

import siliconcompiler

####################################################################
# Make Docs
####################################################################
def make_docs():
    '''
    Chisel is a hardware design language that facilitates advanced circuit
    generation and design reuse for both ASIC and FPGA digital logic designs.
    Chisel adds hardware construction primitives to the Scala programming
    language, providing designers with the power of a modern programming
    language to write complex, parameterizable circuit generators that produce
    synthesizable Verilog.

    Documentation: https://www.chisel-lang.org/chisel3/docs/introduction.html

    Sources: https://github.com/chipsalliance/chisel3

    Installation: The Chisel plugin relies on having the Scala Build Tool (sbt)
    installed. Instructions: https://www.scala-sbt.org/download.html.
    '''

    chip = siliconcompiler.Chip('<design>')
    chip.set('arg','step','import')
    chip.set('arg','index','0')
    setup(chip)
    return chip

################################
# Setup Tool (pre executable)
################################

def setup(chip):
    ''' Sets up default settings on a per step basis
    '''

    tool = 'chisel'
    step = chip.get('arg','step')
    index = chip.get('arg','index')
    #TODO: fix below
    task = step

    # Standard Setup
    refdir = 'tools/'+tool
    chip.set('tool', tool, 'exe', 'sbt')
    chip.set('tool', tool, 'vswitch', '--version')
    chip.set('tool', tool, 'version', '>=1.5.5', clobber=False)

    chip.set('tool', tool, 'task', task, 'refdir', step, index,  refdir, clobber=False)
    chip.set('tool', tool, 'task', task, 'threads', step, index,  os.cpu_count(), clobber=False)

    design = chip.top()
    option = f'"runMain SCDriver --module {design} -o ../outputs/{design}.v"'
    chip.set('tool', tool, 'task', task, 'option', step, index,  option)

    # Input/Output requirements
    chip.add('tool', tool, 'task', task, 'output', step, index, chip.top() + '.v')

    chip.set('tool', tool, 'task', task, 'keep', step, index, ['build.sbt', 'SCDriver.scala'])

def parse_version(stdout):
    # sbt version in this project: 1.5.5
    # sbt script version: 1.5.5

    # grab version # by splitting on whitespace
    return stdout.split('\n')[0].split()[-1]

################################
#  Custom runtime options
################################

def runtime_options(chip):

    cmdlist = []

    # TODO: handle these parameters

    # for value in chip.find_files('ydir'):
    #     cmdlist.append('-y ' + value)
    # for value in chip.find_files('vlib'):
    #     cmdlist.append('-v ' + value)
    # for value in chip.find_files('idir'):
    #     cmdlist.append('-I' + value)
    # for value in chip.get('define'):
    #     cmdlist.append('-D' + value)
    # for value in chip.find_files('cmdfile'):
    #     cmdlist.append('-f ' + value)

    # # Set up user-provided parameters to ensure we elaborate the correct modules
    # for param in chip.getkeys('param'):
    #     value = chip.get('param', param)
    #     cmdlist.append(f'-P{param}={value}')

    return cmdlist

def pre_process(chip):
    tool = 'chisel'
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    task = step
    refdir = chip.find_files('tool', tool, 'task', task, 'refdir', step, index)[0]

    for filename in ('build.sbt', 'SCDriver.scala'):
        src = os.path.join(refdir, filename)
        dst = filename
        shutil.copyfile(src, dst)

    # Hack: Chisel driver relies on Scala files being collected into '$CWD/inputs'
    chip.set('input', 'hll', 'scala', True, field='copy')
    chip._collect(step, index)
