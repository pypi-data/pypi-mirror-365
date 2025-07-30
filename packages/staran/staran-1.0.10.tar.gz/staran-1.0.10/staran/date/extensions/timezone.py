#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran 时区支持模块 v1.0.10
==========================

提供完整的时区转换和处理功能，支持全球主要时区。

主要功能：
- 时区信息管理
- 时区转换
- 夏令时支持
- 时区感知的日期操作
"""

import datetime
import time
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass

@dataclass
class TimezoneInfo:
    """时区信息类"""
    code: str  # 时区代码，如 'UTC', 'UTC+8', 'EST'
    name: str  # 时区名称
    offset: float  # UTC偏移（小时）
    description: str  # 时区描述
    country: str  # 国家/地区
    cities: List[str]  # 主要城市
    dst_offset: Optional[float] = None  # 夏令时偏移
    dst_start: Optional[str] = None  # 夏令时开始时间
    dst_end: Optional[str] = None  # 夏令时结束时间

class Timezone:
    """时区管理类"""
    
    # 全球主要时区数据
    TIMEZONE_DATA = {
        # 协调世界时
        'UTC': TimezoneInfo('UTC', 'Coordinated Universal Time', 0, 
                          '协调世界时', 'Global', ['Greenwich']),
        
        # 亚洲时区
        'UTC+8': TimezoneInfo('UTC+8', 'China Standard Time', 8,
                            '中国标准时间', 'China', ['Beijing', 'Shanghai', 'Hong Kong']),
        'JST': TimezoneInfo('JST', 'Japan Standard Time', 9,
                          '日本标准时间', 'Japan', ['Tokyo', 'Osaka']),
        'KST': TimezoneInfo('KST', 'Korea Standard Time', 9,
                          '韩国标准时间', 'Korea', ['Seoul']),
        'IST': TimezoneInfo('IST', 'India Standard Time', 5.5,
                          '印度标准时间', 'India', ['New Delhi', 'Mumbai']),
        
        # 欧洲时区
        'CET': TimezoneInfo('CET', 'Central European Time', 1,
                          '中欧时间', 'Europe', ['Paris', 'Berlin', 'Rome'],
                          dst_offset=2, dst_start='3月最后一个周日', dst_end='10月最后一个周日'),
        'GMT': TimezoneInfo('GMT', 'Greenwich Mean Time', 0,
                          '格林威治标准时间', 'UK', ['London'],
                          dst_offset=1, dst_start='3月最后一个周日', dst_end='10月最后一个周日'),
        'EET': TimezoneInfo('EET', 'Eastern European Time', 2,
                          '东欧时间', 'Europe', ['Helsinki', 'Kiev'],
                          dst_offset=3, dst_start='3月最后一个周日', dst_end='10月最后一个周日'),
        
        # 美洲时区  
        'EST': TimezoneInfo('EST', 'Eastern Standard Time', -5,
                          '美国东部标准时间', 'USA', ['New York', 'Washington'],
                          dst_offset=-4, dst_start='3月第二个周日', dst_end='11月第一个周日'),
        'CST': TimezoneInfo('CST', 'Central Standard Time', -6,
                          '美国中部标准时间', 'USA', ['Chicago', 'Dallas'],
                          dst_offset=-5, dst_start='3月第二个周日', dst_end='11月第一个周日'),
        'MST': TimezoneInfo('MST', 'Mountain Standard Time', -7,
                          '美国山地标准时间', 'USA', ['Denver', 'Phoenix'],
                          dst_offset=-6, dst_start='3月第二个周日', dst_end='11月第一个周日'),
        'PST': TimezoneInfo('PST', 'Pacific Standard Time', -8,
                          '美国太平洋标准时间', 'USA', ['Los Angeles', 'San Francisco'],
                          dst_offset=-7, dst_start='3月第二个周日', dst_end='11月第一个周日'),
        
        # 大洋洲时区
        'AEST': TimezoneInfo('AEST', 'Australian Eastern Standard Time', 10,
                           '澳大利亚东部标准时间', 'Australia', ['Sydney', 'Melbourne'],
                           dst_offset=11, dst_start='10月第一个周日', dst_end='4月第一个周日'),
        'AWST': TimezoneInfo('AWST', 'Australian Western Standard Time', 8,
                           '澳大利亚西部标准时间', 'Australia', ['Perth']),
        'NZST': TimezoneInfo('NZST', 'New Zealand Standard Time', 12,
                           '新西兰标准时间', 'New Zealand', ['Auckland', 'Wellington'],
                           dst_offset=13, dst_start='9月最后一个周日', dst_end='4月第一个周日'),
    }
    
    @classmethod
    def get_timezone_info(cls, timezone_code: str) -> Optional[TimezoneInfo]:
        """获取时区信息"""
        return cls.TIMEZONE_DATA.get(timezone_code.upper())
    
    @classmethod
    def list_timezones(cls) -> List[str]:
        """列出所有支持的时区"""
        return list(cls.TIMEZONE_DATA.keys())
    
    @classmethod
    def find_timezone_by_city(cls, city: str) -> List[str]:
        """根据城市查找时区"""
        result = []
        city_lower = city.lower()
        for code, info in cls.TIMEZONE_DATA.items():
            if any(city_lower in c.lower() for c in info.cities):
                result.append(code)
        return result
    
    @classmethod
    def find_timezone_by_country(cls, country: str) -> List[str]:
        """根据国家查找时区"""
        result = []
        country_lower = country.lower()
        for code, info in cls.TIMEZONE_DATA.items():
            if country_lower in info.country.lower():
                result.append(code)
        return result
    
    @classmethod
    def convert_timezone(cls, dt: datetime.datetime, from_tz: str, to_tz: str, 
                        consider_dst: bool = True) -> datetime.datetime:
        """时区转换"""
        from_info = cls.get_timezone_info(from_tz)
        to_info = cls.get_timezone_info(to_tz)
        
        if not from_info or not to_info:
            raise ValueError(f"不支持的时区: {from_tz} 或 {to_tz}")
        
        # 计算有效偏移（考虑夏令时）
        from_offset = from_info.offset
        to_offset = to_info.offset
        
        if consider_dst:
            if cls.is_dst_active(dt, from_info):
                from_offset = from_info.dst_offset or from_info.offset
            if cls.is_dst_active(dt, to_info):
                to_offset = to_info.dst_offset or to_info.offset
        
        # 转换时间
        offset_diff = to_offset - from_offset
        return dt + datetime.timedelta(hours=offset_diff)
    
    @classmethod
    def is_dst_active(cls, dt: datetime.datetime, tz_info: TimezoneInfo) -> bool:
        """判断指定日期是否在夏令时期间"""
        if not tz_info.dst_offset or not tz_info.dst_start or not tz_info.dst_end:
            return False
        
        # 简化的夏令时判断（实际实现会更复杂）
        year = dt.year
        
        # 解析夏令时开始和结束规则
        dst_start_date = cls._parse_dst_rule(tz_info.dst_start, year)
        dst_end_date = cls._parse_dst_rule(tz_info.dst_end, year)
        
        if dst_start_date and dst_end_date:
            if dst_start_date <= dst_end_date:
                # 北半球夏令时
                return dst_start_date <= dt.date() <= dst_end_date
            else:
                # 南半球夏令时
                return dt.date() >= dst_start_date or dt.date() <= dst_end_date
        
        return False
    
    @classmethod
    def _parse_dst_rule(cls, rule: str, year: int) -> Optional[datetime.date]:
        """解析夏令时规则"""
        try:
            if '月最后一个周日' in rule:
                month = int(rule.split('月')[0])
                # 找到该月最后一个周日
                last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
                while last_day.weekday() != 6:  # 6 表示周日
                    last_day -= datetime.timedelta(days=1)
                return last_day
            elif '月第' in rule and '个周日' in rule:
                parts = rule.split('月第')
                month = int(parts[0])
                week_num = int(parts[1].split('个周日')[0])
                # 找到该月第N个周日
                first_day = datetime.date(year, month, 1)
                days_to_sunday = (6 - first_day.weekday()) % 7
                first_sunday = first_day + datetime.timedelta(days=days_to_sunday)
                target_sunday = first_sunday + datetime.timedelta(weeks=week_num - 1)
                return target_sunday
        except:
            pass
        return None
    
    @classmethod
    def get_current_offset(cls, timezone_code: str) -> float:
        """获取当前时区偏移（考虑夏令时）"""
        tz_info = cls.get_timezone_info(timezone_code)
        if not tz_info:
            raise ValueError(f"不支持的时区: {timezone_code}")
        
        now = datetime.datetime.now()
        if cls.is_dst_active(now, tz_info):
            return tz_info.dst_offset or tz_info.offset
        return tz_info.offset
    
    @classmethod
    def format_timezone_offset(cls, offset: float) -> str:
        """格式化时区偏移"""
        if offset == 0:
            return "UTC"
        elif offset > 0:
            hours = int(offset)
            minutes = int((offset - hours) * 60)
            if minutes == 0:
                return f"UTC+{hours}"
            else:
                return f"UTC+{hours}:{minutes:02d}"
        else:
            hours = int(-offset)
            minutes = int((-offset - hours) * 60)
            if minutes == 0:
                return f"UTC-{hours}"
            else:
                return f"UTC-{hours}:{minutes:02d}"
    
    @classmethod
    def get_timezone_display_info(cls, timezone_code: str) -> Dict[str, any]:
        """获取时区显示信息"""
        tz_info = cls.get_timezone_info(timezone_code)
        if not tz_info:
            raise ValueError(f"不支持的时区: {timezone_code}")
        
        current_offset = cls.get_current_offset(timezone_code)
        now = datetime.datetime.now()
        is_dst = cls.is_dst_active(now, tz_info)
        
        return {
            'code': tz_info.code,
            'name': tz_info.name,
            'description': tz_info.description,
            'country': tz_info.country,
            'cities': tz_info.cities,
            'current_offset': current_offset,
            'offset_string': cls.format_timezone_offset(current_offset),
            'is_dst_active': is_dst,
            'standard_offset': tz_info.offset,
            'dst_offset': tz_info.dst_offset
        }

# 便捷函数
def get_timezone_info(timezone_code: str) -> Optional[TimezoneInfo]:
    """获取时区信息（便捷函数）"""
    return Timezone.get_timezone_info(timezone_code)

def list_timezones() -> List[str]:
    """列出所有支持的时区（便捷函数）"""
    return Timezone.list_timezones()

def convert_timezone(dt: datetime.datetime, from_tz: str, to_tz: str) -> datetime.datetime:
    """时区转换（便捷函数）"""
    return Timezone.convert_timezone(dt, from_tz, to_tz)

def find_timezone_by_city(city: str) -> List[str]:
    """根据城市查找时区（便捷函数）"""
    return Timezone.find_timezone_by_city(city)
