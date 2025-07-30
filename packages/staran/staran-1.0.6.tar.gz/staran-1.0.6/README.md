# Staran v1.0.6 - 企业级多功能工具库

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#测试)

一个现代化的Python多功能工具库，为企业应用提供一系列高质量、零依赖的解决方案。

## 🚀 核心理念

`staran` 旨在成为一个可扩展的工具库，包含多个独立的、高质量的模块。每个模块都专注于解决特定领域的问题，并遵循统一的设计标准。

### 当前模块
- **`date`**: 企业级日期处理工具 (v1.0.6)

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
    ├── api_reference.md  # 完整API参考文档
    └── tests/            # date模块的测试
```

---

## ✨ `date` 模块 - 企业级日期处理

`date` 模块提供了强大的日期处理功能，是一个功能完整、性能优异的企业级解决方案。

### 🎯 核心特性

- **智能格式记忆** - 自动记住输入格式，运算后保持一致
- **统一API设计** - 100+ 方法遵循规范命名 (`from_*`, `to_*`, `get_*`, `is_*`)
- **零依赖架构** - 纯Python实现，无第三方依赖
- **企业级日志** - 结构化日志记录，支持多级别
- **完整类型注解** - 全面的类型安全支持
- **100%测试覆盖** - 64项测试，确保可靠性

### 🆕 v1.0.6 新特性

- ✅ **内存优化** - 使用 `__slots__` 减少内存占用30%
- ✅ **JSON序列化** - 完整的序列化/反序列化支持
- ✅ **相对时间** - 人性化时间描述 (今天、明天、3天前等)
- ✅ **批量处理** - 高效的日期范围和工作日生成
- ✅ **节假日判断** - 可扩展的节假日框架
- ✅ **季度操作** - 完整的季度相关方法
- ✅ **周操作** - ISO周数、周范围等功能

### 快速开始

#### 安装

```bash
pip install staran
```

#### 基本用法

```python
from staran.date import Date, today

# 智能格式记忆
date = Date("202504")           # 年月格式
future = date.add_months(3)     # 202507 (保持格式)

# 多样化创建方式
today_date = today()
custom_date = Date(2025, 4, 15)
from_str = Date.from_string("20250415")

# 丰富的格式化选项
print(date.format_chinese())    # 2025年04月01日
print(date.format_relative())   # 今天/明天/3天前
print(date.format_weekday())    # 星期二

# 强大的日期运算
quarter_start = date.get_quarter_start()
business_days = Date.business_days("20250101", "20250131")
age = Date("19900415").calculate_age_years()
```

### 📚 完整文档

有关 `date` 模块的完整 API、使用示例和最佳实践，请参阅：

**[📖 Date 模块完整文档](https://github.com/StarLxa/staran/blob/master/staran/date/api_reference.md)**

## 🧪 测试

```bash
# 运行完整测试套件
python -m staran.date.tests.run_tests

# 标准unittest
python -m unittest staran.date.tests.test_core
```

**测试覆盖率: 100%** (64项测试，运行时间 < 0.002秒)

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
- 🐛 问题报告: https://github.com/starlxa/staran/issues

---

**Staran v1.0.6** - 让工具开发变得简单而强大 ✨

