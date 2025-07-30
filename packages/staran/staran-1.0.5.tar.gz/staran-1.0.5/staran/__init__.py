#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran - 企业级多功能工具库
==========================

一个现代化的Python多功能工具库，为企业应用提供一系列高质量、零依赖的解决方案。

当前模块：
- **date**: 企业级日期处理 (v1.0.2)

未来模块：
- file: 文件处理工具
- crypto: 加解密工具
- ...

快速开始 (日期处理):
    >>> from staran.date import Date
    >>> 
    >>> today = Date.today()
    >>> print(today)
    20250729
    
    >>> date = Date.from_string("20250415")
    >>> print(date.format_chinese())
    2025年04月15日
"""

__version__ = "1.0.5"
__author__ = "Staran Team"
__email__ = "team@staran.dev"
__license__ = "MIT"

# 导入核心模块
from .date import (
    Date, 
    DateLogger, 
    today, 
    from_string,
    DateError,
    InvalidDateFormatError,
    InvalidDateValueError
)

# 定义公共API
__all__ = [
    # Date 模块
    'Date',
    'DateLogger', 
    'today',
    'from_string',
    'DateError',
    'InvalidDateFormatError',
    'InvalidDateValueError',
    
    # 元数据
    '__version__',
    '__author__',
    '__email__',
    '__license__'
]
