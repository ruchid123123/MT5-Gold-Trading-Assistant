# MT5 黄金交易助手

一个专为黄金（XAU/USD）交易设计的 MetaTrader 5 辅助工具，提供风险计算、仓位管理和自动追踪止盈功能。

## 目录结构

```
.
├── 01_original/                   # 原始/逆向出来的文件
│   ├── mt5tradingassistant.py
│   ├── mt5tradingassistant.pyc
│   ├── mt5tradingassistant.dis
│   └── README.md
├── 02_extracted/                  # 提取的运行时库
│   ├── PYZ-00.pyz
│   ├── base_library.zip
│   ├── MetaTrader5/
│   ├── PyQt5/
│   ├── numpy/
│   └── README.md
├── 03_tools/                      # 逆向分析工具
│   ├── check_header.py
│   ├── disassemble_pyc.py
│   ├── extract_strings.py
│   ├── extract_strings_v2.py
│   ├── test_marshal.py
│   └── README.md
├── 04_research/                   # 逆向工程资料
│   ├── README_REVERSE_ENGINEERING.md
│   ├── raw_decompiled.py
│   └── README.md
├── 05_src/                        # 源代码（包含新旧版本）
│   ├── 01_main_original.py       # [旧版存档] 原始通用版（有Bug）
│   ├── 02_mt5_assistant_cn.py    # [新版推荐] 黄金专用修复版
│   └── README.md                 # 版本对比说明
└── 06_assets/                     # 资源文件
    ├── logo.ico
    ├── logo.jpeg
    └── README.md
```

## 快速开始

**推荐使用新版（已修复）：**
```bash
cd 05_src
python 02_mt5_assistant_cn.py
```

## 版本说明

本项目合并了两个仓库的内容：
- **新版代码**：今天修复的黄金专用版（`05_src/02_mt5_assistant_cn.py`）
- **旧版代码**：原 MT5-Trading-Assistant 仓库的通用版（`05_src/01_main_original.py`）

详见 `05_src/README.md` 了解两个版本的具体差异。

## 依赖安装

```bash
pip install PyQt5 MetaTrader5
```

## 功能特点

### 黄金专用风险计算器（新版）
- 自动获取黄金实时价格（支持 XAUUSD、GOLD、XAUUSDm 等代码）
- 基于账户余额和风险比例自动计算建议仓位
- 显示止损距离（pips）、实际风险金额
- 支持止盈计算，显示盈亏比

### 订单管理
- 实时显示持仓列表
- 部分平仓功能（10%、25%、50%、75%、100%）
- 移动止盈（TTP）：触及 TP 后自动移动止损
- 自动读取 MT5 账户余额

### 其他功能
- 深色/浅色主题切换
- 日志窗口
- 实时价格更新

## 计算说明

### 黄金计算参数
- 1标准手 = 100盎司
- 1 pip = 0.01美元
- 点值 = $1/每pip/每标准手

### 仓位计算公式
```
风险金额 = 账户余额 × 风险比例%
止损点数 = |进场价 - 止损价| / 0.01
建议手数 = 风险金额 / (止损点数 × 1)
```

## 注意事项

1. 必须先运行 MetaTrader 5 并登录账户才能使用连接功能
2. 移动止盈功能会在后台运行，关闭程序会停止监控
3. 建议先用模拟账户测试所有功能
4. **旧版 `01_main_original.py` 存在计算Bug，仅供参考对比**

## 相关仓库

- [MT5-Trading-Assistant](https://github.com/ruchid123123/MT5-Trading-Assistant) - 原仓库（旧版通用版本）

## 免责声明

本工具仅供学习研究使用，不构成投资建议。交易有风险，入市需谨慎。

## 更新日志

### v2.0 (2025-05-08)
- 合并原 MT5-Trading-Assistant 仓库内容
- 新增黄金专用计算器（修复计算逻辑）
- 自动获取黄金实时价格功能
- 修复表格显示问题
- 新增盈亏比计算
- 重新整理目录结构
- 添加数字编号

### v1.0 (2025-04-19)
- 初始版本（MT5-Trading-Assistant 仓库）
- 基础仓位计算和订单管理
- 三级止盈机制