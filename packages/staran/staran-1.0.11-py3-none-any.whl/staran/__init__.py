#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran - 企业级Python日期处理库
"""

__version__ = "1.0.11"
__author__ = "StarAn"
__email__ = "starlxa@icloud.com"
__license__ = "MIT"

# 导入核心功能
try:
    from .date import (
        Date, 
        DateRange,
        DateError,
        LunarDate,
        Language,
        today, 
        from_string,
        from_lunar,
        parse_expression,
        get_version_info,
        get_feature_status
    )
except ImportError as e:
    import warnings
    warnings.warn(f"Staran核心功能导入失败: {e}")
    
    Date = None
    DateRange = None
    DateError = Exception
    LunarDate = None
    Language = None
    
    def today():
        raise ImportError("Staran核心功能不可用")
    
    def from_string(date_string: str):
        raise ImportError("Staran核心功能不可用")
    
    def from_lunar(year: int, month: int, day: int, is_leap: bool = False):
        raise ImportError("Staran核心功能不可用")
    
    def parse_expression(expression: str):
        raise ImportError("Staran核心功能不可用")
    
    def get_version_info():
        return {'version': __version__, 'status': 'core_unavailable'}
    
    def get_feature_status():
        return {'core_available': False}

__all__ = [
    '__version__', '__author__', '__email__', '__license__',
    'Date', 'DateRange', 'DateError', 'LunarDate', 'Language',
    'today', 'from_string', 'from_lunar', 'parse_expression',
    'get_version_info', 'get_feature_status'
]
