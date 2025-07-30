#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日期处理辅助工具
==============

提供日期处理相关的辅助函数和常量。
"""

import calendar
from typing import List, Tuple

# 常量定义
WEEKDAYS_ZH = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
WEEKDAYS_EN = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MONTHS_ZH = ['一月', '二月', '三月', '四月', '五月', '六月', 
            '七月', '八月', '九月', '十月', '十一月', '十二月']
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December']


def get_quarter(month: int) -> int:
    """获取月份对应的季度
    
    Args:
        month: 月份 (1-12)
        
    Returns:
        季度 (1-4)
    """
    return (month - 1) // 3 + 1


def get_quarter_months(quarter: int) -> List[int]:
    """获取季度包含的月份
    
    Args:
        quarter: 季度 (1-4)
        
    Returns:
        月份列表
    """
    if quarter == 1:
        return [1, 2, 3]
    elif quarter == 2:
        return [4, 5, 6]
    elif quarter == 3:
        return [7, 8, 9]
    elif quarter == 4:
        return [10, 11, 12]
    else:
        raise ValueError("季度必须在1-4之间")


def is_business_day(year: int, month: int, day: int) -> bool:
    """判断是否为工作日（简单版本，仅考虑周末）
    
    Args:
        year: 年
        month: 月
        day: 日
        
    Returns:
        是否为工作日
    """
    import datetime
    date = datetime.date(year, month, day)
    return date.weekday() < 5  # 0-4为周一到周五


def get_week_range(year: int, month: int, day: int) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """获取指定日期所在周的开始和结束日期
    
    Args:
        year: 年
        month: 月
        day: 日
        
    Returns:
        ((开始年, 开始月, 开始日), (结束年, 结束月, 结束日))
    """
    import datetime
    date = datetime.date(year, month, day)
    
    # 计算周一（周开始）
    days_since_monday = date.weekday()
    monday = date - datetime.timedelta(days=days_since_monday)
    
    # 计算周日（周结束）
    sunday = monday + datetime.timedelta(days=6)
    
    return ((monday.year, monday.month, monday.day), 
            (sunday.year, sunday.month, sunday.day))


def format_weekday(weekday: int, lang: str = 'zh') -> str:
    """格式化星期几
    
    Args:
        weekday: 星期几 (0=星期一, 6=星期日)
        lang: 语言 ('zh'=中文, 'en'=英文)
        
    Returns:
        格式化的星期几字符串
    """
    if lang == 'zh':
        return WEEKDAYS_ZH[weekday]
    elif lang == 'en':
        return WEEKDAYS_EN[weekday]
    else:
        raise ValueError("语言必须是 'zh' 或 'en'")


def format_month(month: int, lang: str = 'zh') -> str:
    """格式化月份
    
    Args:
        month: 月份 (1-12)
        lang: 语言 ('zh'=中文, 'en'=英文)
        
    Returns:
        格式化的月份字符串
    """
    if lang == 'zh':
        return MONTHS_ZH[month - 1]
    elif lang == 'en':
        return MONTHS_EN[month - 1]
    else:
        raise ValueError("语言必须是 'zh' 或 'en'")


def calculate_age(birth_year: int, birth_month: int, birth_day: int, 
                 current_year: int, current_month: int, current_day: int) -> int:
    """计算年龄
    
    Args:
        birth_year: 出生年
        birth_month: 出生月
        birth_day: 出生日
        current_year: 当前年
        current_month: 当前月
        current_day: 当前日
        
    Returns:
        年龄
    """
    age = current_year - birth_year
    
    # 如果还没到生日，年龄减1
    if (current_month, current_day) < (birth_month, birth_day):
        age -= 1
    
    return age


def get_zodiac_sign(month: int, day: int) -> str:
    """获取星座
    
    Args:
        month: 月份
        day: 日期
        
    Returns:
        星座名称
    """
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "白羊座"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "金牛座"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "双子座"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "巨蟹座"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "狮子座"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "处女座"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "天秤座"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "天蝎座"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "射手座"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "摩羯座"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "水瓶座"
    else:  # (month == 2 and day >= 19) or (month == 3 and day <= 20)
        return "双鱼座"


def get_chinese_zodiac(year: int) -> str:
    """获取生肖
    
    Args:
        year: 年份
        
    Returns:
        生肖名称
    """
    zodiacs = ['猴', '鸡', '狗', '猪', '鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊']
    return zodiacs[year % 12]
