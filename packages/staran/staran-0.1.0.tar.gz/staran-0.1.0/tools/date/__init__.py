#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date模块 - 高性能日期处理工具
支持C扩展加速和跨平台兼容
"""

from .date import Date
from .platform_utils import (
    get_today,
    date_to_timestamp, 
    days_between,
    is_leap_year_c,
    has_c_extension,
    get_platform_info,
    PlatformDateUtils
)

# 导出主要类和函数
__all__ = [
    'Date',
    'get_today',
    'date_to_timestamp',
    'days_between', 
    'is_leap_year_c',
    'has_c_extension',
    'get_platform_info',
    'PlatformDateUtils'
]

# 模块信息
__version__ = '1.0.0'
__author__ = 'Staran Team'
__description__ = 'High-performance date processing with C extension support'

# 便捷访问
def create_date(*args, **kwargs):
    """便捷的日期创建函数"""
    return Date(*args, **kwargs)

def today():
    """快速获取今日日期"""
    return Date()

def from_string(date_string):
    """从字符串创建日期"""
    return Date(date_string)

def from_timestamp(timestamp):
    """从时间戳创建日期（需要先实现该功能）"""
    import datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    return Date(dt.year, dt.month, dt.day)

# 检查C扩展状态并显示信息
if has_c_extension():
    print("✅ Date模块已加载，C扩展可用")
else:
    print("⚠️  Date模块已加载，使用Python备用实现")
