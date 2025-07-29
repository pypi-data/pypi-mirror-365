#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran Tools - 高性能工具集合
包含日期处理等各种实用工具
"""

# 导入date模块的主要类和函数
from .date import (
    Date,
    get_today,
    date_to_timestamp,
    days_between,
    is_leap_year_c,
    has_c_extension,
    get_platform_info,
    PlatformDateUtils,
    create_date,
    today,
    from_string,
    from_timestamp
)

# 为了向后兼容，也可以通过time模块访问
from . import date as date_module

# 主要导出
__all__ = [
    # 核心类
    'Date',
    'PlatformDateUtils',
    
    # 核心函数
    'get_today',
    'date_to_timestamp', 
    'days_between',
    'is_leap_year_c',
    'has_c_extension',
    'get_platform_info',
    
    # 便捷函数
    'create_date',
    'today',
    'from_string',
    'from_timestamp',
    
    # 子模块
    'date_module'
]

# 模块信息
__version__ = '1.0.0'
__author__ = 'Staran Team'
__description__ = 'Staran high-performance tools collection'

# 模块级便捷函数
def get_module_info():
    """获取tools模块信息"""
    return {
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'available_modules': ['date'],
        'date_c_extension': has_c_extension()
    }

# 显示加载信息
print(f"🚀 Staran Tools v{__version__} 已加载")
print(f"   📅 Date模块: {'C扩展' if has_c_extension() else 'Python实现'}")
