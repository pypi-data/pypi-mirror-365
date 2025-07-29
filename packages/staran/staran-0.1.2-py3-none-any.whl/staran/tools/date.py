#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的Date类 - 纯Python实现
使用datetime包提供日期处理功能
"""

import datetime
import calendar
import re

class Date:
    """简化的日期类，基于Python datetime实现"""
    
    def __init__(self, *args, **kwargs):
        """
        初始化日期对象
        支持多种创建方式：
        - Date() - 今日
        - Date(year, month, day) - 指定日期
        - Date('20240615') - 从字符串
        - Date(year=2024, month=6, day=15) - 关键字参数
        """
        if not args and not kwargs:
            # 无参数 - 今日
            today = datetime.date.today()
            self.year, self.month, self.day = today.year, today.month, today.day
        elif len(args) == 1 and isinstance(args[0], str):
            # 字符串参数
            self._init_from_string(args[0])
        elif len(args) == 1 and isinstance(args[0], int):
            # 单个整数参数 - 视为时间戳
            dt = datetime.datetime.fromtimestamp(args[0])
            self.year, self.month, self.day = dt.year, dt.month, dt.day
        elif len(args) in [2, 3]:
            # 位置参数
            self._init_from_args(args)
        elif kwargs:
            # 关键字参数
            self._init_from_kwargs(kwargs)
        else:
            raise ValueError("Invalid arguments for Date initialization")
        
        # 验证日期有效性
        self._validate_date()
    
    def _init_from_string(self, date_string):
        """从字符串初始化日期"""
        # 移除所有分隔符
        clean_string = re.sub(r'[^\d]', '', date_string)
        
        if len(clean_string) == 6:  # YYYYMM
            self.year = int(clean_string[:4])
            self.month = int(clean_string[4:6])
            self.day = 1
        elif len(clean_string) == 8:  # YYYYMMDD
            self.year = int(clean_string[:4])
            self.month = int(clean_string[4:6])
            self.day = int(clean_string[6:8])
        else:
            raise ValueError(f"Date string must be 6 (YYYYMM) or 8 (YYYYMMDD) digits after removing separators, got {len(clean_string)}")
    
    def _init_from_args(self, args):
        """从位置参数初始化日期"""
        if len(args) == 2:
            self.year, self.month = args
            self.day = 1
        elif len(args) == 3:
            self.year, self.month, self.day = args
        else:
            raise ValueError("Expected 2 or 3 positional arguments")
    
    def _init_from_kwargs(self, kwargs):
        """从关键字参数初始化日期"""
        self.year = kwargs.get('year')
        self.month = kwargs.get('month')
        self.day = kwargs.get('day', 1)
        
        if self.year is None or self.month is None:
            raise ValueError("year and month are required")
    
    def _validate_date(self):
        """验证日期有效性"""
        if not isinstance(self.year, int) or self.year <= 0:
            raise ValueError(f"Year must be positive, got {self.year}")
        
        if not isinstance(self.month, int) or not (1 <= self.month <= 12):
            raise ValueError(f"Month must be between 1 and 12, got {self.month}")
        
        if not isinstance(self.day, int) or self.day <= 0:
            raise ValueError(f"Day must be positive, got {self.day}")
        
        # 检查日期是否在该月的有效范围内
        max_day = calendar.monthrange(self.year, self.month)[1]
        if self.day > max_day:
            raise ValueError(f"Day {self.day} is invalid for {self.year}-{self.month:02d}")
    
    def to_timestamp(self):
        """转换为时间戳"""
        dt = datetime.datetime.combine(
            datetime.date(self.year, self.month, self.day),
            datetime.time()
        )
        return dt.timestamp()
    
    def to_date(self):
        """转换为Python datetime.date对象"""
        return datetime.date(self.year, self.month, self.day)
    
    def to_datetime(self):
        """转换为Python datetime.datetime对象"""
        return datetime.datetime(self.year, self.month, self.day)
    
    def format(self, fmt='%Y-%m-%d'):
        """格式化日期字符串"""
        return self.to_date().strftime(fmt)
    
    def weekday(self):
        """返回星期几（0=Monday, 6=Sunday）"""
        return self.to_date().weekday()
    
    def isoweekday(self):
        """返回星期几（1=Monday, 7=Sunday）"""
        return self.to_date().isoweekday()
    
    def is_leap_year(self):
        """判断是否为闰年"""
        return calendar.isleap(self.year)
    
    def days_in_month(self):
        """返回当月天数"""
        return calendar.monthrange(self.year, self.month)[1]
    
    def days_in_year(self):
        """返回当年天数"""
        return 366 if self.is_leap_year() else 365
    
    def add_days(self, days):
        """增加天数，返回新的Date对象"""
        new_date = self.to_date() + datetime.timedelta(days=days)
        return Date(new_date.year, new_date.month, new_date.day)
    
    def add_months(self, months):
        """增加月数，返回新的Date对象"""
        new_month = self.month + months
        new_year = self.year
        
        while new_month > 12:
            new_month -= 12
            new_year += 1
        while new_month < 1:
            new_month += 12
            new_year -= 1
        
        # 处理日期溢出（如1月31日+1个月=2月28/29日）
        max_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(self.day, max_day)
        
        return Date(new_year, new_month, new_day)
    
    def difference(self, other):
        """计算与另一个日期的天数差"""
        if not isinstance(other, Date):
            raise TypeError("Expected Date object")
        
        date1 = self.to_date()
        date2 = other.to_date()
        return (date1 - date2).days
    
    def __str__(self):
        """字符串表示"""
        return f"{self.year}-{self.month:02d}-{self.day:02d}"
    
    def __repr__(self):
        """调试表示"""
        return f"Date({self.year}, {self.month}, {self.day})"
    
    def __eq__(self, other):
        """相等比较"""
        if not isinstance(other, Date):
            return False
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)
    
    def __lt__(self, other):
        """小于比较"""
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)
    
    def __le__(self, other):
        """小于等于比较"""
        return self < other or self == other
    
    def __gt__(self, other):
        """大于比较"""
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year, self.month, self.day) > (other.year, other.month, other.day)
    
    def __ge__(self, other):
        """大于等于比较"""
        return self > other or self == other
    
    def __hash__(self):
        """哈希值"""
        return hash((self.year, self.month, self.day))