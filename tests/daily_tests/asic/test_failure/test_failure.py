import os
import siliconcompiler
from tests.fixtures import test_wrapper

import pytest

##################################
def test_failure_notquiet():
    '''Test that SC exits early on errors without -quiet switch.

    This is a regression test for an issue where SC would only exit early on a
    command failure in cases where the -quiet switch was included.

    TODO: these tests are somewhat bad because unrelated failures can cause
    them to pass. Needs a more specific check.
    '''

    # Create instance of Chip class
    chip = siliconcompiler.Chip(loglevel='NOTSET')

    # Inserting value into configuration
    chip.add('source', '../../tests/daily_tests/asic/test_failure/bad.v')
    chip.set('design', 'bad')
    chip.set('asic', 'diearea', [(0, 0), (10, 10)])
    chip.set('asic',  'corearea', [(1, 1), (9, 9)])
    chip.set('target', 'asicflow_freepdk45')

    chip.target()

    chip.add('steplist', 'import')
    chip.add('steplist', 'syn')

    # Expect that command exits early
    with pytest.raises(SystemExit):
        chip.run()

    # Check we made it past initial setup
    assert os.path.isdir('build/bad/job0/import')
    assert os.path.isdir('build/bad/job0/syn')

    # Expect that there is no import output
    assert chip.find_result('v', step='import') is None
    # Expect that synthesis doesn't run
    assert not os.path.isdir('build/bad/job0/syn/0/inputs')

def test_failure_quiet():
    '''Test that SC exits early on errors with -quiet switch.
    '''

    # Create instance of Chip class
    chip = siliconcompiler.Chip(loglevel='NOTSET')

    # Inserting value into configuration
    chip.add('source', '../../tests/daily_tests/asic/test_failure/bad.v')
    chip.set('design', 'bad')
    chip.set('asic', 'diearea', [(0, 0), (10, 10)])
    chip.set('asic',  'corearea', [(1, 1), (9, 9)])
    chip.set('target', 'asicflow_freepdk45')

    chip.target()

    chip.add('steplist', 'import')
    chip.add('steplist', 'syn')

    chip.set('quiet', 'true')

    # Expect that command exits early
    with pytest.raises(SystemExit):
        chip.run()

    # Check we made it past initial setup
    assert os.path.isdir('build/bad/job0/import')
    assert os.path.isdir('build/bad/job0/syn')

    # Expect that there is no import output
    assert chip.find_result('v', step='import') is None
    # Expect that synthesis doesn't run
    assert not os.path.isdir('build/bad/job0/syn/0/inputs')
