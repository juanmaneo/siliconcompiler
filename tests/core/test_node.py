import siliconcompiler
from siliconcompiler.tools.builtin import join
from siliconcompiler.flows import asicflow


def test_builtin():
    chip = siliconcompiler.Chip('test')
    flow = 'test'
    chip.node(flow, 'A', join)

    assert chip.get('flowgraph', flow, 'A', '0', 'tool') == "builtin"
    assert chip.get('flowgraph', flow, 'A', '0', 'task') == "join"


def test_import_task():
    chip = siliconcompiler.Chip('test')
    flow = 'test'
    from siliconcompiler.tools.yosys import syn_asic
    chip.node(flow, 'A', syn_asic)

    assert chip.get('flowgraph', flow, 'A', '0', 'tool') == "yosys"
    assert chip.get('flowgraph', flow, 'A', '0', 'task') == "syn_asic"
    assert chip.get('flowgraph', flow, 'A', '0', 'taskmodule') == \
        "siliconcompiler.tools.yosys.syn_asic"


def test_string_task():
    chip = siliconcompiler.Chip('test')
    flow = 'test'
    chip.node(flow, 'A', 'siliconcompiler.tools.yosys.syn_asic')

    assert chip.get('flowgraph', flow, 'A', '0', 'tool') == "yosys"
    assert chip.get('flowgraph', flow, 'A', '0', 'task') == "syn_asic"
    assert chip.get('flowgraph', flow, 'A', '0', 'taskmodule') == \
        "siliconcompiler.tools.yosys.syn_asic"


def test_remove_node_one_index():
    chip = siliconcompiler.Chip('test')
    chip.use(asicflow, place_np=3)

    chip._remove_node('asicflow', 'place', '1')

    assert '0' in chip.getkeys('flowgraph', 'asicflow', 'place')
    assert '1' not in chip.getkeys('flowgraph', 'asicflow', 'place')
    assert '2' in chip.getkeys('flowgraph', 'asicflow', 'place')

    assert chip._check_flowgraph('asicflow')


def test_remove_node_all_index():
    chip = siliconcompiler.Chip('test')
    chip.use(asicflow, place_np=3)

    chip._remove_node('asicflow', 'place')

    assert 'place' not in chip.getkeys('flowgraph', 'asicflow')

    assert chip._check_flowgraph('asicflow')
