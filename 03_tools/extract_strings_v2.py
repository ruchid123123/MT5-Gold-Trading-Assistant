import marshal, sys

with open('mt5tradingassistant.pyc', 'rb') as f:
    data = f.read()
    # Find the first 0xE3 which is the start of a code object
    start = data.find(b'\xe3')
    if start != -1:
        code = marshal.loads(data[start:])
        
        def dump_strings(code_obj):
            results = []
            for const in code_obj.co_consts:
                if isinstance(const, type(code_obj)):
                    results.extend(dump_strings(const))
                elif isinstance(const, str) and len(const) > 1:
                    results.append(const)
            return results

        strings = dump_strings(code)
        for s in sorted(list(set(strings))):
            print(s)
