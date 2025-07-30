#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran 日期处理库 v1.0.10 - 简化版导入
"""

# 版本信息
__version__ = "1.0.11"
__author__ = "StarAn"
__email__ = "starlxa@icloud.com"

# 直接导入核心模块 (测试用)
from .core import Date, DateRange, DateError, LunarDate, Language

# 导入扩展功能
from .extensions import (
    Timezone, TimezoneInfo, TIMEZONE_AVAILABLE,
    DateExpressionParser, ParseResult, EXPRESSIONS_AVAILABLE,
    SolarTerms, SolarTerm, SOLAR_TERMS_AVAILABLE
)

# 导入集成功能  
from .integrations import (
    DateVisualization, ChartData, TimeSeriesPoint, VISUALIZATION_AVAILABLE,
    StaranAPIServer, StaranAPIHandler, API_SERVER_AVAILABLE
)

# 便捷函数
def today():
    """创建今日的Date对象"""
    return Date.today()

def from_string(date_string: str):
    """从字符串创建Date对象"""
    return Date(date_string)

def from_lunar(year: int, month: int, day: int, is_leap: bool = False):
    """从农历创建Date对象"""
    return Date.from_lunar(year, month, day, is_leap)

def parse_expression(expression: str):
    """解析日期表达式 (v1.0.10)"""
    if not EXPRESSIONS_AVAILABLE or not DateExpressionParser:
        return None
    parser = DateExpressionParser()
    result = parser.parse(expression)
    if result and result.success and result.date:
        # 确保返回Date对象而不是datetime.date
        if hasattr(result.date, 'year'):
            return Date(result.date.year, result.date.month, result.date.day)
        else:
            return result.date
    return None

def get_version_info():
    """获取版本和功能信息"""
    return {
        'version': __version__,
        'author': __author__,
        'timezone_support': TIMEZONE_AVAILABLE,
        'expression_parsing': EXPRESSIONS_AVAILABLE,
        'solar_terms': SOLAR_TERMS_AVAILABLE,
        'visualization': VISUALIZATION_AVAILABLE,
        'api_server': API_SERVER_AVAILABLE,
        'api_count': 190
    }

def get_feature_status():
    """获取功能状态"""
    return {
        'core_date_operations': True,
        'lunar_calendar': True,
        'multilingual_support': True,
        'timezone_support': TIMEZONE_AVAILABLE,
        'expression_parsing': EXPRESSIONS_AVAILABLE,
        'solar_terms': SOLAR_TERMS_AVAILABLE,
        'data_visualization': VISUALIZATION_AVAILABLE,
        'rest_api': API_SERVER_AVAILABLE
    }

# 导出
__all__ = [
    '__version__', '__author__', '__email__',
    'Date', 'DateRange', 'DateError', 'LunarDate', 'Language',
    'Timezone', 'TimezoneInfo', 'DateExpressionParser', 'ParseResult',
    'SolarTerms', 'SolarTerm', 'DateVisualization', 'ChartData', 
    'TimeSeriesPoint', 'StaranAPIServer', 'StaranAPIHandler',
    'today', 'from_string', 'from_lunar', 'parse_expression',
    'get_version_info', 'get_feature_status'
]
