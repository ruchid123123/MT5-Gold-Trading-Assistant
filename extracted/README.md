# 提取的运行时库

此目录包含从原始 exe 文件提取的 Python 运行时和第三方库。

## 目录结构

- `PYZ-00.pyz` - PyInstaller 打包的 Python 库压缩包
- `PYZ-00.pyz_extracted/` - 解压后的 Python 库
- `base_library.zip` - Python 基础库
- `MetaTrader5/` - MT5 Python API
- `PyQt5/` - GUI 框架
- `numpy/` - 数值计算库
- `charset_normalizer/` - 字符编码库

## 用途

这些文件可用于：
1. 分析原始程序依赖
2. 在没有 pip 的环境下运行（不推荐）
3. 学习 PyInstaller 打包结构

**建议使用 pip 安装依赖而不是使用这些提取的库。**