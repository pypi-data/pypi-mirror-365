#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran 扩展功能模块
==================

包含v1.0.10新增的扩展功能：
- 时区支持
- 日期表达式解析
- 二十四节气计算
"""

try:
    from .timezone import Timezone, TimezoneInfo
    TIMEZONE_AVAILABLE = True
except ImportError:
    TIMEZONE_AVAILABLE = False
    Timezone = None
    TimezoneInfo = None

try:
    from .expressions import DateExpressionParser, ParseResult
    EXPRESSIONS_AVAILABLE = True
except ImportError:
    EXPRESSIONS_AVAILABLE = False
    DateExpressionParser = None
    ParseResult = None

try:
    from .solar_terms import SolarTerms, SolarTerm
    SOLAR_TERMS_AVAILABLE = True
except ImportError:
    SOLAR_TERMS_AVAILABLE = False
    SolarTerms = None
    SolarTerm = None

__all__ = [
    'Timezone',
    'TimezoneInfo',
    'DateExpressionParser', 
    'ParseResult',
    'SolarTerms',
    'SolarTerm',
    'TIMEZONE_AVAILABLE',
    'EXPRESSIONS_AVAILABLE',
    'SOLAR_TERMS_AVAILABLE'
]
