with open('mt5tradingassistant.pyc', 'rb') as f:
    header = f.read(32)
    print(header.hex(' '))
