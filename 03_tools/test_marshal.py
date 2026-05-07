import marshal
with open('mt5tradingassistant.pyc', 'rb') as f:
    data = f.read()
    print(f"Total size: {len(data)}")
    try:
        code = marshal.loads(data[16:])
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        # Let's try to find where it starts failing
        for i in range(16, 128):
            try:
                marshal.loads(data[i:])
                print(f"Found valid start at {i}")
                break
            except:
                pass
