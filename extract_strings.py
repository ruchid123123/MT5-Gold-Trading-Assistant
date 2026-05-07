import marshal, dis, sys

def dump_code(code_obj, indent=0):
    print('  ' * indent + f'Code object: {code_obj.co_name}')
    for const in code_obj.co_consts:
        if isinstance(const, type(code_obj)):
            dump_code(const, indent + 1)
        else:
            if isinstance(const, str) and len(const) > 1:
                print('  ' * (indent + 1) + f'String: {const}')

with open('mt5tradingassistant.pyc', 'rb') as f:
    f.read(16) # Skip header for Python 3.7+
    code = marshal.load(f)
    dump_code(code)
