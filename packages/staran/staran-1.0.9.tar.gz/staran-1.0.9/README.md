# Staran v1.0.9 - 企业级多功能工具库

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#测试)
[![Performance](https://img.shields.io/badge/performance-optimized-green.svg)](#性能)

一个现代化的Python多功能工具库，为企业应用提供一系列高质量、零依赖的解决方案。专注于性能、易用性和可扩展性。

## 📚 文档导航

- **[API 参考文档](API_REFERENCE.md)** - 完整的API文档和使用指南
- **[更新日志](CHANGELOG.md)** - 详细的版本历史和更新记录
- **[快速开始](#快速开始)** - 立即开始使用

## 🚀 核心理念

`staran` 旨在成为一个可扩展的工具库，包含多个独立的、高质量的模块。每个模块都专注于解决特定领域的问题，并遵循统一的设计标准。

### 当前模块
- **`date`**: 企业级日期处理工具 (v1.0.9) - **智能推断与异步处理版**

### 未来模块
- `file`: 文件处理工具
- `crypto`: 加解密工具  
- `network`: 网络通信工具
- ...

## 📁 项目结构

```
staran/
├── __init__.py              # 主包入口
├── README.md                # 项目简介
├── API_REFERENCE.md         # 完整API文档
├── CHANGELOG.md             # 版本更新日志
└── date/                    # 日期工具模块
    ├── __init__.py          # date模块入口
    ├── core.py              # 核心Date类 (2000+行代码)
    ├── i18n.py              # 国际化支持
    ├── lunar.py             # 农历功能
    ├── examples/            # 使用示例
    │   ├── basic_usage.py
    │   ├── enhanced_features.py
    │   └── v109_features_demo.py
    └── tests/               # 测试套件
        ├── test_core.py
        ├── test_v108_features.py
        ├── test_v109_features.py
        └── run_tests.py
```

## ⚡ 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/StarLxa/staran.git
cd staran
pip install -e .
```

### 基本使用

```python
from staran.date import Date

# 创建日期对象
d = Date(2025, 7, 29)
print(d.format_chinese())  # 2025年7月29日

# v1.0.9 新功能 - 智能推断
smart_date = Date.smart_parse("15")  # 自动推断为本月15日
print(smart_date.format_iso())

# 异步批量处理
import asyncio
async def demo():
    dates = await Date.async_batch_create(['2025-01-01', '2025-12-31'])
    return [d.format_chinese() for d in dates]

result = asyncio.run(demo())
print(result)  # ['2025年1月1日', '2025年12月31日']
```

### v1.0.9 核心新功能

- 🧠 **智能日期推断** - 自动推断不完整的日期输入
- ⚡ **异步批量处理** - 支持大量日期的异步操作
- 📅 **日期范围操作** - 范围创建、交集、并集运算
- 📊 **数据导入导出** - CSV/JSON格式的批量数据处理
- 🚀 **性能优化缓存** - 多级缓存系统，性能提升25-40%

## 🎯 核心特性

### 企业级功能
- **120+ API方法** - 完整的日期处理解决方案
- **农历支持** - 农历与公历互转，天干地支生肖
- **多语言本地化** - 中简、中繁、日、英四种语言
- **智能格式记忆** - 自动记住输入格式
- **零依赖架构** - 纯Python实现，无第三方依赖

### 性能与质量
- **100%测试覆盖** - 188项测试全部通过
- **类型安全** - 完整的类型注解支持
- **线程安全** - 多线程环境数据一致性保证
- **内存优化** - 对象内存占用仅54字节（减少15%）

## 📊 性能基准

| 操作类型 | v1.0.9性能 | 提升幅度 |
|---------|-----------|---------|
| 对象创建 | 10,000个/28ms | 24% ↑ |
| 农历转换 | 100个/5.5ms | 31% ↑ |
| 批量处理 | 1,000个/1.2ms | 40% ↑ |
| 格式化操作 | 15,000次/3ms | 25% ↑ |
| 内存占用 | 54 bytes/对象 | 15% ↓ |

## 🧪 测试

```bash
# 运行所有测试
cd staran
python -m staran.date.tests.run_tests

# 测试统计: 188项测试，100%通过率
# - 核心功能: 126项测试
# - v1.0.8功能: 21项测试  
# - v1.0.9新功能: 21项测试
# - 增强功能: 20项测试
```

## 📖 文档

- **[API参考文档](API_REFERENCE.md)** - 完整的API文档、使用指南和示例
- **[更新日志](CHANGELOG.md)** - 详细的版本历史和功能变更

## 🛠️ 开发

### 贡献指南

```bash
# 克隆项目
git clone https://github.com/StarLxa/staran.git
cd staran

# 安装开发依赖
pip install -e .

# 运行测试
python -m staran.date.tests.run_tests
```

### 代码规范
- 遵循PEP 8代码风格
- 完整的类型注解
- 100%测试覆盖率
- 向后兼容性保证

## 📞 支持

- **GitHub Issues**: 报告Bug和功能请求
- **文档**: [API参考文档](API_REFERENCE.md)
- **示例**: 查看 `examples/` 目录

## 📄 许可证

本项目采用 MIT 许可证。详细信息请查看 [LICENSE](LICENSE) 文件。

---

**Staran v1.0.9** - 让日期处理更简单、更强大！ 🚀

*专为企业级应用设计，追求极致的性能与易用性。*
