import marshal, dis, sys

with open('mt5tradingassistant.pyc', 'rb') as f:
    data = f.read()
    start = data.find(b'\xe3')
    if start != -1:
        code = marshal.loads(data[start:])
        with open('mt5tradingassistant.dis', 'w', encoding='utf-8') as out:
            dis.dis(code, file=out)
            # Also disassemble inner code objects (functions/classes)
            def dis_recursive(co, out):
                for const in co.co_consts:
                    if hasattr(const, 'co_code'):
                        out.write(f"\n\n--- Disassembly of {const.co_name} ---\n")
                        dis.dis(const, file=out)
                        dis_recursive(const, out)
            dis_recursive(code, out)
