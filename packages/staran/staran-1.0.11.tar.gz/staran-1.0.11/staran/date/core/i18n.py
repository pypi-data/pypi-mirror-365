#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多语言配置模块
=============

提供中简、中繁、日、英四种语言的配置支持，
支持全局语言设置和单次使用覆盖。
"""

from typing import Dict, Any, Optional
import threading


class Language:
    """语言配置类
    
    支持中简、中繁、日、英四种语言的本地化配置。
    配置一次后全局生效，也支持单次使用时覆盖。
    """
    
    # 支持的语言代码
    SUPPORTED_LANGUAGES = ['zh_CN', 'zh_TW', 'ja_JP', 'en_US']
    
    # 语言配置数据
    _LANGUAGE_DATA = {
        'zh_CN': {  # 中文简体
            'name': '中文简体',
            'weekdays': ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'],
            'weekdays_short': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            'months': ['一月', '二月', '三月', '四月', '五月', '六月',
                      '七月', '八月', '九月', '十月', '十一月', '十二月'],
            'months_short': ['1月', '2月', '3月', '4月', '5月', '6月',
                           '7月', '8月', '9月', '10月', '11月', '12月'],
            'date_formats': {
                'full': '{year}年{month:02d}月{day:02d}日',
                'short': '{year}/{month:02d}/{day:02d}',
                'year_month': '{year}年{month:02d}月',
                'month_day': '{month:02d}月{day:02d}日'
            },
            'relative_time': {
                'today': '今天',
                'tomorrow': '明天',
                'yesterday': '昨天',
                'days_ago': '{days}天前',
                'days_later': '{days}天后',
                'weeks_ago': '{weeks}周前',
                'weeks_later': '{weeks}周后',
                'months_ago': '{months}个月前',
                'months_later': '{months}个月后',
                'years_ago': '{years}年前',
                'years_later': '{years}年后'
            },
            'quarters': ['第一季度', '第二季度', '第三季度', '第四季度'],
            'quarters_short': ['Q1', 'Q2', 'Q3', 'Q4'],
            'lunar': {
                'prefix': '农历',
                'leap_month': '闰{month}月',
                'ganzhi_year': '{ganzhi}年',
                'zodiac_year': '{zodiac}年'
            },
            'business_terms': {
                'business_day': '工作日',
                'weekend': '周末',
                'holiday': '节假日',
                'workday': '工作日'
            }
        },
        'zh_TW': {  # 中文繁体
            'name': '中文繁體',
            'weekdays': ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'],
            'weekdays_short': ['週一', '週二', '週三', '週四', '週五', '週六', '週日'],
            'months': ['一月', '二月', '三月', '四月', '五月', '六月',
                      '七月', '八月', '九月', '十月', '十一月', '十二月'],
            'months_short': ['1月', '2月', '3月', '4月', '5月', '6月',
                           '7月', '8月', '9月', '10月', '11月', '12月'],
            'date_formats': {
                'full': '{year}年{month:02d}月{day:02d}日',
                'short': '{year}/{month:02d}/{day:02d}',
                'year_month': '{year}年{month:02d}月',
                'month_day': '{month:02d}月{day:02d}日'
            },
            'relative_time': {
                'today': '今天',
                'tomorrow': '明天',
                'yesterday': '昨天',
                'days_ago': '{days}天前',
                'days_later': '{days}天後',
                'weeks_ago': '{weeks}週前',
                'weeks_later': '{weeks}週後',
                'months_ago': '{months}個月前',
                'months_later': '{months}個月後',
                'years_ago': '{years}年前',
                'years_later': '{years}年後'
            },
            'quarters': ['第一季度', '第二季度', '第三季度', '第四季度'],
            'quarters_short': ['Q1', 'Q2', 'Q3', 'Q4'],
            'lunar': {
                'prefix': '農曆',
                'leap_month': '閏{month}月',
                'ganzhi_year': '{ganzhi}年',
                'zodiac_year': '{zodiac}年'
            },
            'business_terms': {
                'business_day': '工作日',
                'weekend': '週末',
                'holiday': '節假日',
                'workday': '工作日'
            }
        },
        'ja_JP': {  # 日语
            'name': '日本語',
            'weekdays': ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日'],
            'weekdays_short': ['月', '火', '水', '木', '金', '土', '日'],
            'months': ['1月', '2月', '3月', '4月', '5月', '6月',
                      '7月', '8月', '9月', '10月', '11月', '12月'],
            'months_short': ['1月', '2月', '3月', '4月', '5月', '6月',
                           '7月', '8月', '9月', '10月', '11月', '12月'],
            'date_formats': {
                'full': '{year}年{month:02d}月{day:02d}日',
                'short': '{year}/{month:02d}/{day:02d}',
                'year_month': '{year}年{month:02d}月',
                'month_day': '{month:02d}月{day:02d}日'
            },
            'relative_time': {
                'today': '今日',
                'tomorrow': '明日',
                'yesterday': '昨日',
                'days_ago': '{days}日前',
                'days_later': '{days}日後',
                'weeks_ago': '{weeks}週間前',
                'weeks_later': '{weeks}週間後',
                'months_ago': '{months}ヶ月前',
                'months_later': '{months}ヶ月後',
                'years_ago': '{years}年前',
                'years_later': '{years}年後'
            },
            'quarters': ['第1四半期', '第2四半期', '第3四半期', '第4四半期'],
            'quarters_short': ['Q1', 'Q2', 'Q3', 'Q4'],
            'lunar': {
                'prefix': '旧暦',
                'leap_month': '閏{month}月',
                'ganzhi_year': '{ganzhi}年',
                'zodiac_year': '{zodiac}年'
            },
            'business_terms': {
                'business_day': '営業日',
                'weekend': '週末',
                'holiday': '祝日',
                'workday': '平日'
            }
        },
        'en_US': {  # 英语
            'name': 'English',
            'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'weekdays_short': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'months': ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December'],
            'months_short': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'date_formats': {
                'full': '{month:02d}/{day:02d}/{year}',
                'short': '{month:02d}/{day:02d}/{year}',
                'year_month': '{month:02d}/{year}',
                'month_day': '{month:02d}/{day:02d}'
            },
            'relative_time': {
                'today': 'today',
                'tomorrow': 'tomorrow',
                'yesterday': 'yesterday',
                'days_ago': '{days} days ago',
                'days_later': 'in {days} days',
                'weeks_ago': '{weeks} weeks ago',
                'weeks_later': 'in {weeks} weeks',
                'months_ago': '{months} months ago',
                'months_later': 'in {months} months',
                'years_ago': '{years} years ago',
                'years_later': 'in {years} years'
            },
            'quarters': ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter'],
            'quarters_short': ['Q1', 'Q2', 'Q3', 'Q4'],
            'lunar': {
                'prefix': 'Lunar',
                'leap_month': 'Leap {month}',
                'ganzhi_year': '{ganzhi} Year',
                'zodiac_year': 'Year of {zodiac}'
            },
            'business_terms': {
                'business_day': 'business day',
                'weekend': 'weekend',
                'holiday': 'holiday',
                'workday': 'workday'
            }
        }
    }
    
    # 全局语言设置
    _global_language = 'zh_CN'  # 默认中文简体
    _lock = threading.Lock()
    
    @classmethod
    def set_global_language(cls, language_code: str) -> None:
        """设置全局语言
        
        Args:
            language_code: 语言代码 (zh_CN, zh_TW, ja_JP, en_US)
            
        Raises:
            ValueError: 不支持的语言代码
        """
        if language_code not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(f"不支持的语言代码: {language_code}。支持的语言: {cls.SUPPORTED_LANGUAGES}")
        
        with cls._lock:
            cls._global_language = language_code
    
    @classmethod
    def get_global_language(cls) -> str:
        """获取当前全局语言设置"""
        return cls._global_language
    
    @classmethod
    def get_language_data(cls, language_code: Optional[str] = None) -> Dict[str, Any]:
        """获取语言数据
        
        Args:
            language_code: 语言代码，如果为None则使用全局设置
            
        Returns:
            语言数据字典
            
        Raises:
            ValueError: 不支持的语言代码
        """
        if language_code is None:
            language_code = cls._global_language
        
        if language_code not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(f"不支持的语言代码: {language_code}")
        
        return cls._LANGUAGE_DATA[language_code].copy()
    
    @classmethod
    def get_weekday_name(cls, weekday_index: int, short: bool = False, 
                        language_code: Optional[str] = None) -> str:
        """获取星期几的名称
        
        Args:
            weekday_index: 星期几索引 (0=星期一, 6=星期日)
            short: 是否使用短名称
            language_code: 语言代码
            
        Returns:
            星期几的名称
        """
        data = cls.get_language_data(language_code)
        weekdays = data['weekdays_short'] if short else data['weekdays']
        return weekdays[weekday_index % 7]
    
    @classmethod
    def get_month_name(cls, month: int, short: bool = False, 
                      language_code: Optional[str] = None) -> str:
        """获取月份名称
        
        Args:
            month: 月份 (1-12)
            short: 是否使用短名称
            language_code: 语言代码
            
        Returns:
            月份名称
        """
        data = cls.get_language_data(language_code)
        months = data['months_short'] if short else data['months']
        return months[month - 1]
    
    @classmethod
    def get_quarter_name(cls, quarter: int, short: bool = False, 
                        language_code: Optional[str] = None) -> str:
        """获取季度名称
        
        Args:
            quarter: 季度 (1-4)
            short: 是否使用短名称
            language_code: 语言代码
            
        Returns:
            季度名称
        """
        data = cls.get_language_data(language_code)
        quarters = data['quarters_short'] if short else data['quarters']
        return quarters[quarter - 1]
    
    @classmethod
    def format_date(cls, year: int, month: int, day: int, format_type: str = 'full',
                   language_code: Optional[str] = None) -> str:
        """格式化日期
        
        Args:
            year: 年份
            month: 月份
            day: 日期
            format_type: 格式类型 (full, short, year_month, month_day)
            language_code: 语言代码
            
        Returns:
            格式化后的日期字符串
        """
        data = cls.get_language_data(language_code)
        date_format = data['date_formats'].get(format_type, data['date_formats']['full'])
        return date_format.format(year=year, month=month, day=day)
    
    @classmethod
    def format_relative_time(cls, relative_type: str, value: int = 0,
                           language_code: Optional[str] = None) -> str:
        """格式化相对时间
        
        Args:
            relative_type: 相对时间类型 (today, tomorrow, yesterday, days_ago等)
            value: 数值 (如天数、周数等)
            language_code: 语言代码
            
        Returns:
            格式化后的相对时间字符串
        """
        data = cls.get_language_data(language_code)
        relative_format = data['relative_time'].get(relative_type, relative_type)
        
        if '{' in relative_format:
            # 处理需要替换值的格式
            if 'days' in relative_type:
                return relative_format.format(days=value)
            elif 'weeks' in relative_type:
                return relative_format.format(weeks=value)
            elif 'months' in relative_type:
                return relative_format.format(months=value)
            elif 'years' in relative_type:
                return relative_format.format(years=value)
        
        return relative_format
    
    @classmethod
    def get_business_term(cls, term: str, language_code: Optional[str] = None) -> str:
        """获取商务术语
        
        Args:
            term: 术语名称 (business_day, weekend, holiday, workday)
            language_code: 语言代码
            
        Returns:
            本地化的术语
        """
        data = cls.get_language_data(language_code)
        return data['business_terms'].get(term, term)
    
    @classmethod
    def get_supported_languages(cls) -> Dict[str, str]:
        """获取支持的语言列表
        
        Returns:
            语言代码到语言名称的映射
        """
        return {code: cls._LANGUAGE_DATA[code]['name'] for code in cls.SUPPORTED_LANGUAGES}
    
    @classmethod
    def is_supported_language(cls, language_code: str) -> bool:
        """检查是否支持指定语言
        
        Args:
            language_code: 语言代码
            
        Returns:
            是否支持
        """
        return language_code in cls.SUPPORTED_LANGUAGES
