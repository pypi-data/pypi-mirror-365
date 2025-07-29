#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran Tools - 工具集合模块
==========================

提供各种实用工具类和函数：

Date类 - 智能日期处理：
- 格式记忆：根据输入自动设置默认格式
- 多种创建方式：支持字符串、参数、关键字等
- 丰富格式化：提供多种预设输出格式
- 日期运算：支持天数、月数的加减运算
- 标准比较：支持日期间的比较操作

示例::

    from staran.tools import Date
    
    # 创建日期
    date = Date('202504')       # 自动记住YYYYMM格式
    full_date = Date('20250415') # 自动记住YYYYMMDD格式
    
    # 运算保持格式
    next_month = date.add_months(1)  # 输出: 202505
    
    # 多种格式输出
    print(date.format_chinese())     # 2025年04月01日
"""

# 导入date模块的主要类和函数
from .date import Date

# 主要导出
__all__ = [
    'Date'
]

# 模块信息
__version__ = '1.0.0'
__author__ = 'Staran Team'
__description__ = 'Staran utilities with smart format memory'
