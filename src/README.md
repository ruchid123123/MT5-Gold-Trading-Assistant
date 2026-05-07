# 源代码目录

此目录包含不同版本的 MT5 交易助手源代码。

## 版本说明

| 文件 | 版本 | 状态 | 说明 |
|------|------|------|------|
| `mt5_assistant_cn.py` | **新版（推荐）** | 已修复 | 黄金专用版，修复了计算逻辑和表格显示问题 |
| `main_original.py` | 旧版 | 有Bug | 从原 MT5-Trading-Assistant 仓库合并的通用版本 |

---

## 新版（推荐）- mt5_assistant_cn.py

**特点：**
- 专为黄金（XAU/USD）交易优化
- 修复了仓位计算逻辑
- 新增自动获取黄金实时价格
- 修复表格盈亏显示异常
- 新增盈亏比计算

**运行：**
```bash
python mt5_assistant_cn.py
```

## 旧版 - main_original.py

**来源：** [MT5-Trading-Assistant](https://github.com/ruchid123123/MT5-Trading-Assistant) 仓库

**注意：** 此版本存在以下已知问题：
- 仓位计算公式不正确（未正确处理黄金的点值）
- 表格盈亏显示异常（重复包装 QTableWidgetItem）
- 通用版本，未针对特定品种优化

**保留原因：** 作为原始代码参考和历史版本存档

---

## 依赖安装

```bash
pip install PyQt5 MetaTrader5
```

## 功能对比

| 功能 | 新版 mt5_assistant_cn.py | 旧版 main_original.py |
|------|-------------------------|---------------------|
| 黄金专用计算 | 是 | 否（通用） |
| 自动获取价格 | 是 | 否 |
| 计算准确性 | 已修复 | 有Bug |
| 表格显示 | 已修复 | 有Bug |
| 盈亏比显示 | 有 | 无 |

## 建议

**推荐使用 `mt5_assistant_cn.py`**，旧版仅供对比参考。

## 免责声明

本工具仅供学习研究使用，不构成投资建议。交易有风险，入市需谨慎。