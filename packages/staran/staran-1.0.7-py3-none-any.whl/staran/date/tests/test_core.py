#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date类核心功能测试
================

测试Date类的所有功能，包括：
- 对象创建和初始化
- 格式记忆和保持
- 日期运算
- 格式化输出
- 比较操作
- 错误处理
- API命名规范
- 向后兼容性
"""

import unittest
import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date.core import Date


class TestDateCreation(unittest.TestCase):
    """测试Date对象创建"""
    
    def test_create_from_string_yyyy(self):
        """测试从YYYY字符串创建"""
        d = Date('2025')
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 1)
        self.assertEqual(str(d), '2025')
    
    def test_create_from_string_yyyymm(self):
        """测试从YYYYMM字符串创建"""
        d = Date('202504')
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 1)
        self.assertEqual(str(d), '202504')
    
    def test_create_from_string_yyyymmdd(self):
        """测试从YYYYMMDD字符串创建"""
        d = Date('20250415')
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
        self.assertEqual(str(d), '20250415')
    
    def test_create_from_position_args(self):
        """测试从位置参数创建"""
        d = Date(2025, 4, 15)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
        self.assertEqual(str(d), '2025-04-15')
    
    def test_create_from_keyword_args(self):
        """测试从关键字参数创建"""
        d = Date(year=2025, month=4, day=15)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
    
    def test_create_from_datetime_object(self):
        """测试从datetime.datetime对象创建"""
        dt = datetime.datetime(2025, 4, 15, 10, 30)
        d = Date(dt)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
    
    def test_create_from_date_object(self):
        """测试从datetime.date对象创建"""
        dt = datetime.date(2025, 4, 15)
        d = Date(dt)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
    
    def test_create_today(self):
        """测试创建今日对象"""
        d = Date()
        today = datetime.date.today()
        self.assertEqual(d.year, today.year)
        self.assertEqual(d.month, today.month)
        self.assertEqual(d.day, today.day)


class TestDateClassMethods(unittest.TestCase):
    """测试Date类方法"""
    
    def test_from_string(self):
        """测试from_string类方法"""
        d = Date.from_string('20250415')
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
    
    def test_from_timestamp(self):
        """测试from_timestamp类方法"""
        timestamp = datetime.datetime(2025, 4, 15).timestamp()
        d = Date.from_timestamp(timestamp)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
    
    def test_from_date_object(self):
        """测试from_date_object类方法"""
        date_obj = datetime.date(2025, 4, 15)
        d = Date.from_date_object(date_obj)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
    
    def test_today(self):
        """测试today类方法"""
        d = Date.today()
        today = datetime.date.today()
        self.assertEqual(d.year, today.year)
        self.assertEqual(d.month, today.month)
        self.assertEqual(d.day, today.day)


class TestDateFormatting(unittest.TestCase):
    """测试日期格式化"""
    
    def setUp(self):
        self.date = Date('20250415')
    
    def test_format_default(self):
        """测试format_default方法"""
        self.assertEqual(self.date.format_default(), '20250415')
    
    def test_format_iso(self):
        """测试format_iso方法"""
        self.assertEqual(self.date.format_iso(), '2025-04-15')
    
    def test_format_chinese(self):
        """测试format_chinese方法"""
        self.assertEqual(self.date.format_chinese(), '2025年04月15日')
    
    def test_format_compact(self):
        """测试format_compact方法"""
        self.assertEqual(self.date.format_compact(), '20250415')
    
    def test_format_slash(self):
        """测试format_slash方法"""
        self.assertEqual(self.date.format_slash(), '2025/04/15')
    
    def test_format_dot(self):
        """测试format_dot方法"""
        self.assertEqual(self.date.format_dot(), '2025.04.15')
    
    def test_format_year_month(self):
        """测试format_year_month方法"""
        self.assertEqual(self.date.format_year_month(), '2025-04')
    
    def test_format_year_month_compact(self):
        """测试format_year_month_compact方法"""
        self.assertEqual(self.date.format_year_month_compact(), '202504')
    
    def test_format_custom(self):
        """测试format_custom方法"""
        self.assertEqual(self.date.format_custom('%Y年%m月'), '2025年04月')


class TestDateArithmetic(unittest.TestCase):
    """测试日期运算"""
    
    def test_add_days(self):
        """测试add_days方法"""
        date = Date('20250415')
        new_date = date.add_days(10)
        self.assertEqual(str(new_date), '20250425')
    
    def test_add_months(self):
        """测试add_months方法"""
        date = Date('202504')
        new_date = date.add_months(2)
        self.assertEqual(str(new_date), '202506')
    
    def test_add_years(self):
        """测试add_years方法"""
        date = Date('2025')
        new_date = date.add_years(1)
        self.assertEqual(str(new_date), '2026')
    
    def test_subtract_days(self):
        """测试subtract_days方法"""
        date = Date('20250415')
        new_date = date.subtract_days(5)
        self.assertEqual(str(new_date), '20250410')
    
    def test_subtract_months(self):
        """测试subtract_months方法"""
        date = Date('202504')
        new_date = date.subtract_months(1)
        self.assertEqual(str(new_date), '202503')
    
    def test_subtract_years(self):
        """测试subtract_years方法"""
        date = Date('2025')
        new_date = date.subtract_years(1)
        self.assertEqual(str(new_date), '2024')
    
    def test_format_preservation(self):
        """测试运算后格式保持"""
        # 年份格式
        year_date = Date('2025')
        self.assertEqual(str(year_date.add_years(1)), '2026')
        
        # 年月格式  
        ym_date = Date('202504')
        self.assertEqual(str(ym_date.add_months(1)), '202505')
        
        # 完整格式
        full_date = Date('20250415')
        self.assertEqual(str(full_date.add_days(1)), '20250416')


class TestDateComparison(unittest.TestCase):
    """测试日期比较"""
    
    def test_equality(self):
        """测试相等比较"""
        date1 = Date('20250415')
        date2 = Date('20250415')
        date3 = Date('20250416')
        
        self.assertEqual(date1, date2)
        self.assertNotEqual(date1, date3)
    
    def test_less_than(self):
        """测试小于比较"""
        date1 = Date('20250415')
        date2 = Date('20250416')
        
        self.assertLess(date1, date2)
        self.assertFalse(date2 < date1)
    
    def test_greater_than(self):
        """测试大于比较"""
        date1 = Date('20250415')
        date2 = Date('20250416')
        
        self.assertGreater(date2, date1)
        self.assertFalse(date1 > date2)
    
    def test_less_equal(self):
        """测试小于等于比较"""
        date1 = Date('20250415')
        date2 = Date('20250415')
        date3 = Date('20250416')
        
        self.assertLessEqual(date1, date2)
        self.assertLessEqual(date1, date3)
    
    def test_greater_equal(self):
        """测试大于等于比较"""
        date1 = Date('20250415')
        date2 = Date('20250415')
        date3 = Date('20250414')
        
        self.assertGreaterEqual(date1, date2)
        self.assertGreaterEqual(date1, date3)
    
    def test_hash(self):
        """测试哈希值"""
        date1 = Date('20250415')
        date2 = Date('20250415')
        
        self.assertEqual(hash(date1), hash(date2))


class TestDateGetters(unittest.TestCase):
    """测试获取方法"""
    
    def setUp(self):
        self.date = Date('20250415')  # 2025年4月15日，星期二
    
    def test_get_weekday(self):
        """测试get_weekday方法"""
        weekday = self.date.get_weekday()
        self.assertEqual(weekday, 1)  # 星期二 = 1
    
    def test_get_isoweekday(self):
        """测试get_isoweekday方法"""
        isoweekday = self.date.get_isoweekday()
        self.assertEqual(isoweekday, 2)  # 星期二 = 2
    
    def test_get_month_start(self):
        """测试get_month_start方法"""
        month_start = self.date.get_month_start()
        self.assertEqual(str(month_start), '20250401')
    
    def test_get_month_end(self):
        """测试get_month_end方法"""
        month_end = self.date.get_month_end()
        self.assertEqual(str(month_end), '20250430')
    
    def test_get_year_start(self):
        """测试get_year_start方法"""
        year_start = self.date.get_year_start()
        self.assertEqual(str(year_start), '20250101')
    
    def test_get_year_end(self):
        """测试get_year_end方法"""
        year_end = self.date.get_year_end()
        self.assertEqual(str(year_end), '20251231')
    
    def test_get_days_in_month(self):
        """测试get_days_in_month方法"""
        days = self.date.get_days_in_month()
        self.assertEqual(days, 30)  # 4月有30天
    
    def test_get_days_in_year(self):
        """测试get_days_in_year方法"""
        days = self.date.get_days_in_year()
        self.assertEqual(days, 365)  # 2025年不是闰年


class TestDatePredicates(unittest.TestCase):
    """测试判断方法"""
    
    def setUp(self):
        self.date = Date('20250415')  # 2025年4月15日，星期二
    
    def test_is_weekend(self):
        """测试is_weekend方法"""
        self.assertFalse(self.date.is_weekend())  # 星期二不是周末
        
        # 测试周末
        saturday = Date('20250419')  # 星期六
        self.assertTrue(saturday.is_weekend())
    
    def test_is_weekday(self):
        """测试is_weekday方法"""
        self.assertTrue(self.date.is_weekday())  # 星期二是工作日
        
        # 测试周末
        sunday = Date('20250420')  # 星期日
        self.assertFalse(sunday.is_weekday())
    
    def test_is_leap_year(self):
        """测试is_leap_year方法"""
        self.assertFalse(self.date.is_leap_year())  # 2025不是闰年
        
        # 测试闰年
        leap_year_date = Date('20240229')  # 2024是闰年
        self.assertTrue(leap_year_date.is_leap_year())
    
    def test_is_month_start(self):
        """测试is_month_start方法"""
        self.assertFalse(self.date.is_month_start())  # 15号不是月初
        
        # 测试月初
        month_start = Date('20250401')
        self.assertTrue(month_start.is_month_start())
    
    def test_is_month_end(self):
        """测试is_month_end方法"""
        self.assertFalse(self.date.is_month_end())  # 15号不是月末
        
        # 测试月末
        month_end = Date('20250430')
        self.assertTrue(month_end.is_month_end())
    
    def test_is_year_start(self):
        """测试is_year_start方法"""
        self.assertFalse(self.date.is_year_start())  # 4月15日不是年初
        
        # 测试年初
        year_start = Date('20250101')
        self.assertTrue(year_start.is_year_start())
    
    def test_is_year_end(self):
        """测试is_year_end方法"""
        self.assertFalse(self.date.is_year_end())  # 4月15日不是年末
        
        # 测试年末
        year_end = Date('20251231')
        self.assertTrue(year_end.is_year_end())


class TestDateConversion(unittest.TestCase):
    """测试转换方法"""
    
    def setUp(self):
        self.date = Date('20250415')
    
    def test_to_tuple(self):
        """测试to_tuple方法"""
        result = self.date.to_tuple()
        self.assertEqual(result, (2025, 4, 15))
    
    def test_to_dict(self):
        """测试to_dict方法"""
        result = self.date.to_dict()
        expected = {'year': 2025, 'month': 4, 'day': 15}
        self.assertEqual(result, expected)
    
    def test_to_date_object(self):
        """测试to_date_object方法"""
        result = self.date.to_date_object()
        expected = datetime.date(2025, 4, 15)
        self.assertEqual(result, expected)
    
    def test_to_datetime_object(self):
        """测试to_datetime_object方法"""
        result = self.date.to_datetime_object()
        expected = datetime.datetime(2025, 4, 15)
        self.assertEqual(result, expected)
    
    def test_to_timestamp(self):
        """测试to_timestamp方法"""
        result = self.date.to_timestamp()
        self.assertIsInstance(result, float)


class TestDateCalculation(unittest.TestCase):
    """测试计算方法"""
    
    def test_calculate_difference_days(self):
        """测试calculate_difference_days方法"""
        date1 = Date('20250415')
        date2 = Date('20250425')
        
        diff = date1.calculate_difference_days(date2)
        self.assertEqual(diff, 10)
        
        # 反向计算
        diff_reverse = date2.calculate_difference_days(date1)
        self.assertEqual(diff_reverse, -10)
    
    def test_calculate_difference_months(self):
        """测试calculate_difference_months方法"""
        date1 = Date('20250415')
        date2 = Date('20250615')
        
        diff = date1.calculate_difference_months(date2)
        self.assertEqual(diff, 2)


class TestBackwardCompatibility(unittest.TestCase):
    """测试向后兼容性"""
    
    def setUp(self):
        self.date = Date('20250415')
    
    def test_old_format_method(self):
        """测试旧的format方法"""
        result = self.date.format('%Y年%m月')
        self.assertEqual(result, '2025年04月')
    
    def test_old_to_date_method(self):
        """测试旧的to_date方法"""
        result = self.date.to_date()
        expected = datetime.date(2025, 4, 15)
        self.assertEqual(result, expected)
    
    def test_old_to_datetime_method(self):
        """测试旧的to_datetime方法"""
        result = self.date.to_datetime()
        expected = datetime.datetime(2025, 4, 15)
        self.assertEqual(result, expected)
    
    def test_old_weekday_method(self):
        """测试旧的weekday方法"""
        result = self.date.weekday()
        self.assertEqual(result, 1)  # 星期二
    
    def test_old_difference_method(self):
        """测试旧的difference方法"""
        other_date = Date('20250425')
        diff = self.date.difference(other_date)
        self.assertEqual(diff, 10)


class TestDateErrorHandling(unittest.TestCase):
    """测试错误处理"""
    
    def test_invalid_string_format(self):
        """测试无效字符串格式"""
        with self.assertRaises(ValueError):
            Date('invalid')
        
        with self.assertRaises(ValueError):
            Date('20251')  # 5位数字
    
    def test_invalid_date_values(self):
        """测试无效日期值"""
        with self.assertRaises(ValueError):
            Date('20250230')  # 2月30日不存在
        
        with self.assertRaises(ValueError):
            Date(2025, 13, 1)  # 13月不存在
        
        with self.assertRaises(ValueError):
            Date(2025, 4, 31)  # 4月31日不存在
    
    def test_invalid_argument_types(self):
        """测试无效参数类型"""
        from staran.date.core import InvalidDateFormatError
        
        with self.assertRaises(InvalidDateFormatError):
            Date([2025, 4, 15])  # 列表不支持
        
        with self.assertRaises(InvalidDateFormatError):
            Date({'year': 2025})  # 字典不支持


if __name__ == '__main__':
    unittest.main(verbosity=2)
