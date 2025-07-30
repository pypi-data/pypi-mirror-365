#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran Date 模块
================

提供企业级日期处理功能。
"""

__version__ = "1.0.6"
__author__ = "Staran Team"
__email__ = "team@staran.dev"

# 导入核心类和功能
from .core import (
    Date, 
    DateLogger,
    DateError,
    InvalidDateFormatError,
    InvalidDateValueError
)

# 导出便捷函数
def today() -> Date:
    """
    创建今日的Date对象
    """
    return Date.today()

def from_string(date_string: str) -> Date:
    """
    从字符串创建Date对象
    """
    return Date.from_string(date_string)

# 定义公共API
__all__ = [
    'Date',
    'DateLogger',
    'DateError',
    'InvalidDateFormatError', 
    'InvalidDateValueError',
    'today',
    'from_string'
]
