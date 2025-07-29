# Staran - 简化的Python工具库

## � 轻量级Python实用工具集

Staran是一个基于Python标准库的实用工具库，提供日期处理等常用功能，无需复杂依赖。

## 🚀 快速开始

### 安装
```bash
pip install staran
```

### 基本使用

```python
from staran import Date

# 创建日期 - 智能格式记忆
date1 = Date('202504')      # 输出: 202504 (记住年月格式)
date2 = Date('20250415')    # 输出: 20250415 (记住完整格式)
date3 = Date(2025, 4, 15)   # 输出: 2025-04-15

# 日期运算保持格式
new_date = date1.add_months(2)  # 输出: 202506 (保持YYYYMM格式)
```

## 📖 主要功能

### 1. 智能格式记忆
Date类会根据输入格式自动设置默认输出格式：

| 输入方式 | 默认输出 | 说明 |
|---------|---------|------|
| `Date('202504')` | `202504` | 年月紧凑格式 |
| `Date('20250415')` | `20250415` | 完整紧凑格式 |
| `Date(2025, 4)` | `2025-04` | 年月格式 |
| `Date(2025, 4, 15)` | `2025-04-15` | 完整格式 |

### 2. 多种输出格式
```python
date = Date('202504')

# 默认格式（保持输入风格）
print(date)                         # 202504

# 常用格式
print(date.format_full())          # 2025-04-01
print(date.format_chinese())       # 2025年04月01日
print(date.format_year_month())    # 2025-04
print(date.format_compact())       # 20250401
```

### 3. 日期运算
```python
date = Date('202504')

# 运算后保持原格式
next_month = date.add_months(1)     # 202505
tomorrow = date.add_days(1)         # 202504 (智能处理)

# 日期差计算
diff = date.difference(Date('202502'))  # 天数差
```

### 4. 基本信息
```python
date = Date(2024, 2, 29)
print(date.is_leap_year())          # True
print(date.weekday())               # 星期几
print(date.days_in_month())         # 当月天数
```

## 🎯 设计特色

- **格式智能** - 自动记忆输入格式，保持输出一致性
- **零依赖** - 仅基于Python标准库
- **直观API** - 符合Python习惯的设计
- **类型安全** - 完整的参数验证和错误处理

## 📁 项目结构

```
staran/
├── __init__.py           # 主包入口，包含使用示例
├── tools/
│   ├── __init__.py      # 工具模块
│   └── date.py          # Date类实现
├── setup.py             # 安装配置  
└── README.md            # 本文档
```

## 🧪 快速测试

```python
from staran import Date

# 测试格式记忆
date = Date('202504')
print(f"原始: {date}")                    # 202504
print(f"加2月: {date.add_months(2)}")     # 202506

# 测试多格式输出
print(f"中文: {date.format_chinese()}")   # 2025年04月01日
print(f"完整: {date.format_full()}")      # 2025-04-01
```

## 📄 许可证

MIT License

---

**Staran** - 让Python工具使用更简单 🌟
