#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
农历计算模块
============

提供公历与农历互转功能，支持农历日期的创建、输出和比较。
基于中国传统农历历法计算，支持1900-2100年范围。
"""
from typing import Tuple, Optional, Union, TYPE_CHECKING
import datetime

if TYPE_CHECKING:
    from .core import Date


class LunarDate:
    """农历日期类
    
    支持农历与公历的互相转换，农历日期的创建和格式化输出。
    """
    
    # 农历数据表 (1900-2100年)
    _LUNAR_INFO = [
        0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
        0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
        0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
        0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
        0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
        0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
        0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
        0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
        0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
        0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0,
        0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
        0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
        0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
        0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
        0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
        0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06b20, 0x1a6c4, 0x0aae0,
        0x0a2e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,
        0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,
        0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,
        0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a2d0, 0x0d150, 0x0f252,
        0x0d520
    ]
    
    def __init__(self, year: int, month: int, day: int, is_leap: bool = False):
        self.year = year
        self.month = month
        self.day = day
        self.is_leap = is_leap
    
    @classmethod
    def from_solar(cls, solar_date):
        """从公历日期转换为农历日期"""
        if hasattr(solar_date, 'to_datetime_object'):
            solar_date = solar_date.to_datetime_object()
        
        # 计算距离1900年1月31日的天数
        base_date = datetime.date(1900, 1, 31)
        delta = solar_date - base_date
        offset = delta.days
        
        # 计算农历年份
        lunar_year = 1900
        while offset > 0:
            year_days = cls._get_lunar_year_days(lunar_year)
            if offset >= year_days:
                offset -= year_days
                lunar_year += 1
            else:
                break
        
        # 计算农历月份和日期
        lunar_month = 1
        is_leap = False
        
        while offset > 0:
            month_days = cls._get_lunar_month_days(lunar_year, lunar_month, False)
            leap_month = cls._get_leap_month(lunar_year)
            
            if offset >= month_days:
                offset -= month_days
                if lunar_month == leap_month and not is_leap:
                    leap_days = cls._get_lunar_month_days(lunar_year, lunar_month, True)
                    if offset >= leap_days:
                        offset -= leap_days
                        lunar_month += 1
                    else:
                        is_leap = True
                        break
                else:
                    lunar_month += 1
            else:
                break
        
        lunar_day = offset + 1
        return cls(lunar_year, lunar_month, lunar_day, is_leap)
    
    @classmethod
    def _get_lunar_year_days(cls, year):
        """获取农历年的总天数"""
        if year < 1900 or year > 2100:
            return 0
        
        info = cls._LUNAR_INFO[year - 1900]
        days = 0
        
        # 12个月的天数
        for month in range(1, 13):
            days += 29 if (info & (0x10000 >> month)) == 0 else 30
        
        # 闰月天数
        leap_month = cls._get_leap_month(year)
        if leap_month > 0:
            days += cls._get_lunar_month_days(year, leap_month, True)
        
        return days
    
    @classmethod
    def _get_lunar_month_days(cls, year, month, is_leap=False):
        """获取农历月的天数"""
        if year < 1900 or year > 2100:
            return 0
        
        info = cls._LUNAR_INFO[year - 1900]
        
        if is_leap:
            leap_month = cls._get_leap_month(year)
            if month != leap_month:
                return 0
            return 29 if (info & 0x10000) == 0 else 30
        else:
            return 29 if (info & (0x10000 >> month)) == 0 else 30
    
    @classmethod
    def _get_leap_month(cls, year):
        """获取闰月月份"""
        if year < 1900 or year > 2100:
            return 0
        
        info = cls._LUNAR_INFO[year - 1900]
        return info & 0xf
    
    def format_chinese(self):
        """格式化为中文"""
        leap_str = "闰" if self.is_leap else ""
        return f"农历{self.year}年{leap_str}{self.month}月{self.day}日"
