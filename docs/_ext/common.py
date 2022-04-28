from docutils import nodes
from sphinx.util.nodes import nested_parse_with_titles
from docutils.statemachine import ViewList

from siliconcompiler.schema import schema_cfg

# Docutils helpers
def build_table(items):
    table = nodes.table()
    table['classes'] = ['longtable']

    group = nodes.tgroup(cols=len(items[0]))
    table += group
    for _ in items[0]:
        # not sure how colwidth affects things - columns seem to adjust to contents
        group += nodes.colspec(colwidth=100)

    body = nodes.tbody()
    group += body

    for row in items:
        row_node = nodes.row()
        body += row_node
        for col in row:
            entry = nodes.entry()
            row_node += entry
            entry += col

    return table

def build_section(text, key):
    sec = nodes.section(ids=[nodes.make_id(key)])
    sec += nodes.title(text=text)
    return sec

def build_section_with_target(text, key, ctx):
    id = nodes.make_id(key)
    target = nodes.target('', '', ids=[id], names=[id])
    sec = nodes.section(ids=[id])
    sec += nodes.title(text=text)

    # We don't need to add target node to hierarchy, just need to call this
    # function.
    ctx.note_explicit_target(target)

    return sec

def para(text):
    return nodes.paragraph(text=text)

def code(text):
    return nodes.literal(text=text)

def literalblock(text):
    block = nodes.literal_block(text=text)
    block['language'] = 'none'
    return block

def strong(text):
    p = nodes.paragraph()
    p += nodes.strong(text=text)
    return p

def image(src, center=False):
    i = nodes.image()
    i['uri'] = '/' + src
    if center:
        i['align'] = 'center'
    return i

def link(url, text=None):
    if text is None:
        text = url
    return nodes.reference(internal=False, refuri=url, text=text)

def build_list(items, enumerated=False):
    if enumerated:
        list = nodes.enumerated_list()
    else:
        list = nodes.bullet_list()

    for item in items:
        docutils_item = nodes.list_item()
        docutils_item += item
        list += docutils_item

    return list

# SC schema helpers
def is_leaf(schema):
    if 'defvalue' in schema:
        return True
    elif len(schema.keys()) == 1 and 'default' in schema:
        return is_leaf(schema['default'])
    return False

def flatten(cfg, prefix=()):
    flat_cfg = {}

    for key, val in cfg.items():
        if key == 'default': continue
        if 'defvalue' in val:
            flat_cfg[prefix + (key,)] = val
        else:
            flat_cfg.update(flatten(val, prefix + (key,)))

    return flat_cfg

def keypath(*args):
    '''Helper function for displaying Schema keypaths.'''
    text_parts = []
    key_parts = []
    cfg = schema_cfg()
    for key in args:
        if list(cfg.keys()) != ['default']:
            text_parts.append(f"'{key}'")
            key_parts.append(key)
            try:
                cfg = cfg[key]
            except KeyError:
                raise ValueError(f'Invalid keypath {args}')
        else:
            cfg = cfg['default']
            if key.startswith('<') and key.endswith('>'):
                # Placeholder
                text_parts.append(key)
            else:
                # Fully-qualified
                text_parts.append(f"'{key}'")

    if 'help' not in cfg:
        # Not leaf
        text_parts.append('...')

    text = f"[{', '.join(text_parts)}]"
    refid = '-'.join(key_parts)
    # TODO: figure out URL automatically/figure out internal ref for PDF
    url = f'https://docs.siliconcompiler.com/en/latest/reference_manual/schema.html#{refid}'

    # Note: The literal node returned by code() must be a child of the reference
    # node (not the other way round), otherwise the Latex builder mangles the
    # URL.
    ref_node = nodes.reference(internal=False, refuri=url)
    text_node = code(text)
    ref_node += text_node

    return ref_node
