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
from typing import Union, Optional, Tuple, Dict, Any, List
from functools import lru_cache

# 导入农历和多语言模块
from .lunar import LunarDate
from .i18n import Language

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
    
    v1.0.8 新增功能:
    - 农历日期支持 (from_lunar, to_lunar, format_lunar等)
    - 多语言配置 (中简、中繁、日、英四种语言)
    - 全局语言设置，一次配置全局生效
    
    特性:
    ----
    - 120+个统一命名的API方法
    - 智能格式记忆和保持
    - 企业级日志记录
    - 农历与公历互转
    - 多语言本地化支持
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
    >>> # 农历支持 (v1.0.8)
    >>> lunar_date = Date.from_lunar(2025, 3, 15)  # 农历2025年三月十五
    >>> print(lunar_date.to_lunar().format_chinese())  # 农历2025年三月十五
    >>> 
    >>> # 多语言支持 (v1.0.8)
    >>> Date.set_language('en_US')  # 设置全局语言为英语
    >>> print(date2.format_localized())  # 04/15/2025
    >>> print(date2.format_weekday_localized())  # Tuesday
    >>> # 统一API命名
    >>> date = Date('20250415')
    >>> print(date.format_iso())         # 2025-04-15
    >>> print(date.format_chinese())     # 2025年04月15日
    >>> print(date.get_weekday())        # 1 (星期二)
    >>> print(date.is_weekend())         # False
    
    Raises:
    -------
    InvalidDateFormatError
        当输入的日期格式无效时抛出
    InvalidDateValueError
        当日期值超出有效范围时抛出
    """
    
    __slots__ = ('year', 'month', 'day', '_input_format')
    
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
        # 基本范围检查
        if not (1 <= self.month <= 12):
            raise InvalidDateValueError(f"无效的月份: {self.month}")
        
        # 年份合理性检查
        if not (1900 <= self.year <= 3000):
            self._logger.warning(f"年份 {self.year} 超出常规范围 (1900-3000)")
        
        max_days = calendar.monthrange(self.year, self.month)[1]
        if not (1 <= self.day <= max_days):
            raise InvalidDateValueError(f"无效的日期: {self.day} (对于 {self.year}-{self.month})")

        try:
            datetime.date(self.year, self.month, self.day)
        except ValueError as e:
            raise InvalidDateValueError(f"无效的日期: {self.year}-{self.month}-{self.day}") from e
        
        # 特殊日期检查
        self._check_special_dates()
    
    def _check_special_dates(self):
        """检查特殊日期"""
        # 检查是否为闰年2月29日
        if self.month == 2 and self.day == 29 and not calendar.isleap(self.year):
            raise InvalidDateValueError(f"非闰年 {self.year} 不存在2月29日")
            
        # 检查历史边界日期
        if self.year < 1582 and self.month == 10 and 5 <= self.day <= 14:
            self._logger.warning("日期位于格里高利历改革期间 (1582年10月5-14日)")
            
    @classmethod
    def is_valid_date_string(cls, date_string: str) -> bool:
        """检查日期字符串是否有效
        
        Args:
            date_string: 日期字符串
            
        Returns:
            是否为有效日期字符串
        """
        try:
            cls(date_string)
            return True
        except (InvalidDateFormatError, InvalidDateValueError):
            return False
    
    @lru_cache(maxsize=128)
    def _create_with_same_format(self, year: int, month: int, day: int) -> 'Date':
        """创建具有相同格式的新Date对象"""
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
    def from_timestamp(cls, timestamp: Union[int, float], timezone_offset: int = 0) -> 'Date':
        """从时间戳创建Date对象
        
        Args:
            timestamp: Unix时间戳
            timezone_offset: 时区偏移小时数 (如 +8 表示东八区)
        """
        dt = datetime.datetime.fromtimestamp(timestamp)
        # 调整时区
        if timezone_offset != 0:
            dt = dt + datetime.timedelta(hours=timezone_offset)
        return cls(dt.date())
    
    @classmethod
    def from_date_object(cls, date_obj: datetime.date) -> 'Date':
        """从datetime.date对象创建Date对象"""
        return cls(date_obj)
    
    @classmethod
    def today(cls) -> 'Date':
        """创建今日Date对象"""
        return cls(datetime.date.today())
    
    @classmethod
    def from_lunar(cls, year: int, month: int, day: int, is_leap: bool = False) -> 'Date':
        """从农历日期创建Date对象 (v1.0.8)
        
        Args:
            year: 农历年份
            month: 农历月份
            day: 农历日期
            is_leap: 是否闰月
            
        Returns:
            对应的公历Date对象
            
        Example:
            >>> date = Date.from_lunar(2025, 3, 15)  # 农历2025年三月十五
        """
        lunar_date = LunarDate(year, month, day, is_leap)
        solar_date = lunar_date.to_solar()
        return cls(solar_date)
    
    @classmethod
    def from_lunar_string(cls, lunar_string: str) -> 'Date':
        """从农历字符串创建Date对象 (v1.0.8)
        
        支持格式:
        - "20250315" (农历2025年3月15日)
        - "2025闰0315" (农历2025年闰3月15日)
        
        Args:
            lunar_string: 农历日期字符串
            
        Returns:
            对应的公历Date对象
        """
        # 解析闰月标记
        is_leap = '闰' in lunar_string
        clean_string = lunar_string.replace('闰', '')
        
        if len(clean_string) != 8:
            raise InvalidDateFormatError(f"农历日期字符串格式无效: {lunar_string}")
        
        year = int(clean_string[:4])
        month = int(clean_string[4:6])
        day = int(clean_string[6:8])
        
        return cls.from_lunar(year, month, day, is_leap)
    
    @classmethod
    def set_language(cls, language_code: str) -> None:
        """设置全局语言 (v1.0.8)
        
        一次设置，全局生效。支持中简、中繁、日、英四种语言。
        
        Args:
            language_code: 语言代码
                - 'zh_CN': 中文简体
                - 'zh_TW': 中文繁体  
                - 'ja_JP': 日语
                - 'en_US': 英语
                
        Example:
            >>> Date.set_language('en_US')  # 设置为英语
            >>> Date.set_language('zh_TW')  # 设置为繁体中文
        """
        Language.set_global_language(language_code)
        cls._logger.info(f"全局语言已设置为: {language_code}")
    
    @classmethod
    def get_language(cls) -> str:
        """获取当前全局语言设置 (v1.0.8)"""
        return Language.get_global_language()
    
    @classmethod
    def get_supported_languages(cls) -> Dict[str, str]:
        """获取支持的语言列表 (v1.0.8)"""
        return Language.get_supported_languages()
    
    @classmethod
    def date_range(cls, start: Union[str, 'Date'], end: Union[str, 'Date'], 
                   step: int = 1) -> List['Date']:
        """生成日期范围
        
        Args:
            start: 开始日期
            end: 结束日期
            step: 步长（天数）
            
        Returns:
            日期列表
        """
        if isinstance(start, str):
            start = cls.from_string(start)
        if isinstance(end, str):
            end = cls.from_string(end)
            
        dates = []
        current = start
        while current <= end:
            dates.append(current)
            current = current.add_days(step)
        return dates
    
    @classmethod
    def business_days(cls, start: Union[str, 'Date'], end: Union[str, 'Date']) -> List['Date']:
        """生成工作日列表"""
        dates = cls.date_range(start, end)
        return [date for date in dates if date.is_business_day()]
    
    @classmethod
    def weekends(cls, start: Union[str, 'Date'], end: Union[str, 'Date']) -> List['Date']:
        """生成周末日期列表"""
        dates = cls.date_range(start, end)
        return [date for date in dates if date.is_weekend()]
    
    @classmethod
    def month_range(cls, start_year_month: Union[str, 'Date'], months: int) -> List['Date']:
        """生成月份范围
        
        Args:
            start_year_month: 开始年月 (如 "202501" 或 Date对象)
            months: 月份数量
            
        Returns:
            月份第一天的日期列表
            
        Example:
            Date.month_range("202501", 3)  # [202501, 202502, 202503]
        """
        if isinstance(start_year_month, str):
            start_date = cls.from_string(start_year_month)
        else:
            start_date = start_year_month
            
        # 确保是月初
        start_date = start_date.get_month_start()
        
        result = []
        current = start_date
        for _ in range(months):
            result.append(current)
            current = current.add_months(1)
        
        return result
    
    @classmethod 
    def quarter_dates(cls, year: int) -> Dict[int, Tuple['Date', 'Date']]:
        """获取指定年份的季度起止日期
        
        Args:
            year: 年份
            
        Returns:
            季度字典 {1: (Q1开始, Q1结束), 2: (Q2开始, Q2结束), ...}
        """
        quarters = {}
        for quarter in range(1, 5):
            start_month = (quarter - 1) * 3 + 1
            end_month = quarter * 3
            
            start_date = cls(year, start_month, 1)
            end_date = cls(year, end_month, 1).get_month_end()
            
            quarters[quarter] = (start_date, end_date)
            
        return quarters
    
    # =============================================
    # to_* 系列：转换方法
    # =============================================
    
    def to_tuple(self) -> Tuple[int, int, int]:
        """转为元组 (year, month, day)"""
        return (self.year, self.month, self.day)
    
    def to_date_object(self) -> datetime.date:
        """转为datetime.date对象"""
        return datetime.date(self.year, self.month, self.day)
    
    def to_datetime_object(self) -> datetime.datetime:
        """转为datetime.datetime对象"""
        return datetime.datetime(self.year, self.month, self.day)
    
    def to_timestamp(self, timezone_offset: int = 0) -> float:
        """转为时间戳
        
        Args:
            timezone_offset: 时区偏移小时数 (如 +8 表示东八区)
            
        Returns:
            Unix时间戳
        """
        dt = self.to_datetime_object()
        # 调整时区
        if timezone_offset != 0:
            dt = dt - datetime.timedelta(hours=timezone_offset)
        return dt.timestamp()
    
    def to_lunar(self) -> LunarDate:
        """转为农历日期对象 (v1.0.8)
        
        Returns:
            对应的农历日期对象
            
        Example:
            >>> date = Date('20250415')
            >>> lunar = date.to_lunar()
            >>> print(lunar.format_chinese())  # 农历2025年三月十八
        """
        return LunarDate.from_solar(self.to_date_object())
    
    def to_lunar_string(self, compact: bool = True) -> str:
        """转为农历字符串 (v1.0.8)
        
        Args:
            compact: 是否使用紧凑格式
            
        Returns:
            农历日期字符串
            
        Example:
            >>> date = Date('20250415')
            >>> print(date.to_lunar_string())  # 20250318
            >>> print(date.to_lunar_string(False))  # 农历2025年三月十八
        """
        lunar = self.to_lunar()
        return lunar.format_compact() if compact else lunar.format_chinese()
    
    def to_json(self, include_metadata: bool = True) -> str:
        """转为JSON字符串
        
        Args:
            include_metadata: 是否包含元数据（格式、版本等）
            
        Returns:
            JSON字符串
        """
        import json
        
        data = {
            'date': self.format_iso(),
            'year': self.year,
            'month': self.month,
            'day': self.day
        }
        
        if include_metadata:
            data.update({
                'format': self._input_format,
                'weekday': self.get_weekday(),
                'is_weekend': self.is_weekend(),
                'quarter': self.get_quarter(),
                'version': '1.0.7'
            })
        
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Date':
        """从JSON字符串创建Date对象
        
        Args:
            json_str: JSON字符串
            
        Returns:
            Date对象
            
        Raises:
            ValueError: JSON格式错误或缺少必要字段
        """
        import json
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的JSON格式: {e}")
        
        # 检查必要字段
        required_fields = ['year', 'month', 'day']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"JSON缺少必要字段: {missing_fields}")
        
        try:
            date = cls(data['year'], data['month'], data['day'])
            date._input_format = data.get('format', 'iso')
            return date
        except (InvalidDateFormatError, InvalidDateValueError) as e:
            raise ValueError(f"JSON中的日期数据无效: {e}")
    
    def to_dict(self, include_metadata: bool = False) -> Dict[str, Any]:
        """转为字典
        
        Args:
            include_metadata: 是否包含元数据
            
        Returns:
            字典表示
        """
        result = {
            'year': self.year,
            'month': self.month,
            'day': self.day
        }
        
        if include_metadata:
            result.update({
                'format': self._input_format,
                'weekday': self.get_weekday(),
                'is_weekend': self.is_weekend(),
                'quarter': self.get_quarter(),
                'iso_string': self.format_iso(),
                'compact_string': self.format_compact()
            })
        
        return result
    
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
    
    def format_weekday(self, lang: str = 'zh') -> str:
        """格式化星期几"""
        weekday = self.get_weekday()
        if lang == 'zh':
            weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        else:  # en
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return weekdays[weekday]
    
    def format_month_name(self, lang: str = 'zh') -> str:
        """格式化月份名称"""
        if lang == 'zh':
            months = ['一月', '二月', '三月', '四月', '五月', '六月',
                     '七月', '八月', '九月', '十月', '十一月', '十二月']
        else:  # en
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
        return months[self.month - 1]
    
    def format_relative(self, reference_date: Optional['Date'] = None, lang: str = 'zh') -> str:
        """相对时间格式化"""
        if reference_date is None:
            reference_date = Date.today()
        
        diff_days = reference_date.calculate_difference_days(self)
        
        if lang == 'zh':
            if diff_days == 0:
                return "今天"
            elif diff_days == 1:
                return "明天"
            elif diff_days == -1:
                return "昨天"
            elif diff_days == 2:
                return "后天"
            elif diff_days == -2:
                return "前天"
            elif 3 <= diff_days <= 6:
                return f"{diff_days}天后"
            elif -6 <= diff_days <= -3:
                return f"{abs(diff_days)}天前"
            elif 7 <= diff_days <= 13:
                return "下周"
            elif -13 <= diff_days <= -7:
                return "上周"
            elif diff_days > 0:
                return f"{diff_days}天后"
            else:
                return f"{abs(diff_days)}天前"
        else:  # en
            if diff_days == 0:
                return "today"
            elif diff_days == 1:
                return "tomorrow"
            elif diff_days == -1:
                return "yesterday"
            elif diff_days > 0:
                return f"in {diff_days} days"
            else:
                return f"{abs(diff_days)} days ago"
    
    def format_localized(self, format_type: str = 'full', language_code: Optional[str] = None) -> str:
        """多语言本地化格式 (v1.0.8)
        
        Args:
            format_type: 格式类型 (full, short, year_month, month_day)
            language_code: 语言代码，None时使用全局设置
            
        Returns:
            本地化格式的日期字符串
            
        Example:
            >>> Date.set_language('en_US')
            >>> date = Date('20250415')
            >>> print(date.format_localized())  # 04/15/2025
            >>> print(date.format_localized('short'))  # 04/15/2025
        """
        return Language.format_date(self.year, self.month, self.day, format_type, language_code)
    
    def format_weekday_localized(self, short: bool = False, language_code: Optional[str] = None) -> str:
        """多语言星期几格式 (v1.0.8)
        
        Args:
            short: 是否使用短名称
            language_code: 语言代码，None时使用全局设置
            
        Returns:
            本地化的星期几名称
            
        Example:
            >>> Date.set_language('ja_JP')
            >>> date = Date('20250415')  # 星期二
            >>> print(date.format_weekday_localized())  # 火曜日
            >>> print(date.format_weekday_localized(short=True))  # 火
        """
        weekday_index = self.get_weekday()
        return Language.get_weekday_name(weekday_index, short, language_code)
    
    def format_month_localized(self, short: bool = False, language_code: Optional[str] = None) -> str:
        """多语言月份格式 (v1.0.8)
        
        Args:
            short: 是否使用短名称
            language_code: 语言代码，None时使用全局设置
            
        Returns:
            本地化的月份名称
        """
        return Language.get_month_name(self.month, short, language_code)
    
    def format_quarter_localized(self, short: bool = False, language_code: Optional[str] = None) -> str:
        """多语言季度格式 (v1.0.8)
        
        Args:
            short: 是否使用短名称  
            language_code: 语言代码，None时使用全局设置
            
        Returns:
            本地化的季度名称
        """
        quarter = self.get_quarter()
        return Language.get_quarter_name(quarter, short, language_code)
    
    def format_relative_localized(self, reference_date: Optional['Date'] = None, 
                                 language_code: Optional[str] = None) -> str:
        """多语言相对时间格式 (v1.0.8)
        
        Args:
            reference_date: 参考日期，None时使用今天
            language_code: 语言代码，None时使用全局设置
            
        Returns:
            本地化的相对时间描述
            
        Example:
            >>> Date.set_language('en_US')
            >>> today = Date.today()
            >>> tomorrow = today.add_days(1)
            >>> print(tomorrow.format_relative_localized())  # tomorrow
        """
        if reference_date is None:
            reference_date = Date.today()
        
        diff_days = reference_date.calculate_difference_days(self)
        
        if diff_days == 0:
            return Language.format_relative_time('today', language_code=language_code)
        elif diff_days == 1:
            return Language.format_relative_time('tomorrow', language_code=language_code)
        elif diff_days == -1:
            return Language.format_relative_time('yesterday', language_code=language_code)
        elif diff_days > 0:
            if diff_days <= 6:
                return Language.format_relative_time('days_later', diff_days, language_code)
            elif diff_days <= 28:
                weeks = diff_days // 7
                return Language.format_relative_time('weeks_later', weeks, language_code)
            elif diff_days <= 365:
                months = diff_days // 30
                return Language.format_relative_time('months_later', months, language_code)
            else:
                years = diff_days // 365
                return Language.format_relative_time('years_later', years, language_code)
        else:
            abs_days = abs(diff_days)
            if abs_days <= 6:
                return Language.format_relative_time('days_ago', abs_days, language_code)
            elif abs_days <= 28:
                weeks = abs_days // 7
                return Language.format_relative_time('weeks_ago', weeks, language_code)
            elif abs_days <= 365:
                months = abs_days // 30
                return Language.format_relative_time('months_ago', months, language_code)
            else:
                years = abs_days // 365
                return Language.format_relative_time('years_ago', years, language_code)
    
    def format_lunar(self, include_year: bool = True, include_zodiac: bool = False,
                    language_code: Optional[str] = None) -> str:
        """农历格式化 (v1.0.8)
        
        Args:
            include_year: 是否包含年份
            include_zodiac: 是否包含生肖
            language_code: 语言代码，None时使用全局设置
            
        Returns:
            农历日期字符串
            
        Example:
            >>> date = Date('20250415')
            >>> print(date.format_lunar())  # 农历2025年三月十八
            >>> print(date.format_lunar(include_zodiac=True))  # 乙巳(蛇)年三月十八
        """
        lunar = self.to_lunar()
        return lunar.format_chinese(include_year, include_zodiac)
    
    def format_lunar_compact(self) -> str:
        """农历紧凑格式 (v1.0.8)
        
        Returns:
            农历紧凑格式字符串
            
        Example:
            >>> date = Date('20250415')
            >>> print(date.format_lunar_compact())  # 20250318
        """
        lunar = self.to_lunar()
        return lunar.format_compact()
    
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
    
    def get_quarter_start(self) -> 'Date':
        """获取季度开始日期"""
        quarter = self.get_quarter()
        start_month = (quarter - 1) * 3 + 1
        return self._create_with_same_format(self.year, start_month, 1)
    
    def get_quarter_end(self) -> 'Date':
        """获取季度结束日期"""
        quarter = self.get_quarter()
        end_month = quarter * 3
        if end_month == 3:
            end_day = 31
        elif end_month == 6:
            end_day = 30
        elif end_month == 9:
            end_day = 30
        else:  # 12
            end_day = 31
        return self._create_with_same_format(self.year, end_month, end_day)
    
    def get_week_start(self) -> 'Date':
        """获取本周开始日期（周一）"""
        days_since_monday = self.get_weekday()
        start_date = self.subtract_days(days_since_monday)
        return start_date
    
    def get_week_end(self) -> 'Date':
        """获取本周结束日期（周日）"""
        days_until_sunday = 6 - self.get_weekday()
        end_date = self.add_days(days_until_sunday)
        return end_date
    
    def get_days_in_month(self) -> int:
        """获取当月天数"""
        return calendar.monthrange(self.year, self.month)[1]
    
    def get_days_in_year(self) -> int:
        """获取当年天数"""
        return 366 if calendar.isleap(self.year) else 365
    
    def get_quarter(self) -> int:
        """获取季度 (1-4)"""
        return (self.month - 1) // 3 + 1
    
    def get_week_of_year(self) -> int:
        """获取年内第几周 (ISO周数)"""
        return self.to_date_object().isocalendar()[1]
    
    def get_day_of_year(self) -> int:
        """获取年内第几天 (1-366)"""
        return self.to_date_object().timetuple().tm_yday
    
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
    
    def is_business_day(self) -> bool:
        """是否为工作日（简单版本，仅考虑周末）"""
        return self.get_weekday() < 5
    
    def is_quarter_start(self) -> bool:
        """是否为季度开始"""
        return self.day == 1 and self.month in [1, 4, 7, 10]
    
    def is_quarter_end(self) -> bool:
        """是否为季度结束"""
        quarter_end_months = {3: 31, 6: 30, 9: 30, 12: 31}
        return (self.month in quarter_end_months and 
                self.day == quarter_end_months[self.month])
    
    def is_lunar_new_year(self) -> bool:
        """是否为农历新年 (v1.0.8)
        
        Returns:
            是否为农历正月初一
        """
        lunar = self.to_lunar()
        return lunar.month == 1 and lunar.day == 1 and not lunar.is_leap
    
    def is_lunar_month_start(self) -> bool:
        """是否为农历月初 (v1.0.8)
        
        Returns:
            是否为农历月初一
        """
        lunar = self.to_lunar()
        return lunar.day == 1
    
    def is_lunar_month_mid(self) -> bool:
        """是否为农历月中 (v1.0.8)
        
        Returns:
            是否为农历十五
        """
        lunar = self.to_lunar()
        return lunar.day == 15
    
    def is_lunar_leap_month(self) -> bool:
        """是否在农历闰月 (v1.0.8)
        
        Returns:
            是否为农历闰月
        """
        lunar = self.to_lunar()
        return lunar.is_leap
    
    def is_holiday(self, country: str = 'CN') -> bool:
        """是否为节假日（增强版实现）
        
        Args:
            country: 国家代码 ('CN', 'US', 'UK', 'JP' 等)
            
        Returns:
            是否为节假日
            
        Note:
            支持多国节假日，包含农历节日计算
        """
        if country == 'CN':
            # 中国固定节假日
            fixed_holidays = [
                (1, 1),   # 元旦
                (5, 1),   # 劳动节
                (10, 1),  # 国庆节
                (10, 2),  # 国庆节
                (10, 3),  # 国庆节
                (12, 13), # 国家公祭日
            ]
            
            # 检查固定节假日
            if (self.month, self.day) in fixed_holidays:
                return True
                
            # 特殊节日计算
            # 春节：农历正月初一（简化版本，实际需要农历计算）
            # 清明节：4月4日或5日（简化）
            if self.month == 4 and self.day in [4, 5]:
                return True
                
            # 端午节、中秋节等需要农历计算，这里提供扩展接口
            return self._check_lunar_holidays()
            
        elif country == 'US':
            # 美国节假日
            fixed_holidays = [
                (1, 1),   # New Year's Day
                (7, 4),   # Independence Day
                (12, 25), # Christmas Day
                (11, 11), # Veterans Day
            ]
            
            if (self.month, self.day) in fixed_holidays:
                return True
                
            # 感恩节：11月第四个星期四
            if self.month == 11:
                return self._is_thanksgiving()
                
        elif country == 'JP':
            # 日本节假日
            fixed_holidays = [
                (1, 1),   # 元日
                (2, 11),  # 建国記念の日
                (4, 29),  # 昭和の日
                (5, 3),   # 憲法記念日
                (5, 4),   # みどりの日
                (5, 5),   # こどもの日
                (11, 3),  # 文化の日
                (11, 23), # 勤労感謝の日
                (12, 23), # 天皇誕生日
            ]
            return (self.month, self.day) in fixed_holidays
            
        elif country == 'UK':
            # 英国节假日
            fixed_holidays = [
                (1, 1),   # New Year's Day
                (12, 25), # Christmas Day
                (12, 26), # Boxing Day
            ]
            return (self.month, self.day) in fixed_holidays
            
        else:
            # 未知国家，返回False
            return False
    
    def _check_lunar_holidays(self) -> bool:
        """检查农历节假日（扩展接口）
        
        Note:
            这是一个扩展接口，实际项目中可以集成农历库
            如 `lunardate` 或 `zhdate` 等第三方库
        """
        # 这里可以扩展农历节日计算
        # 目前返回 False，保持轻量级
        return False
    
    def _is_thanksgiving(self) -> bool:
        """判断是否为美国感恩节（11月第四个星期四）"""
        if self.month != 11:
            return False
            
        # 找到11月第一天是星期几
        first_day = Date(self.year, 11, 1)
        first_weekday = first_day.get_weekday()
        
        # 计算第四个星期四的日期
        # 星期四是weekday=3
        days_to_first_thursday = (3 - first_weekday) % 7
        fourth_thursday = 1 + days_to_first_thursday + 21  # 第四个星期四
        
        return self.day == fourth_thursday
    
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
    
    def calculate_age_years(self, reference_date: Optional['Date'] = None) -> int:
        """计算年龄（以年为单位）"""
        if reference_date is None:
            reference_date = Date.today()
        
        age = reference_date.year - self.year
        
        # 如果还没到生日，年龄减1
        if (reference_date.month, reference_date.day) < (self.month, self.day):
            age -= 1
            
        return age
    
    def days_until(self, target_date: 'Date') -> int:
        """计算距离目标日期还有多少天"""
        return self.calculate_difference_days(target_date)
    
    def days_since(self, start_date: 'Date') -> int:
        """计算从起始日期过了多少天"""
        return start_date.calculate_difference_days(self)
    
    # =============================================
    # 批量处理方法
    # =============================================
    
    @classmethod
    def batch_create(cls, date_strings: List[str]) -> List['Date']:
        """批量创建Date对象
        
        Args:
            date_strings: 日期字符串列表
            
        Returns:
            Date对象列表
            
        Raises:
            InvalidDateFormatError: 如果某个字符串格式无效
        """
        result = []
        for date_str in date_strings:
            try:
                result.append(cls(date_str))
            except (InvalidDateFormatError, InvalidDateValueError) as e:
                cls._logger.error(f"批量创建失败: {date_str} - {e}")
                raise
        return result
    
    @classmethod
    def batch_format(cls, dates: List['Date'], format_type: str = 'iso') -> List[str]:
        """批量格式化日期
        
        Args:
            dates: Date对象列表
            format_type: 格式类型 ('iso', 'chinese', 'compact' 等)
            
        Returns:
            格式化后的字符串列表
        """
        format_methods = {
            'iso': lambda d: d.format_iso(),
            'chinese': lambda d: d.format_chinese(),
            'compact': lambda d: d.format_compact(),
            'slash': lambda d: d.format_slash(),
            'dot': lambda d: d.format_dot(),
            'default': lambda d: d.format_default()
        }
        
        format_func = format_methods.get(format_type, lambda d: d.format_default())
        return [format_func(date) for date in dates]
    
    @classmethod
    def batch_add_days(cls, dates: List['Date'], days: int) -> List['Date']:
        """批量添加天数
        
        Args:
            dates: Date对象列表
            days: 要添加的天数
            
        Returns:
            新的Date对象列表
        """
        return [date.add_days(days) for date in dates]
    
    def apply_business_rule(self, rule: str, **kwargs) -> 'Date':
        """应用业务规则
        
        Args:
            rule: 规则名称
                - 'month_end': 移动到月末
                - 'quarter_end': 移动到季度末
                - 'next_business_day': 移动到下一个工作日
                - 'prev_business_day': 移动到上一个工作日
            **kwargs: 规则参数
            
        Returns:
            应用规则后的新Date对象
        """
        if rule == 'month_end':
            return self.get_month_end()
        elif rule == 'quarter_end':
            return self.get_quarter_end()
        elif rule == 'next_business_day':
            current = self
            while not current.is_business_day():
                current = current.add_days(1)
            return current
        elif rule == 'prev_business_day':
            current = self
            while not current.is_business_day():
                current = current.subtract_days(1)
            return current
        else:
            raise ValueError(f"未知的业务规则: {rule}")
    
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
    
    def compare_lunar(self, other: 'Date') -> int:
        """农历日期比较 (v1.0.8)
        
        Args:
            other: 另一个Date对象
            
        Returns:
            -1: self < other, 0: self == other, 1: self > other
            
        Example:
            >>> date1 = Date.from_lunar(2025, 1, 1)  # 农历正月初一
            >>> date2 = Date.from_lunar(2025, 1, 15) # 农历正月十五
            >>> print(date1.compare_lunar(date2))    # -1
        """
        lunar_self = self.to_lunar()
        lunar_other = other.to_lunar()
        
        if lunar_self < lunar_other:
            return -1
        elif lunar_self > lunar_other:
            return 1
        else:
            return 0
    
    def is_same_lunar_month(self, other: 'Date') -> bool:
        """是否同一农历月份 (v1.0.8)
        
        Args:
            other: 另一个Date对象
            
        Returns:
            是否为同一农历月份
        """
        lunar_self = self.to_lunar()
        lunar_other = other.to_lunar()
        return (lunar_self.year == lunar_other.year and
                lunar_self.month == lunar_other.month and
                lunar_self.is_leap == lunar_other.is_leap)
    
    def is_same_lunar_day(self, other: 'Date') -> bool:
        """是否同一农历日期 (v1.0.8)
        
        Args:
            other: 另一个Date对象
            
        Returns:
            是否为同一农历日期
        """
        lunar_self = self.to_lunar()
        lunar_other = other.to_lunar()
        return lunar_self == lunar_other
    
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
