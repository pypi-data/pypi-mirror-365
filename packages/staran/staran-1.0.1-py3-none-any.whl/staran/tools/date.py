#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran Date类 - 企业级日期处理工具
支持智能格式记忆、日志记录和一致的API设计
"""

import datetime
import calendar
import re
import logging
from typing import Union, Tuple, Dict, Optional, Any

class Date:
    """
    企业级日期处理类，支持：
    - 多种输入格式自动识别
    - 智能格式记忆
    - 统一的API命名规范
    - 企业级日志记录
    - 向后兼容性
    """
    
    def __init__(self, *args, **kwargs):
        """初始化Date对象"""
        # 初始化属性
        self.year: int = 0
        self.month: int = 0
        self.day: int = 0
        self._input_format_type: str = 'unknown'
        
        # 简化的初始化逻辑
        if not args and not kwargs:
            # 无参数 - 今天
            today = datetime.date.today()
            self.year, self.month, self.day = today.year, today.month, today.day
            self._input_format_type = 'today'
        elif len(args) == 1:
            # 单个参数
            self._handle_single_arg(args[0])
        elif len(args) == 3:
            # 三个参数
            self.year, self.month, self.day = args
            self._input_format_type = 'full'
            self._validate_date()
        elif 'year' in kwargs and 'month' in kwargs and 'day' in kwargs:
            self.year = kwargs['year']
            self.month = kwargs['month'] 
            self.day = kwargs['day']
            self._input_format_type = 'full'
            self._validate_date()
        else:
            raise ValueError("Invalid arguments for Date initialization")
    
    def _validate_date(self):
        """验证日期有效性"""
        if not (1 <= self.month <= 12):
            raise ValueError(f"Month must be between 1 and 12, got {self.month}")
        
        try:
            # 使用datetime来验证日期的有效性
            datetime.date(self.year, self.month, self.day)
        except ValueError as e:
            if self.month == 2 and self.day == 29:
                raise ValueError(f"Day 29 is invalid for {self.year}-02")
            elif self.day > calendar.monthrange(self.year, self.month)[1]:
                raise ValueError(f"Day {self.day} is invalid for {self.year}-{self.month:02d}")
            else:
                raise ValueError(f"Invalid date: {self.year}-{self.month:02d}-{self.day:02d}")
    
    def _handle_single_arg(self, arg):
        """处理单个参数的初始化"""
        if isinstance(arg, str):
            self._init_from_string(arg)
        elif isinstance(arg, datetime.datetime):  # 先检查datetime，因为datetime是date的子类
            self.year, self.month, self.day = arg.year, arg.month, arg.day
            self._input_format_type = 'datetime_object'
        elif isinstance(arg, datetime.date):
            self.year, self.month, self.day = arg.year, arg.month, arg.day
            self._input_format_type = 'date_object'
        elif isinstance(arg, (int, float)):  # 支持int和float时间戳
            dt = datetime.datetime.fromtimestamp(arg)
            self.year, self.month, self.day = dt.year, dt.month, dt.day
            self._input_format_type = 'timestamp'
        else:
            raise TypeError(f"Unsupported argument type: {type(arg)}")
    
    def _init_from_string(self, date_string: str):
        """从字符串初始化"""
        clean_string = re.sub(r'[^\d]', '', date_string.strip())
        
        if not clean_string:
            raise ValueError(f"Date string must be 4 (YYYY), 6 (YYYYMM) or 8 (YYYYMMDD) digits after removing separators, got 0 digits: '{clean_string}'")
        
        length = len(clean_string)
        
        if length == 8:
            year_str, month_str, day_str = clean_string[:4], clean_string[4:6], clean_string[6:8]
            self.year, self.month, self.day = int(year_str), int(month_str), int(day_str)
            self._input_format_type = 'full'
        elif length == 6:
            year_str, month_str = clean_string[:4], clean_string[4:6]
            self.year, self.month, self.day = int(year_str), int(month_str), 1
            self._input_format_type = 'year_month'
        elif length == 4:
            self.year, self.month, self.day = int(clean_string), 1, 1
            self._input_format_type = 'year_only'
        else:
            raise ValueError(f"Date string must be 4 (YYYY), 6 (YYYYMM) or 8 (YYYYMMDD) digits after removing separators, got {length} digits: '{clean_string}'")
    
    def __str__(self) -> str:
        """返回默认字符串表示"""
        if self._input_format_type == 'year_only':
            return f"{self.year:04d}"
        elif self._input_format_type == 'year_month':
            return f"{self.year:04d}{self.month:02d}"
        else:
            return f"{self.year:04d}{self.month:02d}{self.day:02d}"
    
    # 类方法
    @classmethod
    def from_string(cls, date_string: str) -> 'Date':
        return cls(date_string)
    
    @classmethod
    def from_timestamp(cls, timestamp: Union[int, float]) -> 'Date':
        return cls(timestamp)
    
    @classmethod
    def from_date_object(cls, date_obj: datetime.date) -> 'Date':
        return cls(date_obj)
    
    @classmethod
    def from_datetime_object(cls, datetime_obj: datetime.datetime) -> 'Date':
        return cls(datetime_obj)
    
    @classmethod
    def today(cls) -> 'Date':
        return cls()
    
    # 转换方法
    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.year, self.month, self.day)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'format_type': self._input_format_type
        }
    
    def to_date_object(self) -> datetime.date:
        return datetime.date(self.year, self.month, self.day)
    
    def to_datetime_object(self) -> datetime.datetime:
        return datetime.datetime(self.year, self.month, self.day)
    
    def to_timestamp(self) -> float:
        return self.to_datetime_object().timestamp()
    
    # 格式化方法
    def format_default(self) -> str:
        return str(self)
    
    def format_iso(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
    
    def format_chinese(self) -> str:
        return f"{self.year:04d}年{self.month:02d}月{self.day:02d}日"
    
    def format_compact(self) -> str:
        return f"{self.year:04d}{self.month:02d}{self.day:02d}"
    
    def format_slash(self) -> str:
        return f"{self.year:04d}/{self.month:02d}/{self.day:02d}"
    
    def format_dot(self) -> str:
        return f"{self.year:04d}.{self.month:02d}.{self.day:02d}"
    
    def format_custom(self, format_string: str) -> str:
        return self.to_date_object().strftime(format_string)
    
    def format_year_month(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"
    
    def format_year_month_compact(self) -> str:
        return f"{self.year:04d}{self.month:02d}"
    
    # 获取方法
    def get_weekday(self) -> int:
        return self.to_date_object().weekday()
    
    def get_isoweekday(self) -> int:
        return self.to_date_object().isoweekday()
    
    def get_days_in_month(self) -> int:
        return calendar.monthrange(self.year, self.month)[1]
    
    def get_days_in_year(self) -> int:
        return 366 if calendar.isleap(self.year) else 365
    
    def get_format_type(self) -> str:
        return self._input_format_type
    
    def get_month_start(self) -> 'Date':
        return Date(self.year, self.month, 1)
    
    def get_month_end(self) -> 'Date':
        last_day = self.get_days_in_month()
        return Date(self.year, self.month, last_day)
    
    def get_year_start(self) -> 'Date':
        return Date(self.year, 1, 1)
    
    def get_year_end(self) -> 'Date':
        return Date(self.year, 12, 31)
    
    # 判断方法
    def is_weekend(self) -> bool:
        return self.get_weekday() >= 5
    
    def is_weekday(self) -> bool:
        return not self.is_weekend()
    
    def is_leap_year(self) -> bool:
        return calendar.isleap(self.year)
    
    def is_month_start(self) -> bool:
        return self.day == 1
    
    def is_month_end(self) -> bool:
        return self.day == self.get_days_in_month()
    
    def is_year_start(self) -> bool:
        return self.month == 1 and self.day == 1
    
    def is_year_end(self) -> bool:
        return self.month == 12 and self.day == 31
    
    # 运算方法
    def add_days(self, days: int) -> 'Date':
        new_date = self.to_date_object() + datetime.timedelta(days=days)
        return self._create_with_same_format(new_date.year, new_date.month, new_date.day)
    
    def add_months(self, months: int) -> 'Date':
        new_month = self.month + months
        new_year = self.year
        
        while new_month > 12:
            new_month -= 12
            new_year += 1
        while new_month < 1:
            new_month += 12
            new_year -= 1
        
        max_day = calendar.monthrange(new_year, new_month)[1]
        new_day = min(self.day, max_day)
        
        return self._create_with_same_format(new_year, new_month, new_day)
    
    def add_years(self, years: int) -> 'Date':
        new_year = self.year + years
        new_day = self.day
        if self.month == 2 and self.day == 29 and not calendar.isleap(new_year):
            new_day = 28
        
        return self._create_with_same_format(new_year, self.month, new_day)
    
    def subtract_days(self, days: int) -> 'Date':
        return self.add_days(-days)
    
    def subtract_months(self, months: int) -> 'Date':
        return self.add_months(-months)
    
    def subtract_years(self, years: int) -> 'Date':
        return self.add_years(-years)
    
    def _create_with_same_format(self, year: int, month: int, day: int) -> 'Date':
        """创建保持相同格式的新Date对象"""
        if self._input_format_type == 'year_only':
            return Date(f"{year:04d}")
        elif self._input_format_type == 'year_month':
            return Date(f"{year:04d}{month:02d}")
        else:
            return Date(year, month, day)
    
    # 计算方法
    def calculate_difference_days(self, other: 'Date') -> int:
        return (self.to_date_object() - other.to_date_object()).days
    
    def calculate_difference_months(self, other: 'Date') -> int:
        return (self.year - other.year) * 12 + (self.month - other.month)
    
    # 比较操作
    def __eq__(self, other) -> bool:
        if not isinstance(other, Date):
            return False
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)
    
    def __le__(self, other) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year, self.month, self.day) <= (other.year, other.month, other.day)
    
    def __gt__(self, other) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year, self.month, self.day) > (other.year, other.month, other.day)
    
    def __ge__(self, other) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year, self.month, self.day) >= (other.year, other.month, other.day)
    
    def __hash__(self) -> int:
        return hash((self.year, self.month, self.day))
    
    # 向后兼容性方法
    def format(self, format_string: str = None) -> str:
        if format_string is None:
            return str(self)
        return self.format_custom(format_string)
    
    def to_date(self) -> datetime.date:
        return self.to_date_object()
    
    def to_datetime(self) -> datetime.datetime:
        return self.to_datetime_object()
    
    def weekday(self) -> int:
        return self.get_weekday()
    
    def difference(self, other: 'Date') -> int:
        return self.calculate_difference_days(other)
    
    def start_of_month(self) -> 'Date':
        return self.get_month_start()
    
    def end_of_month(self) -> 'Date':
        return self.get_month_end()
    
    def start_of_year(self) -> 'Date':
        return self.get_year_start()
    
    def end_of_year(self) -> 'Date':
        return self.get_year_end()
    
    def days_in_month(self) -> int:
        return self.get_days_in_month()
    
    def is_leap(self) -> bool:
        return self.is_leap_year()
    
    def add(self, **kwargs) -> 'Date':
        """向后兼容的add方法"""
        result = self
        if 'days' in kwargs:
            result = result.add_days(kwargs['days'])
        if 'months' in kwargs:
            result = result.add_months(kwargs['months'])
        if 'years' in kwargs:
            result = result.add_years(kwargs['years'])
        return result
    
    def subtract(self, **kwargs) -> 'Date':
        """向后兼容的subtract方法"""
        result = self
        if 'days' in kwargs:
            result = result.subtract_days(kwargs['days'])
        if 'months' in kwargs:
            result = result.subtract_months(kwargs['months'])
        if 'years' in kwargs:
            result = result.subtract_years(kwargs['years'])
        return result
    
    def convert_format(self, format_type: str) -> str:
        """向后兼容的格式转换方法"""
        format_mapping = {
            'iso': self.format_iso,
            'chinese': self.format_chinese,
            'compact': self.format_compact,
            'slash': self.format_slash,
            'dot': self.format_dot
        }
        
        if format_type in format_mapping:
            return format_mapping[format_type]()
        else:
            return str(self)
    
    # 类级别工具方法
    @classmethod
    def set_log_level(cls, level: int):
        pass  # 简化版本不实现日志
    
    @classmethod
    def get_version(cls) -> str:
        return "1.0.1"
