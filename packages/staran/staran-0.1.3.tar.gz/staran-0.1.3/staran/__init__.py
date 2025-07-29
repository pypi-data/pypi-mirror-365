#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran - 简化的Python工具库
=========================

基于Python标准库的轻量级实用工具集，提供日期处理等常用功能。

主要特性：
- 零依赖：仅基于Python标准库
- 智能格式：自动记忆输入格式并保持一致性
- 直观API：符合Python习惯的设计
- 类型安全：完整的参数验证

快速开始：
---------

基本用法::

    from staran import Date
    
    # 智能格式记忆
    date1 = Date('202504')      # 输出: 202504 (年月格式)
    date2 = Date('20250415')    # 输出: 20250415 (完整格式)
    date3 = Date(2025, 4, 15)   # 输出: 2025-04-15
    
    # 格式保持
    new_date = date1.add_months(2)  # 输出: 202506 (保持原格式)

多种输出格式::

    date = Date('202504')
    
    print(date)                     # 202504 (默认格式)
    print(date.format_full())      # 2025-04-01
    print(date.format_chinese())   # 2025年04月01日
    print(date.format_compact())   # 20250401

日期运算::

    date = Date(2025, 4, 15)
    
    # 日期运算
    tomorrow = date.add_days(1)     # 2025-04-16
    next_month = date.add_months(1) # 2025-05-15
    
    # 日期比较
    other = Date(2025, 4, 20)
    diff = other.difference(date)   # 5 (天数差)
    print(date < other)             # True

创建方式::

    # 多种创建方式
    today = Date()                  # 今日
    birthday = Date(1990, 5, 15)    # 指定日期
    event = Date('20240615')        # 从字符串
    deadline = Date(year=2024, month=12, day=31)  # 关键字参数

格式化选项::

    date = Date('202504')
    
    # 常用格式
    date.format_default()           # 202504 (默认)
    date.format_full()              # 2025-04-01 (完整)
    date.format_year_month()        # 2025-04 (年月)
    date.format_chinese()           # 2025年04月01日 (中文)
    date.format_iso()               # 2025-04-01 (ISO)
    date.format_us()                # 04/01/2025 (美式)
    date.format_european()          # 01/04/2025 (欧式)

核心功能：
---------
- Date: 智能日期类，支持格式记忆和多种输出
- 日期运算：add_days(), add_months()
- 格式化：多种预设格式方法
- 比较：支持标准比较操作符
- 转换：to_timestamp(), to_date(), to_datetime()
- 信息：is_leap_year(), weekday(), days_in_month()

版本信息：
---------
- 版本: 1.0.0
- 许可: MIT
- 作者: Staran Team
"""

# 导入主要功能
from .tools import Date

# 主要导出
__all__ = [
    'Date'
]

# 包信息
__version__ = '1.0.0'
__author__ = 'Staran Team'
__description__ = 'Simple Python utilities with smart format memory'
__license__ = 'MIT'

# 便捷函数示例
def help_examples():
    """
    显示Staran使用示例
    
    Returns:
        None: 打印示例到控制台
    """
    print("""
Staran 使用示例
===============

1. 基本创建：
   from staran import Date
   
   date1 = Date('202504')      # 202504
   date2 = Date('20250415')    # 20250415  
   date3 = Date(2025, 4, 15)   # 2025-04-15

2. 格式保持：
   date = Date('202504')
   new_date = date.add_months(2)  # 202506 (保持格式)

3. 多种格式：
   date.format_full()         # 2025-04-01
   date.format_chinese()      # 2025年04月01日
   date.format_compact()      # 20250401

4. 日期运算：
   date.add_days(30)          # 增加30天
   date.add_months(2)         # 增加2个月
   date.difference(other)     # 计算天数差

更多信息请查看: help(Date)
    """)

# 快捷访问帮助
def examples():
    """显示使用示例的快捷方法"""
    help_examples()
