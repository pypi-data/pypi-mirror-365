#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date类完整测试套件
===============

测试staran.tools.date.Date类的所有功能，包括：
- 对象创建和初始化
- API命名规范
- 日期运算
- 格式化输出
- 比较操作
- 错误处理
- 向后兼容性
"""

import unittest
import sys
import os
import datetime
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.tools.date import Date


class TestDateCreation(unittest.TestCase):
    """测试Date对象的创建和初始化"""
    
    def test_create_from_string_yyyymmdd(self):
        """测试从YYYYMMDD字符串创建"""
        d = Date('20250415')
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
        self.assertEqual(d.get_format_type(), 'full')
    
    def test_create_from_string_yyyymm(self):
        """测试从YYYYMM字符串创建"""
        d = Date('202504')
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 1)
        self.assertEqual(d.get_format_type(), 'year_month')
    
    def test_create_from_string_yyyy(self):
        """测试从YYYY字符串创建"""
        d = Date('2025')
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 1)
        self.assertEqual(d.get_format_type(), 'year_only')
    
    def test_create_from_position_args(self):
        """测试从位置参数创建"""
        d = Date(2025, 4, 15)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
        self.assertEqual(d.get_format_type(), 'full')
    
    def test_create_from_keyword_args(self):
        """测试从关键字参数创建"""
        d = Date(year=2025, month=4, day=15)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
        self.assertEqual(d.get_format_type(), 'full')
    
    def test_create_today(self):
        """测试创建今日对象"""
        d = Date()
        today = datetime.date.today()
        self.assertEqual(d.year, today.year)
        self.assertEqual(d.month, today.month)
        self.assertEqual(d.day, today.day)
        self.assertEqual(d.get_format_type(), 'today')
    
    def test_create_from_date_object(self):
        """测试从datetime.date对象创建"""
        date_obj = datetime.date(2025, 4, 15)
        d = Date(date_obj)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
        self.assertEqual(d.get_format_type(), 'date_object')
    
    def test_create_from_datetime_object(self):
        """测试从datetime.datetime对象创建"""
        datetime_obj = datetime.datetime(2025, 4, 15, 10, 30, 0)
        d = Date(datetime_obj)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
        self.assertEqual(d.get_format_type(), 'datetime_object')


class TestDateClassMethods(unittest.TestCase):
    """测试Date类的类方法 (from_* 系列)"""
    
    def test_from_string(self):
        """测试from_string类方法"""
        d = Date.from_string('20250415')
        self.assertEqual(str(d), '20250415')
    
    def test_from_timestamp(self):
        """测试from_timestamp类方法"""
        # 2022-01-01的时间戳
        d = Date.from_timestamp(1640995200)
        self.assertEqual(d.year, 2022)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 1)
    
    def test_from_date_object(self):
        """测试from_date_object类方法"""
        date_obj = datetime.date(2025, 4, 15)
        d = Date.from_date_object(date_obj)
        self.assertEqual(d.year, 2025)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
    
    def test_from_datetime_object(self):
        """测试from_datetime_object类方法"""
        datetime_obj = datetime.datetime(2025, 4, 15, 10, 30)
        d = Date.from_datetime_object(datetime_obj)
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


class TestDateConversion(unittest.TestCase):
    """测试Date对象的转换方法 (to_* 系列)"""
    
    def setUp(self):
        self.date = Date('20250415')
    
    def test_to_tuple(self):
        """测试to_tuple方法"""
        result = self.date.to_tuple()
        self.assertEqual(result, (2025, 4, 15))
        self.assertIsInstance(result, tuple)
    
    def test_to_dict(self):
        """测试to_dict方法"""
        result = self.date.to_dict()
        expected = {
            'year': 2025,
            'month': 4,
            'day': 15,
            'format_type': 'full'
        }
        self.assertEqual(result, expected)
        self.assertIsInstance(result, dict)
    
    def test_to_date_object(self):
        """测试to_date_object方法"""
        result = self.date.to_date_object()
        expected = datetime.date(2025, 4, 15)
        self.assertEqual(result, expected)
        self.assertIsInstance(result, datetime.date)
    
    def test_to_datetime_object(self):
        """测试to_datetime_object方法"""
        result = self.date.to_datetime_object()
        expected = datetime.datetime(2025, 4, 15)
        self.assertEqual(result, expected)
        self.assertIsInstance(result, datetime.datetime)
    
    def test_to_timestamp(self):
        """测试to_timestamp方法"""
        result = self.date.to_timestamp()
        self.assertIsInstance(result, float)
        # 验证时间戳可以转换回正确的日期
        dt = datetime.datetime.fromtimestamp(result)
        self.assertEqual(dt.year, 2025)
        self.assertEqual(dt.month, 4)
        self.assertEqual(dt.day, 15)


class TestDateFormatting(unittest.TestCase):
    """测试Date对象的格式化方法 (format_* 系列)"""
    
    def setUp(self):
        self.date = Date('20250415')
    
    def test_format_default(self):
        """测试format_default方法"""
        result = self.date.format_default()
        self.assertEqual(result, '20250415')
    
    def test_format_iso(self):
        """测试format_iso方法"""
        result = self.date.format_iso()
        self.assertEqual(result, '2025-04-15')
    
    def test_format_chinese(self):
        """测试format_chinese方法"""
        result = self.date.format_chinese()
        self.assertEqual(result, '2025年04月15日')
    
    def test_format_compact(self):
        """测试format_compact方法"""
        result = self.date.format_compact()
        self.assertEqual(result, '20250415')
    
    def test_format_slash(self):
        """测试format_slash方法"""
        result = self.date.format_slash()
        self.assertEqual(result, '2025/04/15')
    
    def test_format_dot(self):
        """测试format_dot方法"""
        result = self.date.format_dot()
        self.assertEqual(result, '2025.04.15')
    
    def test_format_custom(self):
        """测试format_custom方法"""
        result = self.date.format_custom('%Y-%m')
        self.assertEqual(result, '2025-04')
    
    def test_format_year_month(self):
        """测试format_year_month方法"""
        result = self.date.format_year_month()
        self.assertEqual(result, '2025-04')
    
    def test_format_year_month_compact(self):
        """测试format_year_month_compact方法"""
        result = self.date.format_year_month_compact()
        self.assertEqual(result, '202504')


class TestDateGetters(unittest.TestCase):
    """测试Date对象的获取方法 (get_* 系列)"""
    
    def setUp(self):
        self.date = Date('20250415')  # 2025年4月15日，星期二
    
    def test_get_weekday(self):
        """测试get_weekday方法"""
        result = self.date.get_weekday()
        self.assertEqual(result, 1)  # 星期二 = 1 (Monday=0)
    
    def test_get_isoweekday(self):
        """测试get_isoweekday方法"""
        result = self.date.get_isoweekday()
        self.assertEqual(result, 2)  # 星期二 = 2 (Monday=1)
    
    def test_get_days_in_month(self):
        """测试get_days_in_month方法"""
        result = self.date.get_days_in_month()
        self.assertEqual(result, 30)  # 4月有30天
    
    def test_get_days_in_year(self):
        """测试get_days_in_year方法"""
        result = self.date.get_days_in_year()
        self.assertEqual(result, 365)  # 2025年不是闰年
    
    def test_get_month_start(self):
        """测试get_month_start方法"""
        result = self.date.get_month_start()
        self.assertEqual(str(result), '20250401')
    
    def test_get_month_end(self):
        """测试get_month_end方法"""
        result = self.date.get_month_end()
        self.assertEqual(str(result), '20250430')
    
    def test_get_year_start(self):
        """测试get_year_start方法"""
        result = self.date.get_year_start()
        self.assertEqual(str(result), '20250101')
    
    def test_get_year_end(self):
        """测试get_year_end方法"""
        result = self.date.get_year_end()
        self.assertEqual(str(result), '20251231')


class TestDatePredicates(unittest.TestCase):
    """测试Date对象的判断方法 (is_* 系列)"""
    
    def test_is_weekend(self):
        """测试is_weekend方法"""
        # 星期二
        weekday = Date('20250415')
        self.assertFalse(weekday.is_weekend())
        
        # 星期六
        saturday = Date('20250419')
        self.assertTrue(saturday.is_weekend())
        
        # 星期日
        sunday = Date('20250420')
        self.assertTrue(sunday.is_weekend())
    
    def test_is_weekday(self):
        """测试is_weekday方法"""
        weekday = Date('20250415')  # 星期二
        saturday = Date('20250419')  # 星期六
        
        self.assertTrue(weekday.is_weekday())
        self.assertFalse(saturday.is_weekday())
    
    def test_is_leap_year(self):
        """测试is_leap_year方法"""
        # 2024是闰年
        leap_year = Date('20240101')
        self.assertTrue(leap_year.is_leap_year())
        
        # 2025不是闰年
        non_leap_year = Date('20250101')
        self.assertFalse(non_leap_year.is_leap_year())
    
    def test_is_month_start(self):
        """测试is_month_start方法"""
        month_start = Date('20250401')
        not_month_start = Date('20250415')
        
        self.assertTrue(month_start.is_month_start())
        self.assertFalse(not_month_start.is_month_start())
    
    def test_is_month_end(self):
        """测试is_month_end方法"""
        month_end = Date('20250430')
        not_month_end = Date('20250415')
        
        self.assertTrue(month_end.is_month_end())
        self.assertFalse(not_month_end.is_month_end())
    
    def test_is_year_start(self):
        """测试is_year_start方法"""
        year_start = Date('20250101')
        not_year_start = Date('20250415')
        
        self.assertTrue(year_start.is_year_start())
        self.assertFalse(not_year_start.is_year_start())
    
    def test_is_year_end(self):
        """测试is_year_end方法"""
        year_end = Date('20251231')
        not_year_end = Date('20250415')
        
        self.assertTrue(year_end.is_year_end())
        self.assertFalse(not_year_end.is_year_end())


class TestDateArithmetic(unittest.TestCase):
    """测试Date对象的运算方法"""
    
    def setUp(self):
        self.date = Date('20250415')
    
    def test_add_days(self):
        """测试add_days方法"""
        result = self.date.add_days(10)
        self.assertEqual(str(result), '20250425')
        
        # 测试负数
        result = self.date.add_days(-5)
        self.assertEqual(str(result), '20250410')
    
    def test_add_months(self):
        """测试add_months方法"""
        result = self.date.add_months(2)
        self.assertEqual(str(result), '20250615')
        
        # 测试负数
        result = self.date.add_months(-2)
        self.assertEqual(str(result), '20250215')
    
    def test_add_years(self):
        """测试add_years方法"""
        result = self.date.add_years(1)
        self.assertEqual(str(result), '20260415')
        
        # 测试负数
        result = self.date.add_years(-1)
        self.assertEqual(str(result), '20240415')
    
    def test_subtract_days(self):
        """测试subtract_days方法"""
        result = self.date.subtract_days(10)
        self.assertEqual(str(result), '20250405')
    
    def test_subtract_months(self):
        """测试subtract_months方法"""
        result = self.date.subtract_months(2)
        self.assertEqual(str(result), '20250215')
    
    def test_subtract_years(self):
        """测试subtract_years方法"""
        result = self.date.subtract_years(1)
        self.assertEqual(str(result), '20240415')
    
    def test_format_preservation(self):
        """测试运算后格式保持"""
        # 年月格式
        ym_date = Date('202504')
        result = ym_date.add_months(2)
        self.assertEqual(str(result), '202506')
        
        # 完整格式
        full_date = Date('20250415')
        result = full_date.add_days(10)
        self.assertEqual(str(result), '20250425')


class TestDateComparison(unittest.TestCase):
    """测试Date对象的比较操作"""
    
    def setUp(self):
        self.date1 = Date('20250415')
        self.date2 = Date('20250420')
        self.date3 = Date('20250415')
    
    def test_equality(self):
        """测试相等比较"""
        self.assertTrue(self.date1 == self.date3)
        self.assertFalse(self.date1 == self.date2)
    
    def test_less_than(self):
        """测试小于比较"""
        self.assertTrue(self.date1 < self.date2)
        self.assertFalse(self.date2 < self.date1)
        self.assertFalse(self.date1 < self.date3)
    
    def test_less_equal(self):
        """测试小于等于比较"""
        self.assertTrue(self.date1 <= self.date2)
        self.assertTrue(self.date1 <= self.date3)
        self.assertFalse(self.date2 <= self.date1)
    
    def test_greater_than(self):
        """测试大于比较"""
        self.assertTrue(self.date2 > self.date1)
        self.assertFalse(self.date1 > self.date2)
        self.assertFalse(self.date1 > self.date3)
    
    def test_greater_equal(self):
        """测试大于等于比较"""
        self.assertTrue(self.date2 >= self.date1)
        self.assertTrue(self.date1 >= self.date3)
        self.assertFalse(self.date1 >= self.date2)
    
    def test_hash(self):
        """测试哈希值"""
        self.assertEqual(hash(self.date1), hash(self.date3))
        self.assertNotEqual(hash(self.date1), hash(self.date2))


class TestDateCalculation(unittest.TestCase):
    """测试Date对象的计算方法"""
    
    def setUp(self):
        self.date1 = Date('20250415')
        self.date2 = Date('20250420')
    
    def test_calculate_difference_days(self):
        """测试calculate_difference_days方法"""
        diff = self.date2.calculate_difference_days(self.date1)
        self.assertEqual(diff, 5)
        
        # 反向计算
        diff = self.date1.calculate_difference_days(self.date2)
        self.assertEqual(diff, -5)
    
    def test_calculate_difference_months(self):
        """测试calculate_difference_months方法"""
        date1 = Date('20250415')
        date2 = Date('20250615')
        
        diff = date2.calculate_difference_months(date1)
        self.assertEqual(diff, 2)
        
        # 反向计算
        diff = date1.calculate_difference_months(date2)
        self.assertEqual(diff, -2)


class TestDateErrorHandling(unittest.TestCase):
    """测试Date对象的错误处理"""
    
    def test_invalid_string_format(self):
        """测试无效字符串格式"""
        with self.assertRaises(ValueError):
            Date('invalid')
        
        with self.assertRaises(ValueError):
            Date('12345')  # 5位数字
        
        with self.assertRaises(ValueError):
            Date('123456789')  # 9位数字
    
    def test_invalid_date_values(self):
        """测试无效日期值"""
        with self.assertRaises(ValueError):
            Date(2025, 13, 1)  # 无效月份
        
        with self.assertRaises(ValueError):
            Date(2025, 4, 31)  # 4月没有31日
        
        with self.assertRaises(ValueError):
            Date(2025, 2, 29)  # 2025年2月没有29日
    
    def test_invalid_argument_types(self):
        """测试无效参数类型"""
        with self.assertRaises(TypeError):
            Date(['invalid'])
        
        with self.assertRaises(ValueError):
            Date(year=2025)  # 缺少month参数


class TestBackwardCompatibility(unittest.TestCase):
    """测试向后兼容性"""
    
    def setUp(self):
        self.date = Date('20250415')
    
    def test_old_format_method(self):
        """测试旧的format方法"""
        result = self.date.format('%Y-%m-%d')
        self.assertEqual(result, '2025-04-15')
    
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
        self.assertEqual(result, 1)
    
    def test_old_difference_method(self):
        """测试旧的difference方法"""
        other = Date('20250420')
        result = other.difference(self.date)
        self.assertEqual(result, 5)


if __name__ == '__main__':
    # 设置日志级别为WARNING，避免测试时的日志干扰
    Date.set_log_level(logging.WARNING)
    
    # 运行测试
    unittest.main(verbosity=2)
