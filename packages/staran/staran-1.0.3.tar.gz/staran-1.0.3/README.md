# Staran v1.0.3 - 企业级多功能工具库

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#测试)

一个现代化的Python多功能工具库，为企业应用提供一系列高质量、零依赖的解决方案。

## 🚀 核心理念

`staran` 旨在成为一个可扩展的工具库，包含多个独立的、高质量的模块。每个模块都专注于解决特定领域的问题，并遵循统一的设计标准。

### 当前模块
- **`date`**: 企业级日期处理工具 (v1.0.3)

### 未来模块
- `file`: 文件处理工具
- `crypto`: 加解密工具
- ...

## 📁 项目结构

```
staran/
├── __init__.py           # 主包入口，未来可集成更多工具
└── date/                 # 日期工具模块
    ├── __init__.py       # date模块入口
    ├── core.py           # 核心Date类
    ├── tests/            # date模块的测试
    ├── utils/            # date模块的工具函数
    └── examples/         # date模块的示例
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

### 📚 `date` 模块详细文档

#### 1. 创建日期对象

```python
from staran.date import Date

# 多种创建方式
d1 = Date(2025, 4, 15)                    # 从参数
d2 = Date.from_string("202504")           # 从字符串（智能解析）
d3 = Date.from_string("20250415")         # 完整格式
d4 = Date.from_string("2025")             # 年份格式
d5 = Date.today()                         # 今日
```

#### 2. 智能格式记忆

`date` 模块会记住输入格式，并在运算后保持相同格式：

```python
year_date = Date.from_string("2025")
print(year_date.add_years(1))    # 2026

month_date = Date.from_string("202504")
print(month_date.add_months(2))  # 202506

full_date = Date.from_string("20250415")
print(full_date.add_days(10))    # 20250425
```

#### 3. 统一API命名

`date` 模块遵循统一的API命名规范，如 `from_*`, `to_*`, `get_*`, `is_*`, `add_*/subtract_*` 等，具体请参考 `staran/date/examples/basic_usage.py`。

#### 4. 异常处理

`date` 模块提供了一套清晰的异常类，以便更好地处理错误：

- `DateError`: 所有日期相关错误的基类。
- `InvalidDateFormatError`: 当输入字符串格式不正确时抛出。
- `InvalidDateValueError`: 当日期值无效时（如月份为13）抛出。

**示例:**
```python
from staran.date import Date, InvalidDateValueError, InvalidDateFormatError

try:
    Date("2025", 13, 1)
except InvalidDateValueError as e:
    print(e)

try:
    Date("invalid-date")
except InvalidDateFormatError as e:
    print(e)
```

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

- 📧 Email: team@staran.dev
- 📖 文档: https://staran.readthedocs.io/
- 🐛 问题报告: https://github.com/starlxa/staran/issues

---

**Staran v1.0.3** - 让工具开发变得简单而强大 ✨
