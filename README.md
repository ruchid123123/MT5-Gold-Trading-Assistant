# MT5 黄金交易助手

一个专为黄金（XAU/USD）交易设计的 MetaTrader 5 辅助工具，提供风险计算、仓位管理和自动追踪止盈功能。

## 目录结构

```
.
├── src/                    # 重写后的源代码
│   ├── mt5_assistant_cn.py # 主程序
│   └── README.md           # 详细使用说明
├── original/               # 原始/逆向出来的文件
│   ├── mt5tradingassistant.py
│   ├── mt5tradingassistant.pyc
│   └── mt5tradingassistant.dis
├── extracted/              # 提取的运行时库
│   ├── PYZ-00.pyz
│   ├── base_library.zip
│   ├── PYZ-00.pyz_extracted/
│   ├── MetaTrader5/
│   ├── PyQt5/
│   ├── numpy/
│   └── charset_normalizer/
├── tools/                  # 逆向分析工具
│   ├── check_header.py
│   ├── disassemble_pyc.py
│   ├── extract_strings.py
│   ├── extract_strings_v2.py
│   └── test_marshal.py
└── assets/                 # 资源文件
    ├── logo.ico
    └── logo.jpeg
```

## 快速开始

```bash
cd src
python mt5_assistant_cn.py
```

## 依赖安装

```bash
pip install PyQt5 MetaTrader5
```

## 功能特点

- 黄金专用风险计算器
- 自动获取黄金实时价格
- 订单管理（部分平仓、移动止盈）
- 深色/浅色主题切换

详见 `src/README.md` 获取完整使用说明。

## 免责声明

本工具仅供学习研究使用，不构成投资建议。交易有风险，入市需谨慎。