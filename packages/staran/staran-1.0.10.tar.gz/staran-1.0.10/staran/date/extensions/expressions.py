#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran 日期表达式解析模块 v1.0.10
==============================

提供自然语言日期表达式的解析功能，支持中文和英文表达。

主要功能：
- 自然语言日期解析
- 相对日期表达式
- 日期计算表达式
- 智能日期推断
"""

import re
import datetime
from typing import Optional, Union, Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ParseResult:
    """解析结果类"""
    success: bool
    date: Optional[datetime.date]
    expression: str
    confidence: float  # 置信度 0-1
    matched_pattern: str
    extracted_components: Dict[str, any]

class DateExpressionParser:
    """日期表达式解析器"""
    
    def __init__(self):
        self._init_patterns()
    
    def _init_patterns(self):
        """初始化解析模式"""
        
        # 中文数字映射
        self.chinese_numbers = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
            '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, 
            '二十五': 25, '二十六': 26, '二十七': 27, '二十八': 28,
            '二十九': 29, '三十': 30, '三十一': 31
        }
        
        # 月份映射
        self.month_names = {
            # 中文
            '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
            '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12,
            '正月': 1, '腊月': 12,
            # 英文
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7,
            'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        # 星期映射
        self.weekday_names = {
            # 中文
            '周一': 0, '周二': 1, '周三': 2, '周四': 3, '周五': 4, '周六': 5, '周日': 6,
            '星期一': 0, '星期二': 1, '星期三': 2, '星期四': 3, '星期五': 4, '星期六': 5, '星期日': 6,
            '星期天': 6, '礼拜一': 0, '礼拜二': 1, '礼拜三': 2, '礼拜四': 3, '礼拜五': 4, '礼拜六': 5, '礼拜天': 6,
            # 英文
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6,
            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6
        }
        
        # 相对时间表达式模式
        self.patterns = {
            # 绝对日期表达式
            'absolute_dates': [
                # YYYY年MM月DD日
                r'(\d{4})年(\d{1,2})月(\d{1,2})日?',
                # YYYY-MM-DD, YYYY/MM/DD
                r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',
                # MM月DD日 (当年)
                r'(\d{1,2})月(\d{1,2})日?',
                # 中文数字日期
                r'([一二三四五六七八九十]+)年([一二三四五六七八九十]+)月([一二三四五六七八九十]+)日?',
            ],
            
            # 相对日期表达式
            'relative_dates': [
                # 今天、明天、后天、昨天、前天
                r'(今天|明天|后天|昨天|前天|大后天)',
                r'(today|tomorrow|yesterday)',
                
                # N天前/后
                r'(\d+)天(前|后|之前|之后)',
                r'(\d+)\s*(days?)\s*(ago|later|before|after)',
                
                # N周前/后
                r'(\d+)(周|星期|礼拜)(前|后|之前|之后)',
                r'(\d+)\s*(weeks?)\s*(ago|later|before|after)',
                
                # N个月前/后
                r'(\d+)个?月(前|后|之前|之后)',
                r'(\d+)\s*(months?)\s*(ago|later|before|after)',
                
                # N年前/后
                r'(\d+)年(前|后|之前|之后)',
                r'(\d+)\s*(years?)\s*(ago|later|before|after)',
                
                # 上/下 + 时间单位
                r'(上|下)(周|星期|礼拜|月|年)',
                r'(last|next)\s*(week|month|year)',
                
                # 这/本 + 时间单位
                r'(这|本)(周|星期|礼拜|月|年)',
                r'(this)\s*(week|month|year)',
            ],
            
            # 星期表达式
            'weekday_expressions': [
                # 这周/下周/上周 + 星期X
                r'(这|本|下|上)(周|星期|礼拜)([一二三四五六日天])',
                r'(this|next|last)\s*(week)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                
                # 直接星期X
                r'(周|星期|礼拜)([一二三四五六日天])',
                r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            ],
            
            # 节假日和特殊日期
            'special_dates': [
                r'(春节|除夕|元宵节|清明节|劳动节|端午节|中秋节|国庆节|圣诞节|元旦)',
                r'(new\s*year|christmas|valentine|halloween|thanksgiving)',
                r'(母亲节|父亲节|儿童节|教师节|妇女节)',
                r'(生日|结婚纪念日|工作日|周末)',
            ],
            
            # 季度和月份表达式
            'quarter_month': [
                r'(第?[一二三四1234])季度',
                r'([一二三四五六七八九十\d]+)月',
                r'(Q[1234])',
                r'(spring|summer|autumn|fall|winter)',
                r'(春天|夏天|秋天|冬天)',
            ]
        }
    
    def parse(self, expression: str) -> ParseResult:
        """解析日期表达式"""
        expression = expression.strip()
        
        # 尝试不同的解析策略
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                result = self._try_parse_pattern(expression, pattern, pattern_type)
                if result.success:
                    return result
        
        # 如果所有模式都失败，返回失败结果
        return ParseResult(
            success=False,
            date=None,
            expression=expression,
            confidence=0.0,
            matched_pattern='',
            extracted_components={}
        )
    
    def _try_parse_pattern(self, expression: str, pattern: str, pattern_type: str) -> ParseResult:
        """尝试匹配特定模式"""
        match = re.search(pattern, expression, re.IGNORECASE)
        if not match:
            return ParseResult(False, None, expression, 0.0, pattern, {})
        
        try:
            if pattern_type == 'absolute_dates':
                return self._parse_absolute_date(match, pattern, expression)
            elif pattern_type == 'relative_dates':
                return self._parse_relative_date(match, pattern, expression)
            elif pattern_type == 'weekday_expressions':
                return self._parse_weekday_expression(match, pattern, expression)
            elif pattern_type == 'special_dates':
                return self._parse_special_date(match, pattern, expression)
            elif pattern_type == 'quarter_month':
                return self._parse_quarter_month(match, pattern, expression)
            
        except Exception as e:
            pass
        
        return ParseResult(False, None, expression, 0.0, pattern, {})
    
    def _parse_absolute_date(self, match, pattern: str, expression: str) -> ParseResult:
        """解析绝对日期"""
        groups = match.groups()
        
        if len(groups) == 3:
            if '年' in pattern:
                # 年月日格式
                year_str, month_str, day_str = groups
                if any(c in year_str for c in '一二三四五六七八九十'):
                    # 中文数字
                    year = self._chinese_to_number(year_str)
                    month = self._chinese_to_number(month_str)
                    day = self._chinese_to_number(day_str)
                else:
                    year, month, day = int(year_str), int(month_str), int(day_str)
            else:
                # YYYY-MM-DD 或 YYYY/MM/DD
                year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
            
            try:
                date = datetime.date(year, month, day)
                return ParseResult(
                    success=True,
                    date=date,
                    expression=expression,
                    confidence=0.95,
                    matched_pattern=pattern,
                    extracted_components={'year': year, 'month': month, 'day': day}
                )
            except ValueError:
                pass
        
        elif len(groups) == 2:
            # MM月DD日 (当年)
            month_str, day_str = groups
            current_year = datetime.date.today().year
            
            if any(c in month_str for c in '一二三四五六七八九十'):
                month = self._chinese_to_number(month_str)
                day = self._chinese_to_number(day_str)
            else:
                month, day = int(month_str), int(day_str)
            
            try:
                date = datetime.date(current_year, month, day)
                return ParseResult(
                    success=True,
                    date=date,
                    expression=expression,
                    confidence=0.85,
                    matched_pattern=pattern,
                    extracted_components={'year': current_year, 'month': month, 'day': day}
                )
            except ValueError:
                pass
        
        return ParseResult(False, None, expression, 0.0, pattern, {})
    
    def _parse_relative_date(self, match, pattern: str, expression: str) -> ParseResult:
        """解析相对日期"""
        groups = match.groups()
        today = datetime.date.today()
        
        # 简单相对日期
        if len(groups) == 1:
            term = groups[0].lower()
            
            relative_map = {
                '今天': 0, 'today': 0,
                '明天': 1, 'tomorrow': 1,
                '后天': 2,
                '昨天': -1, 'yesterday': -1,
                '前天': -2,
                '大后天': 3,
            }
            
            if term in relative_map:
                days_offset = relative_map[term]
                target_date = today + datetime.timedelta(days=days_offset)
                return ParseResult(
                    success=True,
                    date=target_date,
                    expression=expression,
                    confidence=0.9,
                    matched_pattern=pattern,
                    extracted_components={'offset_days': days_offset}
                )
        
        # 数量 + 时间单位 + 方向
        elif len(groups) >= 2:
            try:
                num_str = groups[0]
                direction = groups[-1] if len(groups) > 1 else ''
                
                # 确定数量
                num = int(num_str) if num_str.isdigit() else self._chinese_to_number(num_str)
                
                # 确定方向（正负）
                is_past = any(word in direction.lower() for word in ['前', '之前', 'ago', 'before'])
                if is_past:
                    num = -num
                
                # 确定时间单位
                unit = ''
                for group in groups[1:-1]:
                    unit += group
                
                # 计算目标日期
                if '天' in unit or 'day' in unit:
                    target_date = today + datetime.timedelta(days=num)
                elif any(word in unit for word in ['周', '星期', '礼拜', 'week']):
                    target_date = today + datetime.timedelta(weeks=num)
                elif '月' in unit or 'month' in unit:
                    target_date = self._add_months(today, num)
                elif '年' in unit or 'year' in unit:
                    target_date = self._add_years(today, num)
                else:
                    return ParseResult(False, None, expression, 0.0, pattern, {})
                
                return ParseResult(
                    success=True,
                    date=target_date,
                    expression=expression,
                    confidence=0.85,
                    matched_pattern=pattern,
                    extracted_components={'number': abs(num), 'unit': unit, 'direction': direction}
                )
            except:
                pass
        
        return ParseResult(False, None, expression, 0.0, pattern, {})
    
    def _parse_weekday_expression(self, match, pattern: str, expression: str) -> ParseResult:
        """解析星期表达式"""
        groups = match.groups()
        today = datetime.date.today()
        
        # 提取星期几
        weekday_name = ''
        week_modifier = ''
        
        for group in groups:
            if group:
                group_lower = group.lower()
                if group_lower in self.weekday_names:
                    weekday_name = group_lower
                elif any(word in group_lower for word in ['上', '下', '这', '本', 'last', 'next', 'this']):
                    week_modifier = group_lower
                elif group in '一二三四五六日天':
                    weekday_name = f'星期{group}'
        
        if not weekday_name:
            # 尝试从单个字符推断星期
            for group in groups:
                if group in '一二三四五六日天':
                    weekday_name = f'星期{group}'
                    break
        
        if weekday_name in self.weekday_names:
            target_weekday = self.weekday_names[weekday_name]
            current_weekday = today.weekday()
            
            # 计算到目标星期几的天数
            days_ahead = target_weekday - current_weekday
            
            # 根据修饰符调整
            if any(word in week_modifier for word in ['下', 'next']):
                if days_ahead <= 0:
                    days_ahead += 7
            elif any(word in week_modifier for word in ['上', 'last']):
                if days_ahead >= 0:
                    days_ahead -= 7
            elif any(word in week_modifier for word in ['这', '本', 'this']):
                # 本周的星期X
                pass
            else:
                # 默认是下一个该星期几
                if days_ahead <= 0:
                    days_ahead += 7
            
            target_date = today + datetime.timedelta(days=days_ahead)
            
            return ParseResult(
                success=True,
                date=target_date,
                expression=expression,
                confidence=0.8,
                matched_pattern=pattern,
                extracted_components={'weekday': target_weekday, 'modifier': week_modifier}
            )
        
        return ParseResult(False, None, expression, 0.0, pattern, {})
    
    def _parse_special_date(self, match, pattern: str, expression: str) -> ParseResult:
        """解析特殊日期（节假日等）"""
        holiday_name = match.group(1).lower()
        current_year = datetime.date.today().year
        
        # 中国节假日映射
        chinese_holidays = {
            '元旦': (1, 1),
            '春节': (2, 10),  # 简化，实际需要农历计算
            '清明节': (4, 5),  # 简化
            '劳动节': (5, 1),
            '端午节': (6, 14),  # 简化，实际需要农历计算
            '中秋节': (9, 17),  # 简化，实际需要农历计算
            '国庆节': (10, 1),
            '圣诞节': (12, 25),
        }
        
        # 英文节假日映射
        english_holidays = {
            'new year': (1, 1),
            'christmas': (12, 25),
            'valentine': (2, 14),
            'halloween': (10, 31),
        }
        
        target_date = None
        if holiday_name in chinese_holidays:
            month, day = chinese_holidays[holiday_name]
            target_date = datetime.date(current_year, month, day)
        elif holiday_name in english_holidays:
            month, day = english_holidays[holiday_name]
            target_date = datetime.date(current_year, month, day)
        
        if target_date:
            return ParseResult(
                success=True,
                date=target_date,
                expression=expression,
                confidence=0.7,
                matched_pattern=pattern,
                extracted_components={'holiday': holiday_name}
            )
        
        return ParseResult(False, None, expression, 0.0, pattern, {})
    
    def _parse_quarter_month(self, match, pattern: str, expression: str) -> ParseResult:
        """解析季度和月份表达式"""
        groups = match.groups()
        today = datetime.date.today()
        current_year = today.year
        
        quarter_str = groups[0].lower()
        
        # 季度映射
        quarter_map = {
            '第一季度': 1, '第二季度': 2, '第三季度': 3, '第四季度': 4,
            '一季度': 1, '二季度': 2, '三季度': 3, '四季度': 4,
            'q1': 1, 'q2': 2, 'q3': 3, 'q4': 4,
        }
        
        # 季节映射
        season_map = {
            'spring': 1, '春天': 1,
            'summer': 2, '夏天': 2, 
            'autumn': 3, 'fall': 3, '秋天': 3,
            'winter': 4, '冬天': 4,
        }
        
        # 月份处理
        if '月' in quarter_str and quarter_str not in season_map:
            month_str = quarter_str.replace('月', '')
            try:
                month = int(month_str) if month_str.isdigit() else self._chinese_to_number(month_str)
                if 1 <= month <= 12:
                    target_date = datetime.date(current_year, month, 1)
                    return ParseResult(
                        success=True,
                        date=target_date,
                        expression=expression,
                        confidence=0.8,
                        matched_pattern=pattern,
                        extracted_components={'month': month}
                    )
            except:
                pass
        
        # 季度或季节处理
        quarter = quarter_map.get(quarter_str) or season_map.get(quarter_str)
        if quarter:
            # 每个季度的第一个月
            quarter_start_month = (quarter - 1) * 3 + 1
            target_date = datetime.date(current_year, quarter_start_month, 1)
            
            return ParseResult(
                success=True,
                date=target_date,
                expression=expression,
                confidence=0.75,
                matched_pattern=pattern,
                extracted_components={'quarter': quarter}
            )
        
        return ParseResult(False, None, expression, 0.0, pattern, {})
    
    def _chinese_to_number(self, chinese_str: str) -> int:
        """中文数字转阿拉伯数字"""
        if chinese_str in self.chinese_numbers:
            return self.chinese_numbers[chinese_str]
        
        # 处理复合数字（如二十三）
        if '十' in chinese_str:
            if chinese_str.startswith('十'):
                # 十X -> 10 + X
                if len(chinese_str) > 1:
                    return 10 + self.chinese_numbers.get(chinese_str[1], 0)
                return 10
            else:
                # X十Y -> X*10 + Y
                parts = chinese_str.split('十')
                tens = self.chinese_numbers.get(parts[0], 0) * 10
                ones = self.chinese_numbers.get(parts[1], 0) if len(parts) > 1 and parts[1] else 0
                return tens + ones
        
        # 尝试直接转换
        try:
            return int(chinese_str)
        except ValueError:
            return 0
    
    def _add_months(self, date: datetime.date, months: int) -> datetime.date:
        """添加月份"""
        year = date.year
        month = date.month + months
        
        while month > 12:
            year += 1
            month -= 12
        while month < 1:
            year -= 1
            month += 12
        
        # 处理日期溢出（如31号在2月）
        try:
            return datetime.date(year, month, date.day)
        except ValueError:
            # 如果日期无效，使用该月最后一天
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            return datetime.date(year, month, min(date.day, last_day))
    
    def _add_years(self, date: datetime.date, years: int) -> datetime.date:
        """添加年份"""
        try:
            return datetime.date(date.year + years, date.month, date.day)
        except ValueError:
            # 闰年处理（2月29日）
            return datetime.date(date.year + years, date.month, 28)

# 便捷函数
def parse_date_expression(expression: str) -> ParseResult:
    """解析日期表达式（便捷函数）"""
    parser = DateExpressionParser()
    return parser.parse(expression)

def smart_parse_date(expression: str) -> Optional[datetime.date]:
    """智能解析日期，返回日期对象或None"""
    result = parse_date_expression(expression)
    return result.date if result.success else None
