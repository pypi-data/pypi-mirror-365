#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
农历计算模块
============

提供公历与农历互转功能，支持农历日期的创建、输出和比较。
基于中国传统农历历法计算，支持1900-2100年范围。
"""

import datetime
from typing import Tuple, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Date


class LunarDate:
    """农历日期类
    
    支持农历与公历的互相转换，农历日期的创建和格式化输出。
    """
    
    # 农历数据表 (1900-2100年)
    # 每个数字的低12位表示12个月，第13位表示闰月月份，第14-17位表示闰月天数
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
    
    # 农历月份名称 
    _LUNAR_MONTHS = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊']
    _LUNAR_DAYS = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                   '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                   '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
    
    # 天干地支
    _TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    _DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    _ZODIAC = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
    
    def __init__(self, year: int, month: int, day: int, is_leap: bool = False):
        """初始化农历日期
        
        Args:
            year: 农历年份
            month: 农历月份
            day: 农历日期
            is_leap: 是否闰月
        """
        self.year = year
        self.month = month
        self.day = day
        self.is_leap = is_leap
        
        if not self._is_valid():
            raise ValueError(f"无效的农历日期: {year}年{month}月{day}日")
    
    def _is_valid(self) -> bool:
        """验证农历日期是否有效"""
        if not (1900 <= self.year <= 2100):
            return False
        if not (1 <= self.month <= 12):
            return False
        if not (1 <= self.day <= 30):
            return False
        return True
    
    @classmethod
    def from_solar(cls, solar_date: Union[datetime.date, 'Date']) -> 'LunarDate':
        """从公历日期转换为农历日期
        
        Args:
            solar_date: 公历日期对象
            
        Returns:
            农历日期对象
        """
        if hasattr(solar_date, 'to_datetime_object'):
            # 处理自定义Date对象
            solar_date = solar_date.to_datetime_object()
        
        year = solar_date.year
        month = solar_date.month
        day = solar_date.day
        
        # 计算距离1900年1月31日(农历1900年正月初一)的天数
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
                    # 处理闰月
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
    
    def to_solar(self) -> datetime.date:
        """转换为公历日期
        
        Returns:
            公历日期对象
        """
        # 计算农历日期距离1900年正月初一的天数
        offset = 0
        
        # 累加年份天数
        for year in range(1900, self.year):
            offset += self._get_lunar_year_days(year)
        
        # 累加月份天数
        for month in range(1, self.month):
            offset += self._get_lunar_month_days(self.year, month, False)
            # 如果有闰月且月份匹配，还要加上闰月天数
            leap_month = self._get_leap_month(self.year)
            if month == leap_month:
                offset += self._get_lunar_month_days(self.year, month, True)
        
        # 如果是闰月，还要加上正常月份的天数
        if self.is_leap:
            offset += self._get_lunar_month_days(self.year, self.month, False)
        
        # 加上日期天数
        offset += self.day - 1
        
        # 基准日期: 1900年1月31日(农历1900年正月初一)
        base_date = datetime.date(1900, 1, 31)
        return base_date + datetime.timedelta(days=offset)
    
    @classmethod
    def _get_lunar_year_days(cls, year: int) -> int:
        """获取农历年的总天数"""
        if year < 1900 or year > 2100:
            return 0
        
        info = cls._LUNAR_INFO[year - 1900]
        days = 0
        
        # 12个月的天数
        for i in range(12):
            days += 29 if (info & (0x10000 >> i)) == 0 else 30
        
        # 闰月天数
        leap_month = cls._get_leap_month(year)
        if leap_month > 0:
            days += cls._get_lunar_month_days(year, leap_month, True)
        
        return days
    
    @classmethod
    def _get_lunar_month_days(cls, year: int, month: int, is_leap: bool = False) -> int:
        """获取农历月的天数"""
        if year < 1900 or year > 2100:
            return 0
        
        info = cls._LUNAR_INFO[year - 1900]
        
        if is_leap:
            # 闰月天数
            leap_month = cls._get_leap_month(year)
            if month != leap_month:
                return 0
            return 29 if (info & 0x10000) == 0 else 30
        else:
            # 正常月份天数
            return 29 if (info & (0x10000 >> month)) == 0 else 30
    
    @classmethod
    def _get_leap_month(cls, year: int) -> int:
        """获取闰月月份，如果没有闰月返回0"""
        if year < 1900 or year > 2100:
            return 0
        
        info = cls._LUNAR_INFO[year - 1900]
        return info & 0xf
    
    def get_ganzhi_year(self) -> str:
        """获取天干地支年份"""
        # 甲子年为1984年，每60年一个周期
        offset = (self.year - 1984) % 60
        tiangan_index = offset % 10
        dizhi_index = offset % 12
        return self._TIANGAN[tiangan_index] + self._DIZHI[dizhi_index]
    
    def get_zodiac(self) -> str:
        """获取生肖"""
        return self._ZODIAC[(self.year - 1900) % 12]
    
    def format_chinese(self, include_year: bool = True, include_zodiac: bool = False) -> str:
        """格式化为中文农历日期
        
        Args:
            include_year: 是否包含年份
            include_zodiac: 是否包含生肖
            
        Returns:
            中文农历日期字符串
        """
        result = ""
        
        if include_year:
            if include_zodiac:
                result += f"{self.get_ganzhi_year()}({self.get_zodiac()})年"
            else:
                result += f"农历{self.year}年"
        
        # 月份
        if self.is_leap:
            result += f"闰{self._LUNAR_MONTHS[self.month - 1]}月"
        else:
            result += f"{self._LUNAR_MONTHS[self.month - 1]}月"
        
        # 日期
        result += self._LUNAR_DAYS[self.day - 1]
        
        return result
    
    def format_compact(self) -> str:
        """紧凑格式"""
        leap_prefix = "闰" if self.is_leap else ""
        return f"{self.year}{leap_prefix}{self.month:02d}{self.day:02d}"
    
    def format_iso_like(self) -> str:
        """类ISO格式"""
        leap_suffix = "L" if self.is_leap else ""
        return f"{self.year}-{self.month:02d}{leap_suffix}-{self.day:02d}"
    
    def __str__(self) -> str:
        """字符串表示"""
        return self.format_chinese()
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"LunarDate({self.year}, {self.month}, {self.day}, is_leap={self.is_leap})"
    
    def __eq__(self, other) -> bool:
        """相等比较"""
        if not isinstance(other, LunarDate):
            return False
        return (self.year == other.year and 
                self.month == other.month and 
                self.day == other.day and 
                self.is_leap == other.is_leap)
    
    def __lt__(self, other) -> bool:
        """小于比较"""
        if not isinstance(other, LunarDate):
            return NotImplemented
        
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        if self.is_leap != other.is_leap:
            return not self.is_leap  # 正常月份小于闰月
        return self.day < other.day
    
    def __le__(self, other) -> bool:
        """小于等于比较"""
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        """大于比较"""
        return not self <= other
    
    def __ge__(self, other) -> bool:
        """大于等于比较"""
        return not self < other
