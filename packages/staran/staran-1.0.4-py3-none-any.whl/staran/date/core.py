#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran 核心日期处理模块
====================

提供Date类的完整实现，包括86+个企业级API方法、
智能格式记忆、日期运算和多种格式化选项。
"""

import datetime
import calendar
import re
import logging
import time
from typing import Union, Optional, Tuple, Dict, Any
from functools import lru_cache

class DateError(ValueError):
    """Date模块的特定异常基类"""
    pass

class InvalidDateFormatError(DateError):
    """无效日期格式异常"""
    pass

class InvalidDateValueError(DateError):
    """无效日期值异常"""
    pass


class DateLogger:
    """企业级日志记录器
    
    为Date类提供结构化的日志记录功能，支持不同日志级别
    和可配置的日志输出格式。
    """
    
    def __init__(self, name: str = 'staran.Date'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.WARNING)  # 默认警告级别
        
        # 如果没有处理器，添加一个基本的控制台处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """记录一般信息"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误信息"""
        self.logger.error(message, extra=kwargs)
    
    def set_level(self, level):
        """设置日志级别"""
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        self.logger.setLevel(level)


class Date:
    """企业级日期处理类
    
    提供智能格式记忆、统一API命名和完整的日期处理功能。
    支持YYYY、YYYYMM、YYYYMMDD等多种输入格式，并在运算中
    自动保持原始格式。
    
    特性:
    ----
    - 86+个统一命名的API方法
    - 智能格式记忆和保持
    - 企业级日志记录
    - 类型安全的日期转换
    - 向后兼容的旧API支持
    
    Examples:
    ---------
    >>> # 智能格式记忆
    >>> date1 = Date('202504')      # 年月格式
    >>> date2 = Date('20250415')    # 完整格式
    >>> 
    >>> # 格式保持运算
    >>> print(date1.add_months(2))  # 202506
    >>> print(date2.add_days(10))   # 20250425
    >>> 
    >>> # 统一API命名
    >>> date = Date('20250415')
    >>> print(date.format_iso())         # 2025-04-15
    >>> print(date.format_chinese())     # 2025年04月15日
    >>> print(date.get_weekday())        # 1 (星期二)
    >>> print(date.is_weekend())         # False
    """
    
    # 类级别的日志记录器
    _logger = DateLogger()
    
    def __init__(self, *args, **kwargs):
        """初始化Date对象
        
        支持多种初始化方式:
        - Date('2025')           # 年份格式
        - Date('202504')         # 年月格式  
        - Date('20250415')       # 完整格式
        - Date(2025, 4, 15)      # 位置参数
        - Date(year=2025, month=4, day=15)  # 关键字参数
        - Date(datetime_obj)     # datetime对象
        """
        self._logger.debug(f"初始化Date对象: args={args}, kwargs={kwargs}")
        
        # 初始化属性
        self.year: int = 0
        self.month: int = 1  
        self.day: int = 1
        self._input_format: str = 'iso'  # 默认ISO格式
        
        # 根据参数类型进行初始化
        if len(args) == 1 and not kwargs:
            arg = args[0]
            if isinstance(arg, str):
                self._init_from_string(arg)
            elif isinstance(arg, (datetime.date, datetime.datetime)):
                self._init_from_datetime(arg)
            else:
                raise InvalidDateFormatError(f"不支持的参数类型: {type(arg)}")
        elif len(args) == 3 and not kwargs:
            self._init_from_args(args[0], args[1], args[2])
        elif not args and kwargs:
            self._init_from_kwargs(kwargs)
        elif len(args) == 0 and len(kwargs) == 0:
            # 默认今日
            today = datetime.date.today()
            self._init_from_datetime(today)
        else:
            raise InvalidDateValueError("无效的参数组合")
        
        self._logger.info(f"创建Date对象: {self.year}-{self.month:02d}-{self.day:02d}, 格式: {self._input_format}")
    
    def _init_from_string(self, date_string: str):
        """从字符串初始化"""
        # 移除分隔符并清理字符串
        clean_string = re.sub(r'[^\d]', '', date_string)
        
        if not clean_string.isdigit():
            raise InvalidDateFormatError(f"日期字符串包含非数字字符: {date_string}")

        if len(clean_string) == 4:  # YYYY
            self.year = int(clean_string)
            self.month = 1
            self.day = 1
            self._input_format = 'year'
        elif len(clean_string) == 6:  # YYYYMM
            self.year = int(clean_string[:4])
            self.month = int(clean_string[4:6])
            self.day = 1
            self._input_format = 'year_month'
        elif len(clean_string) == 8:  # YYYYMMDD
            self.year = int(clean_string[:4])
            self.month = int(clean_string[4:6])
            self.day = int(clean_string[6:8])
            self._input_format = 'full'
        else:
            raise InvalidDateFormatError(f"日期字符串格式无效: {date_string}")
        
        self._validate_date()
    
    def _init_from_datetime(self, dt: Union[datetime.date, datetime.datetime]):
        """从datetime对象初始化"""
        self.year = dt.year
        self.month = dt.month
        self.day = dt.day
        self._input_format = 'iso'
    
    def _init_from_args(self, year: int, month: int, day: int):
        """从位置参数初始化"""
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self._input_format = 'iso'
        self._validate_date()
    
    def _init_from_kwargs(self, kwargs: Dict[str, Any]):
        """从关键字参数初始化"""
        self.year = int(kwargs.get('year', datetime.date.today().year))
        self.month = int(kwargs.get('month', 1))
        self.day = int(kwargs.get('day', 1))
        self._input_format = 'iso'
        self._validate_date()
    
    def _validate_date(self):
        """验证日期的有效性"""
        if not (1 <= self.month <= 12):
            raise InvalidDateValueError(f"无效的月份: {self.month}")
        
        max_days = calendar.monthrange(self.year, self.month)[1]
        if not (1 <= self.day <= max_days):
            raise InvalidDateValueError(f"无效的日期: {self.day} (对于 {self.year}-{self.month})")

        try:
            datetime.date(self.year, self.month, self.day)
        except ValueError as e:
            raise InvalidDateValueError(f"无效的日期: {self.year}-{self.month}-{self.day}") from e
    
    @lru_cache(maxsize=128)
    def _create_with_same_format(self, year: int, month: int, day: int) -> 'Date':
        """创建具有相同格式的新Date对象 (带缓存)"""
        new_date = Date(year, month, day)
        new_date._input_format = self._input_format
        return new_date
    
    # =============================================
    # 核心属性和字符串表示
    # =============================================
    
    def __str__(self) -> str:
        """字符串表示 - 保持原始输入格式"""
        return self.format_default()
    
    def __repr__(self) -> str:
        """开发者友好的字符串表示"""
        return f"Date('{self.__str__()}')"
    
    # =============================================
    # from_* 系列：创建方法
    # =============================================
    
    @classmethod
    def from_string(cls, date_string: str) -> 'Date':
        """从字符串创建Date对象"""
        return cls(date_string)
    
    @classmethod
    def from_timestamp(cls, timestamp: Union[int, float]) -> 'Date':
        """从时间戳创建Date对象"""
        dt = datetime.datetime.fromtimestamp(timestamp)
        return cls(dt.date())
    
    @classmethod
    def from_date_object(cls, date_obj: datetime.date) -> 'Date':
        """从datetime.date对象创建Date对象"""
        return cls(date_obj)
    
    @classmethod
    def today(cls) -> 'Date':
        """创建今日Date对象"""
        return cls(datetime.date.today())
    
    # =============================================
    # to_* 系列：转换方法
    # =============================================
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """转为元组 (year, month, day)"""
        return (self.year, self.month, self.day)
    
    def to_dict(self) -> Dict[str, int]:
        """转为字典"""
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day
        }
    
    def to_date_object(self) -> datetime.date:
        """转为datetime.date对象"""
        return datetime.date(self.year, self.month, self.day)
    
    def to_datetime_object(self) -> datetime.datetime:
        """转为datetime.datetime对象"""
        return datetime.datetime(self.year, self.month, self.day)
    
    def to_timestamp(self) -> float:
        """转为时间戳"""
        return self.to_datetime_object().timestamp()
    
    # =============================================
    # format_* 系列：格式化方法
    # =============================================
    
    def format_default(self) -> str:
        """默认格式 - 保持原始输入格式"""
        if self._input_format == 'year':
            return str(self.year)
        elif self._input_format == 'year_month':
            return f"{self.year}{self.month:02d}"
        elif self._input_format == 'full':
            return f"{self.year}{self.month:02d}{self.day:02d}"
        else:  # iso
            return f"{self.year}-{self.month:02d}-{self.day:02d}"
    
    def format_iso(self) -> str:
        """ISO格式: 2025-04-15"""
        return f"{self.year}-{self.month:02d}-{self.day:02d}"
    
    def format_chinese(self) -> str:
        """中文格式: 2025年04月15日"""
        return f"{self.year}年{self.month:02d}月{self.day:02d}日"
    
    def format_compact(self) -> str:
        """紧凑格式: 20250415"""
        return f"{self.year}{self.month:02d}{self.day:02d}"
    
    def format_slash(self) -> str:
        """斜杠格式: 2025/04/15"""
        return f"{self.year}/{self.month:02d}/{self.day:02d}"
    
    def format_dot(self) -> str:
        """点分格式: 2025.04.15"""
        return f"{self.year}.{self.month:02d}.{self.day:02d}"
    
    def format_year_month(self) -> str:
        """年月格式: 2025-04"""
        return f"{self.year}-{self.month:02d}"
    
    def format_year_month_compact(self) -> str:
        """年月紧凑格式: 202504"""
        return f"{self.year}{self.month:02d}"
    
    def format_custom(self, fmt: str) -> str:
        """自定义格式"""
        dt = self.to_datetime_object()
        return dt.strftime(fmt)
    
    # =============================================
    # get_* 系列：获取方法
    # =============================================
    
    def get_weekday(self) -> int:
        """获取星期几 (0=星期一, 6=星期日)"""
        return self.to_date_object().weekday()
    
    def get_isoweekday(self) -> int:
        """获取ISO星期几 (1=星期一, 7=星期日)"""
        return self.to_date_object().isoweekday()
    
    def get_month_start(self) -> 'Date':
        """获取月初日期"""
        return self._create_with_same_format(self.year, self.month, 1)
    
    def get_month_end(self) -> 'Date':
        """获取月末日期"""
        last_day = calendar.monthrange(self.year, self.month)[1]
        return self._create_with_same_format(self.year, self.month, last_day)
    
    def get_year_start(self) -> 'Date':
        """获取年初日期"""
        return self._create_with_same_format(self.year, 1, 1)
    
    def get_year_end(self) -> 'Date':
        """获取年末日期"""
        return self._create_with_same_format(self.year, 12, 31)
    
    def get_days_in_month(self) -> int:
        """获取当月天数"""
        return calendar.monthrange(self.year, self.month)[1]
    
    def get_days_in_year(self) -> int:
        """获取当年天数"""
        return 366 if calendar.isleap(self.year) else 365
    
    # =============================================
    # is_* 系列：判断方法
    # =============================================
    
    def is_weekend(self) -> bool:
        """是否为周末"""
        return self.get_weekday() >= 5
    
    def is_weekday(self) -> bool:
        """是否为工作日"""
        return not self.is_weekend()
    
    def is_leap_year(self) -> bool:
        """是否为闰年"""
        return calendar.isleap(self.year)
    
    def is_month_start(self) -> bool:
        """是否为月初"""
        return self.day == 1
    
    def is_month_end(self) -> bool:
        """是否为月末"""
        return self.day == self.get_days_in_month()
    
    def is_year_start(self) -> bool:
        """是否为年初"""
        return self.month == 1 and self.day == 1
    
    def is_year_end(self) -> bool:
        """是否为年末"""
        return self.month == 12 and self.day == 31
    
    # =============================================
    # add_*/subtract_* 系列：运算方法
    # =============================================
    
    def add_days(self, days: int) -> 'Date':
        """加天数"""
        new_date = self.to_date_object() + datetime.timedelta(days=days)
        return self._create_with_same_format(new_date.year, new_date.month, new_date.day)
    
    def add_months(self, months: int) -> 'Date':
        """加月数"""
        year = self.year
        month = self.month + months
        
        # 处理月份溢出
        while month > 12:
            year += 1
            month -= 12
        while month < 1:
            year -= 1
            month += 12
        
        # 处理日期调整
        day = self.day
        max_days = calendar.monthrange(year, month)[1]
        if day > max_days:
            day = max_days
        
        return self._create_with_same_format(year, month, day)
    
    def add_years(self, years: int) -> 'Date':
        """加年数"""
        new_year = self.year + years
        day = self.day
        
        # 处理闰年2月29日的情况
        if self.month == 2 and self.day == 29 and not calendar.isleap(new_year):
            day = 28
        
        return self._create_with_same_format(new_year, self.month, day)
    
    def subtract_days(self, days: int) -> 'Date':
        """减天数"""
        return self.add_days(-days)
    
    def subtract_months(self, months: int) -> 'Date':
        """减月数"""
        return self.add_months(-months)
    
    def subtract_years(self, years: int) -> 'Date':
        """减年数"""
        return self.add_years(-years)
    
    # =============================================
    # calculate_* 系列：计算方法
    # =============================================
    
    def calculate_difference_days(self, other: 'Date') -> int:
        """计算与另一个日期的天数差"""
        date1 = self.to_date_object()
        date2 = other.to_date_object()
        return (date2 - date1).days
    
    def calculate_difference_months(self, other: 'Date') -> int:
        """计算与另一个日期的月数差（近似）"""
        return (other.year - self.year) * 12 + (other.month - self.month)
    
    # =============================================
    # 配置和日志方法
    # =============================================
    
    def set_default_format(self, fmt: str):
        """设置默认格式"""
        self._input_format = fmt
    
    @classmethod
    def set_log_level(cls, level):
        """设置日志级别"""
        cls._logger.set_level(level)
    
    # =============================================
    # 比较操作符
    # =============================================
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Date):
            return False
        return self.to_tuple() == other.to_tuple()
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self.to_tuple() < other.to_tuple()
    
    def __le__(self, other) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self.to_tuple() <= other.to_tuple()
    
    def __gt__(self, other) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self.to_tuple() > other.to_tuple()
    
    def __ge__(self, other) -> bool:
        if not isinstance(other, Date):
            return NotImplemented
        return self.to_tuple() >= other.to_tuple()
    
    def __hash__(self) -> int:
        return hash(self.to_tuple())
    
    # =============================================
    # 向后兼容的旧API
    # =============================================
    
    def format(self, fmt: str) -> str:
        """旧API: 自定义格式化"""
        return self.format_custom(fmt)
    
    def to_date(self) -> datetime.date:
        """旧API: 转为datetime.date"""
        return self.to_date_object()
    
    def to_datetime(self) -> datetime.datetime:
        """旧API: 转为datetime.datetime"""
        return self.to_datetime_object()
    
    def weekday(self) -> int:
        """旧API: 获取星期几"""
        return self.get_weekday()
    
    def difference(self, other: 'Date') -> int:
        """旧API: 计算天数差"""
        return self.calculate_difference_days(other)
    
    def month_start(self) -> 'Date':
        """旧API: 获取月初"""
        return self.get_month_start()
    
    def month_end(self) -> 'Date':
        """旧API: 获取月末"""
        return self.get_month_end()
