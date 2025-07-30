# Staran ✨ v1.0.0 - 轻量级Python日期工具库

- 🔧 **完善的包管理** - 优化setup.py配置，专注核心日期功能
- 🗓️ **智能日期处理** - 支持多种日期格式，自动格式记忆
- 📅 **灵活日期运算** - 便捷的日期加减运算，保持原格式
- 🎯 **简洁易用** - 专注日期处理，轻量级设计
- 🔄 **格式转换** - 支持多种日期格式输出
- 📦 **零依赖** - 只使用Python标准库，无外部依赖

## 🎯 专为日期处理设计的Python工具库

Staran是一个轻量级的日期处理工具库，提供智能的日期格式记忆和便捷的日期运算功能。特别适合需要处理多种日期格式的应用场景。

## ✨ v1.0.0 新特性

🎉 **稳定版本发布** - 核心功能完备，API稳定

- 🔧 **完善的包管理** - 优化setup.py配置，专注核心功能
- 📦 **轻量化重构** - 移除非核心模块，专注日期处理
- 🗓️ **智能格式记忆** - 根据输入自动记住日期格式
- 📅 **丰富的运算功能** - 支持天数和月数的加减运算
- 🎯 **零外部依赖** - 只使用Python标准库
- 🔄 **多种输出格式** - 支持中文、ISO等多种格式输出

## 🚧 v1.1.0 计划中的企业级优化

> **注意：** 当前v1.0.0版本具备完整的核心功能，但在企业工程化标准方面还有提升空间。
> 我们将在v1.1.0版本中完成以下企业级优化：

### 🔬 **代码质量提升**
- ✅ **类型注解** - 完整的typing支持和类型检查
- ✅ **单元测试** - 100%代码覆盖率的测试套件
- ✅ **文档规范** - 完善的docstring和API文档
- ✅ **异常处理** - 标准化的异常体系和错误码

### 🏗️ **架构优化**
- ✅ **性能优化** - 缓存机制和延迟计算
- ✅ **配置管理** - 支持配置文件和环境变量
- ✅ **日志系统** - 结构化日志和调试支持
- ✅ **插件架构** - 可扩展的格式化器和验证器

### 🛡️ **企业级特性**
- ✅ **输入验证** - 严格的数据验证和清洗
- ✅ **国际化支持** - 多语言和时区处理
- ✅ **向后兼容** - API版本管理和迁移指南
- ✅ **安全考虑** - 输入安全和数据保护

### 📊 **开发体验**
- ✅ **IDE支持** - 完整的代码提示和自动完成
- ✅ **调试工具** - 丰富的调试信息和工具
- ✅ **基准测试** - 性能基准和监控
- ✅ **CI/CD集成** - 自动化测试和发布流程

## ⚠️ 当前版本限制

v1.0.0是一个功能完备的稳定版本，但请注意以下企业级使用的限制：

### 📝 **代码质量**
- **类型检查**: 当前缺少typing注解，IDE代码提示可能不完整
- **测试覆盖**: 没有自动化测试套件，建议在生产环境使用前进行充分测试
- **异常处理**: 异常信息可能不够详细，调试时需要注意

### 🏗️ **架构限制**
- **性能**: 没有缓存机制，频繁计算可能影响性能
- **配置**: 不支持配置文件，所有设置需要在代码中硬编码
- **日志**: 没有内置日志系统，调试信息有限

### 🛡️ **企业特性**
- **验证**: 输入验证相对简单，复杂场景可能需要额外验证
- **国际化**: 目前只支持基本的中文格式，缺少完整的i18n支持
- **安全**: 没有特殊的安全考虑，输入数据请自行验证

> 💡 **建议**: 如果您需要在企业级生产环境中使用，建议等待v1.1.0版本，或者基于当前版本进行二次开发。

## 🚀 快速开始

### 安装
```bash
pip install staran
```

### 基础用法 - 智能日期处理

