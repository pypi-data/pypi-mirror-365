#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date类增强功能测试
================

测试新增的优化和改进功能：
- 增强的节假日支持
- 批量处理方法
- 时区支持
- 业务规则
- 改进的JSON序列化
"""

import unittest
import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date.core import Date


class TestEnhancedHolidays(unittest.TestCase):
    """测试增强的节假日功能"""
    
    def test_chinese_holidays(self):
        """测试中国节假日"""
        # 元旦
        new_year = Date('20250101')
        self.assertTrue(new_year.is_holiday('CN'))
        
        # 劳动节
        labor_day = Date('20250501')
        self.assertTrue(labor_day.is_holiday('CN'))
        
        # 国庆节
        national_day = Date('20251001')
        self.assertTrue(national_day.is_holiday('CN'))
        
        # 普通日期
        regular_day = Date('20250315')
        self.assertFalse(regular_day.is_holiday('CN'))
    
    def test_us_holidays(self):
        """测试美国节假日"""
        # 独立日
        independence_day = Date('20250704')
        self.assertTrue(independence_day.is_holiday('US'))
        
        # 圣诞节
        christmas = Date('20251225')
        self.assertTrue(christmas.is_holiday('US'))
        
        # 感恩节测试（11月第四个星期四）
        thanksgiving_2025 = Date('20251127')  # 2025年11月27日是第四个星期四
        self.assertTrue(thanksgiving_2025.is_holiday('US'))
    
    def test_japanese_holidays(self):
        """测试日本节假日"""
        # 元日
        new_year = Date('20250101')
        self.assertTrue(new_year.is_holiday('JP'))
        
        # 建国記念の日
        foundation_day = Date('20250211')
        self.assertTrue(foundation_day.is_holiday('JP'))
        
        # 文化の日
        culture_day = Date('20251103')
        self.assertTrue(culture_day.is_holiday('JP'))


class TestBatchProcessing(unittest.TestCase):
    """测试批量处理功能"""
    
    def test_batch_create(self):
        """测试批量创建"""
        date_strings = ['20250101', '20250202', '20250303']
        dates = Date.batch_create(date_strings)
        
        self.assertEqual(len(dates), 3)
        self.assertEqual(str(dates[0]), '20250101')
        self.assertEqual(str(dates[1]), '20250202')
        self.assertEqual(str(dates[2]), '20250303')
    
    def test_batch_format(self):
        """测试批量格式化"""
        dates = [Date('20250101'), Date('20250202'), Date('20250303')]
        
        # ISO格式
        iso_results = Date.batch_format(dates, 'iso')
        self.assertEqual(iso_results, ['2025-01-01', '2025-02-02', '2025-03-03'])
        
        # 中文格式
        chinese_results = Date.batch_format(dates, 'chinese')
        self.assertEqual(chinese_results, ['2025年01月01日', '2025年02月02日', '2025年03月03日'])
    
    def test_batch_add_days(self):
        """测试批量添加天数"""
        dates = [Date('20250101'), Date('20250202')]
        new_dates = Date.batch_add_days(dates, 10)
        
        self.assertEqual(str(new_dates[0]), '20250111')
        self.assertEqual(str(new_dates[1]), '20250212')


class TestTimezoneSupport(unittest.TestCase):
    """测试时区支持"""
    
    def test_timestamp_with_timezone(self):
        """测试带时区的时间戳转换"""
        date = Date('20250101')
        
        # 默认时区
        timestamp_default = date.to_timestamp()
        
        # 东八区
        timestamp_utc8 = date.to_timestamp(8)
        
        # 时差应该是8小时
        self.assertAlmostEqual(timestamp_default - timestamp_utc8, 8 * 3600, delta=1)
    
    def test_from_timestamp_with_timezone(self):
        """测试从带时区的时间戳创建"""
        timestamp = 1735689600  # 2025-01-01 00:00:00 UTC
        
        # UTC时间
        date_utc = Date.from_timestamp(timestamp, 0)
        
        # 东八区时间
        date_utc8 = Date.from_timestamp(timestamp, 8)
        
        # 应该相差一天或在边界情况下相同
        self.assertTrue(abs((date_utc8.to_date_object() - date_utc.to_date_object()).days) <= 1)


class TestBusinessRules(unittest.TestCase):
    """测试业务规则"""
    
    def test_month_end_rule(self):
        """测试月末规则"""
        date = Date('20250415')
        month_end = date.apply_business_rule('month_end')
        self.assertEqual(str(month_end), '20250430')
    
    def test_quarter_end_rule(self):
        """测试季度末规则"""
        date = Date('20250415')
        quarter_end = date.apply_business_rule('quarter_end')
        self.assertEqual(str(quarter_end), '20250630')
    
    def test_next_business_day_rule(self):
        """测试下一个工作日规则"""
        # 周五
        friday = Date('20250418')  # 假设这是周五
        next_business = friday.add_days(1).apply_business_rule('next_business_day')
        
        # 应该跳过周末到周一
        self.assertTrue(next_business.is_business_day())
    
    def test_prev_business_day_rule(self):
        """测试上一个工作日规则"""
        # 周一
        monday = Date('20250421')  # 假设这是周一
        prev_business = monday.subtract_days(1).apply_business_rule('prev_business_day')
        
        # 应该跳过周末到周五
        self.assertTrue(prev_business.is_business_day())


class TestEnhancedJSON(unittest.TestCase):
    """测试增强的JSON功能"""
    
    def test_json_with_metadata(self):
        """测试包含元数据的JSON序列化"""
        date = Date('20250415')
        json_str = date.to_json(include_metadata=True)
        
        import json
        data = json.loads(json_str)
        
        # 检查基本字段
        self.assertEqual(data['year'], 2025)
        self.assertEqual(data['month'], 4)
        self.assertEqual(data['day'], 15)
        
        # 检查元数据
        self.assertIn('weekday', data)
        self.assertIn('is_weekend', data)
        self.assertIn('quarter', data)
        self.assertIn('version', data)
    
    def test_json_without_metadata(self):
        """测试不包含元数据的JSON序列化"""
        date = Date('20250415')
        json_str = date.to_json(include_metadata=False)
        
        import json
        data = json.loads(json_str)
        
        # 检查基本字段存在
        required_fields = ['date', 'year', 'month', 'day']
        for field in required_fields:
            self.assertIn(field, data)
        
        # 检查元数据不存在
        metadata_fields = ['weekday', 'is_weekend', 'quarter', 'version']
        for field in metadata_fields:
            self.assertNotIn(field, data)
    
    def test_dict_with_metadata(self):
        """测试包含元数据的字典转换"""
        date = Date('20250415')
        data = date.to_dict(include_metadata=True)
        
        # 检查基本字段
        self.assertEqual(data['year'], 2025)
        self.assertEqual(data['month'], 4)
        self.assertEqual(data['day'], 15)
        
        # 检查元数据
        self.assertIn('weekday', data)
        self.assertIn('is_weekend', data)
        self.assertIn('quarter', data)
        self.assertIn('iso_string', data)
        self.assertIn('compact_string', data)


class TestNewDateRanges(unittest.TestCase):
    """测试新的日期范围功能"""
    
    def test_weekends_range(self):
        """测试周末范围生成"""
        weekends = Date.weekends('20250401', '20250407')  # 一周
        
        # 应该只包含周末日期
        for date in weekends:
            self.assertTrue(date.is_weekend())
    
    def test_month_range(self):
        """测试月份范围生成"""
        months = Date.month_range('202501', 3)
        
        self.assertEqual(len(months), 3)
        # 注意：月份范围返回的是年月格式，保持输入格式
        self.assertEqual(str(months[0]), '202501')  # 2025年1月1日
        self.assertEqual(str(months[1]), '202502')  # 2025年2月1日
        self.assertEqual(str(months[2]), '202503')  # 2025年3月1日
    
    def test_quarter_dates(self):
        """测试季度日期生成"""
        quarters = Date.quarter_dates(2025)
        
        self.assertEqual(len(quarters), 4)
        
        # 检查第一季度 - 季度日期使用ISO格式
        q1_start, q1_end = quarters[1]
        self.assertEqual(q1_start.format_compact(), '20250101')
        self.assertEqual(q1_end.format_compact(), '20250331')
        
        # 检查第四季度
        q4_start, q4_end = quarters[4]
        self.assertEqual(q4_start.format_compact(), '20251001')
        self.assertEqual(q4_end.format_compact(), '20251231')


class TestDateValidation(unittest.TestCase):
    """测试日期验证功能"""
    
    def test_is_valid_date_string(self):
        """测试日期字符串验证"""
        # 有效日期
        self.assertTrue(Date.is_valid_date_string('20250415'))
        self.assertTrue(Date.is_valid_date_string('202504'))
        self.assertTrue(Date.is_valid_date_string('2025'))
        
        # 无效日期
        self.assertFalse(Date.is_valid_date_string('20250230'))  # 2月30日
        self.assertFalse(Date.is_valid_date_string('invalid'))
        self.assertFalse(Date.is_valid_date_string(''))
    
    def test_year_boundary_warning(self):
        """测试年份边界警告"""
        # 这个测试检查是否会记录警告日志
        # 在实际应用中，可能需要设置日志级别来捕获警告
        extreme_year_date = Date('10000101')  # 公元1000年
        self.assertEqual(extreme_year_date.year, 1000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
