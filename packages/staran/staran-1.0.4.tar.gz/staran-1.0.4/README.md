# Staran v1.0.4 - 企业级多功能工具库

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#测试)

一个现代化的Python多功能工具库，为企业应用提供一系列高质量、零依赖的解决方案。

## 🚀 核心理念

`staran` 旨在成为一个可扩展的工具库，包含多个独立的、高质量的模块。每个模块都专注于解决特定领域的问题，并遵循统一的设计标准。

### 当前模块
- **`date`**: 企业级日期处理工具 (v1.0.4)

### 未来模块
- `file`: 文件处理工具
- `crypto`: 加解密工具
- ...

## 📁 项目结构

```
staran/
├── __init__.py           # 主包入口
└── date/                 # 日期工具模块
    ├── __init__.py       # date模块入口
    ├── core.py           # 核心Date类
    ├── api_reference.md  # API参考文档
    └── tests/            # date模块的测试
```

---

## ✨ `date` 模块 - 企业级日期处理

`date` 模块提供了强大的日期处理功能，具有统一API、智能格式记忆和企业级日志等特性。

### 快速开始

#### 安装

```bash
pip install staran
```

#### 基本用法

```python
from staran.date import Date, today

# 快速创建日期
today_date = today()
print(today_date)  # 2025-07-29

# 从字符串创建
date = Date.from_string("20250415")
print(date.format_chinese())  # 2025年04月15日

# 日期运算（保持格式）
future = date.add_months(3)
print(future)  # 20250715
```

### 📚 文档

有关 `date` 模块的完整 API 和用法，请参阅 **[`date` 模块 API 参考](staran/date/api_reference.md)**。

## 🧪 测试

运行 `date` 模块的完整测试套件：

```bash
# 彩色测试输出
python -m staran.date.tests.run_tests

# 标准unittest
python -m unittest staran.date.tests.test_core
```

测试覆盖率：**100%**（64项测试，涵盖所有功能模块）

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎为 `staran` 贡献新的工具模块或改进现有模块！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📞 支持

- 📧 Email: simon@wsi.hk
- 📖 文档: https://staran.readthedocs.io/
- 🐛 问题报告: https://github.com/starlxa/staran/issues

---

**Staran v1.0.4** - 让工具开发变得简单而强大 ✨

