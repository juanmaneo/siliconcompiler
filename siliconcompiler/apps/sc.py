# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.

#Standard Modules
import os
import sys

import siliconcompiler
from siliconcompiler.utils import get_default_iomap

###########################
def main():


    progname = "sc"
    description = """
    ------------------------------------------------------------
    SiliconCompiler is an open source compiler framework that
    aims to enable automated translation from source code to
    silicon.

    The sc program includes the followins steps.

    1. Read command line arguments
    2. If not set, 'design' is set to base of first source file.
    3. If not set, 'target' is set to 'asicflow_freepdk45.
    4. Run compilation
    5. Display summary

    Sources: https://github.com/siliconcompiler/siliconcompiler
    ------------------------------------------------------------
    """
    # TODO: this is a hack to get around design name requirement: since legal
    # design names probably can't contain spaces, we can detect if it is unset.
    UNSET_DESIGN = '  unset  '

    # Create a base chip class.
    chip = siliconcompiler.Chip(UNSET_DESIGN)

    # Read command-line inputs and generate Chip objects to run the flow on.
    chip.create_cmdline(progname,
                        description=description,
                        input_map=get_default_iomap())

    # Set design if none specified
    if chip.get('design') == UNSET_DESIGN:
        topfile = None
        for sourceset in ('rtl', 'hll'):
            if chip.valid('input', sourceset):
                for filetype in chip.getkeys('input', sourceset):
                    sources = chip.get('input', sourceset, filetype)
                    if sources:
                        topfile = sources[0]
                        break
            if topfile:
                break

        if not topfile:
            chip.logger.error('Invalid arguments: either specify -design or provide sources.')
            sys.exit(1)

        topmodule = os.path.splitext(os.path.basename(topfile))[0]
        chip.set('design', topmodule)

    # Set demo target if none specified
    if not chip.get('option', 'target'):
        chip.load_target('skywater130_demo')

    # Storing user entered steplist/args before running
    if chip.get('arg','step'):
        steplist = [chip.get('arg','step')]
    else:
        steplist = chip.get('option', 'steplist')

    # Run flow
    chip.run()

    # Print Job Summary
    chip.summary(steplist=steplist)

#########################
if __name__ == "__main__":

    sys.exit(main())