```python
from staran import Date

# 创建日期 - 智能格式记忆
date1 = Date('202504')      # 输出: 202504 (记住年月格式)
date2 = Date('20250415')    # 输出: 20250415 (记住完整格式)
date3 = Date(2025, 4, 15)   # 输出: 2025-04-15

# 日期运算保持格式
new_date = date1.add_months(2)  # 输出: 202506 (保持YYYYMM格式)

# 多种格式输出
print(date2.format_chinese())   # 输出: 2025年04月15日
print(date2.format_iso())       # 输出: 2025-04-15
```

## 📚 核心功能

### 🗓️ Date类 - 智能日期处理

#### 创建日期对象

```python
from staran import Date

# 字符串格式（自动识别）
date1 = Date('2025')        # 年份
date2 = Date('202504')      # 年月
date3 = Date('20250415')    # 年月日

# 参数格式
date4 = Date(2025, 4, 15)   # 年, 月, 日
date5 = Date(year=2025, month=4, day=15)

# 从datetime对象
from datetime import datetime
date6 = Date(datetime.now())
```

#### 日期运算

```python
# 加减天数
tomorrow = date.add_days(1)
yesterday = date.add_days(-1)

# 加减月数
next_month = date.add_months(1)
last_month = date.add_months(-1)

# 月末日期
month_end = date.month_end()

# 月初日期
month_start = date.month_start()
```

#### 格式化输出

```python
date = Date('20250415')

print(date)                    # 20250415 (保持原格式)
print(date.format_iso())       # 2025-04-15
print(date.format_chinese())   # 2025年04月15日
print(date.format_slash())     # 2025/04/15
print(date.format_dot())       # 2025.04.15
```

#### 日期比较

```python
date1 = Date('20250415')
date2 = Date('20250416')

print(date1 < date2)    # True
print(date1 == date2)   # False
print(date1 > date2)    # False
```

## 🎯 特色功能

### 智能格式记忆

Date类会根据输入格式自动选择默认输出格式：

```python
# 年月格式 - 输出保持YYYYMM
date_ym = Date('202504')
print(date_ym)                    # 202504
print(date_ym.add_months(1))      # 202505

# 完整格式 - 输出保持YYYYMMDD
date_full = Date('20250415')
print(date_full)                  # 20250415
print(date_full.add_days(1))      # 20250416
```

### 灵活的日期运算

```python
date = Date('202504')

# 月份运算
print(date.add_months(3))    # 202507
print(date.add_months(-2))   # 202502

# 季度运算
print(date.add_months(3))    # 下一季度

# 年份运算
print(date.add_months(12))   # 明年同月
```

## 🛠️ 高级用法

### 批量日期处理

```python
from staran import Date

# 生成日期序列
start_date = Date('202501')
dates = []
for i in range(12):
    dates.append(start_date.add_months(i))

print(dates)  # ['202501', '202502', ..., '202512']
```

### 与datetime互操作

```python
from staran import Date
from datetime import datetime

# Date转datetime
date = Date('20250415')
dt = date.to_datetime()

# datetime转Date
dt = datetime.now()
date = Date(dt)
```

## 📋 API参考

### Date类方法

| 方法 | 描述 | 示例 |
|------|------|------|
| `Date(input)` | 创建日期对象 | `Date('202504')` |
| `add_days(n)` | 加减天数 | `date.add_days(7)` |
| `add_months(n)` | 加减月数 | `date.add_months(2)` |
| `month_start()` | 获取月初 | `date.month_start()` |
| `month_end()` | 获取月末 | `date.month_end()` |
| `format_iso()` | ISO格式 | `date.format_iso()` |
| `format_chinese()` | 中文格式 | `date.format_chinese()` |
| `format_slash()` | 斜杠格式 | `date.format_slash()` |
| `format_dot()` | 点分格式 | `date.format_dot()` |
| `to_datetime()` | 转datetime | `date.to_datetime()` |

## 🤝 贡献

欢迎提交Issues和Pull Requests！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 🔗 链接

- [GitHub仓库](https://github.com/starlxa/staran)
- [PyPI包页面](https://pypi.org/project/staran/)
- [问题反馈](https://github.com/starlxa/staran/issues)

---

**Staran** - 让日期处理变得简单而优雅 ✨
