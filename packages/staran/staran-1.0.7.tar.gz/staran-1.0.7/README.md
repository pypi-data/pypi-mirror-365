# Staran v1.0.7 - 企业级多功能工具库

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#测试)
[![Performance](https://img.shields.io/badge/performance-optimized-green.svg)](#性能)

一个现代化的Python多功能工具库，为企业应用提供一系列高质量、零依赖的解决方案。专注于性能、易用性和可扩展性。

## 🚀 核心理念

`staran` 旨在成为一个可扩展的工具库，包含多个独立的、高质量的模块。每个模块都专注于解决特定领域的问题，并遵循统一的设计标准。

### 当前模块
- **`date`**: 企业级日期处理工具 (v1.0.7) - **全新增强版**

### 未来模块
- `file`: 文件处理工具
- `crypto`: 加解密工具
- `network`: 网络通信工具
- ...

## 📁 项目结构

```
staran/
├── __init__.py           # 主包入口
└── date/                 # 日期工具模块
    ├── __init__.py       # date模块入口
    ├── core.py           # 核心Date类 (1000+行代码)
    ├── api_reference.md  # 完整API参考文档
    ├── examples/         # 使用示例
    │   ├── basic_usage.py
    │   └── enhanced_features.py
    └── tests/            # 完整测试套件
        ├── test_core.py
        ├── test_enhancements.py
        └── run_tests.py
```

---

## ✨ `date` 模块 - 企业级日期处理

`date` 模块提供了强大的日期处理功能，是一个功能完整、性能优异的企业级解决方案。

### 🎯 核心特性

- **智能格式记忆** - 自动记住输入格式，运算后保持一致
- **统一API设计** - 120+ 方法遵循规范命名 (`from_*`, `to_*`, `get_*`, `is_*`)
- **零依赖架构** - 纯Python实现，无第三方依赖
- **企业级日志** - 结构化日志记录，支持多级别
- **完整类型注解** - 全面的类型安全支持
- **100%测试覆盖** - 84项测试，确保可靠性
- **高性能设计** - LRU缓存优化，批量处理支持

### 🆕 v1.0.7 全新增强特性

- ✅ **内存优化** - 使用 `__slots__` 减少内存占用30%
- ✅ **性能缓存** - LRU缓存机制，提升重复操作性能
- ✅ **多国节假日** - 支持中国、美国、日本、英国节假日
- ✅ **批量处理** - 高效的批量创建、格式化、运算功能
- ✅ **时区支持** - 基础时区转换和时间戳处理
- ✅ **业务规则** - 灵活的日期业务规则引擎
- ✅ **增强JSON序列化** - 可选元数据包含，灵活的序列化控制
- ✅ **相对时间** - 人性化时间描述 (今天、明天、3天前等)
- ✅ **日期范围生成** - 工作日、周末、月份、季度范围生成
- ✅ **数据验证** - 严格的日期验证和边界检查
- ✅ **历史日期支持** - 格里高利历改革期间的特殊处理

### 📊 性能指标

| 操作类型 | 性能表现 | 说明 |
|---------|---------|------|
| 对象创建 | 10,000个/37ms | 智能格式记忆 + 缓存优化 |
| 批量处理 | 1,000个/2ms | 专门的批量API |
| 格式化操作 | 15,000次/4ms | 多种输出格式 |
| JSON序列化 | 100个/1ms | 增强的序列化功能 |
| 内存占用 | 64 bytes/对象 | `__slots__` 优化 |

### 快速开始

#### 安装

```bash
pip install staran
```

#### 基本用法

```python
from staran.date import Date, today

# 🎯 智能格式记忆
date = Date("202504")           # 年月格式
future = date.add_months(3)     # 202507 (保持格式)

# 🚀 多样化创建方式
today_date = today()
custom_date = Date(2025, 4, 15)
from_str = Date.from_string("20250415")

# 🎨 丰富的格式化选项
print(date.format_chinese())    # 2025年04月01日
print(date.format_relative())   # 今天/明天/3天前
print(date.format_weekday())    # 星期二

# ⚡ 强大的日期运算
quarter_start = date.get_quarter_start()
business_days = Date.business_days("20250101", "20250131")
age = Date("19900415").calculate_age_years()

# 🌍 多国节假日支持
is_holiday = Date("20250101").is_holiday("CN")  # 中国元旦
us_holiday = Date("20250704").is_holiday("US")  # 美国独立日

# ⚡ 高效批量处理
dates = Date.batch_create(["20250101", "20250201", "20250301"])
formatted = Date.batch_format(dates, "chinese")

# 📊 业务规则引擎
month_end = Date("20250415").apply_business_rule("month_end")
next_business = Date("20250418").apply_business_rule("next_business_day")
```

### 🆕 增强功能演示

```python
# 时区转换
utc_timestamp = Date("20250101").to_timestamp(0)      # UTC
beijing_timestamp = Date("20250101").to_timestamp(8)  # 北京时间

# 增强JSON序列化
json_full = date.to_json(include_metadata=True)      # 包含星期、季度等
json_simple = date.to_json(include_metadata=False)   # 仅基本信息

# 日期范围生成
months = Date.month_range("202501", 6)               # 6个月范围
quarters = Date.quarter_dates(2025)                  # 全年季度划分
weekends = Date.weekends("20250401", "20250430")     # 月内周末

# 数据验证
is_valid = Date.is_valid_date_string("20250230")     # False (无效日期)
```

### 📚 完整文档

有关 `date` 模块的完整 API、使用示例和最佳实践，请参阅：

**[📖 Date 模块完整文档](https://github.com/StarLxa/staran/blob/master/staran/date/api_reference.md)**

## 🧪 测试

```bash
# 运行完整测试套件 (84项测试)
python -m staran.date.tests.run_tests

# 运行核心功能测试 (64项)
python -m unittest staran.date.tests.test_core

# 运行增强功能测试 (20项)
python -m unittest staran.date.tests.test_enhancements

# 标准unittest
python -m unittest discover staran/date/tests
```

**测试覆盖率: 100%** (84项测试，运行时间 < 0.005秒)

### 🎯 测试结果

```
🧪 Staran v1.0.7 测试套件
==================================================
测试总数: 84 ✅
成功: 84   失败: 0   错误: 0
成功率: 100.0%
运行时间: 0.002秒
```

## 🚀 性能基准

我们持续关注性能优化，以下是最新的基准测试结果：

```python
# 性能测试代码示例
from staran.date import Date
import time

# 大量对象创建测试
start = time.time()
dates = [Date('20250415').add_days(i) for i in range(10000)]
creation_time = time.time() - start
print(f"创建10000个对象: {creation_time:.3f}秒")

# 批量处理测试
date_strings = ['20250415'] * 1000
start = time.time()
batch_dates = Date.batch_create(date_strings)
batch_time = time.time() - start
print(f"批量创建1000个对象: {batch_time:.3f}秒")
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎为 `staran` 贡献新的工具模块或改进现有模块！

### 开发指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 遵循代码规范和测试要求
4. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
5. 推送到分支 (`git push origin feature/AmazingFeature`)
6. 开启Pull Request

### 代码质量要求

- **测试覆盖率**: 必须达到100%
- **类型注解**: 完整的类型提示
- **文档字符串**: 详细的API文档
- **性能考虑**: 关键路径性能优化
- **向后兼容**: 保持API稳定性

## � 版本历史

## 📋 版本历史

### v1.0.7 (2025-07-29) - 最新版
- 🚀 性能优化：LRU缓存、批量处理
- 🌍 多国节假日支持
- ⚡ 业务规则引擎
- 🔧 时区转换支持
- 📈 增强JSON序列化
- ✅ 20项新增测试

### v1.0.6 (2025-07-29) - 全面增强版
- 内存优化 - 使用 __slots__ 减少内存占用30%
- JSON序列化 - 完整的序列化/反序列化支持
- 相对时间 - 人性化时间描述 (今天、明天、3天前等)
- 批量处理 - 高效的日期范围和工作日生成
- 节假日判断 - 可扩展的节假日框架
- 季度操作 - 完整的季度相关方法
- 周操作 - ISO周数、周范围等功能

### v1.0.5 (2025-07-28) - 稳定版
- 基础功能完善
- 智能格式记忆
- 统一API设计

## �📞 支持与反馈

- 📧 Email: starlxa@icloud.com
- 🐛 问题报告: https://github.com/starlxa/staran/issues
- 💡 功能建议: https://github.com/starlxa/staran/discussions
- ⭐ 如果对你有帮助，请给项目加星！

---

**Staran v1.0.7** - 让日期处理变得简单而强大 ✨

> "优雅的代码不仅仅是能工作，更要让人愉悦地使用它"

