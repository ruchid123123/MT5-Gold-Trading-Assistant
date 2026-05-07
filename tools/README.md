# 逆向分析工具

此目录包含用于分析原始程序的各种脚本工具。

## 文件说明

| 文件 | 功能 |
|------|------|
| `check_header.py` | 检查 PyInstaller 文件头 |
| `disassemble_pyc.py` | 反编译 pyc 文件 |
| `extract_strings.py` | 提取程序中的字符串 |
| `extract_strings_v2.py` | 字符串提取工具（改进版） |
| `test_marshal.py` | 测试 marshal 加载 |

## 使用方法

```bash
python disassemble_pyc.py ../original/mt5tradingassistant.pyc
```

## 依赖

```bash
pip install uncompyle6 pycdc
```