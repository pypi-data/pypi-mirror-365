#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran Date 模块
================

提供企业级日期处理功能。

v1.0.8 新增功能：
- 农历日期支持
- 多语言本地化
- 全局语言配置
"""

__version__ = "1.0.8"
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

# 导入新增的农历和多语言功能 (v1.0.8)
from .lunar import LunarDate
from .i18n import Language

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

def from_lunar(year: int, month: int, day: int, is_leap: bool = False) -> Date:
    """
    从农历日期创建Date对象 (v1.0.8)
    
    Args:
        year: 农历年份
        month: 农历月份
        day: 农历日期
        is_leap: 是否闰月
        
    Returns:
        对应的公历Date对象
    """
    return Date.from_lunar(year, month, day, is_leap)

def set_language(language_code: str) -> None:
    """
    设置全局语言 (v1.0.8)
    
    一次设置，全局生效。支持中简、中繁、日、英四种语言。
    
    Args:
        language_code: 语言代码
            - 'zh_CN': 中文简体
            - 'zh_TW': 中文繁体  
            - 'ja_JP': 日语
            - 'en_US': 英语
    """
    Date.set_language(language_code)

def get_language() -> str:
    """
    获取当前全局语言设置 (v1.0.8)
    
    Returns:
        当前语言代码
    """
    return Date.get_language()

# 定义公共API
__all__ = [
    # 核心类
    'Date',
    'DateLogger',
    'DateError',
    'InvalidDateFormatError', 
    'InvalidDateValueError',
    
    # v1.0.8 新增类
    'LunarDate',
    'Language',
    
    # 便捷函数
    'today',
    'from_string',
    
    # v1.0.8 新增函数
    'from_lunar',
    'set_language',
    'get_language'
]
