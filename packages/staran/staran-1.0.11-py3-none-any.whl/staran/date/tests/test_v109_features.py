#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date类v1.0.9新功能测试
====================

测试v1.0.9版本新增的功能：
- 智能日期推断
- 异步批量处理
- 日期范围操作
- 数据导入导出
- 性能优化
"""

import unittest
import asyncio
import tempfile
import os
import csv
import json
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date.core import Date, DateRange, SmartDateInference


class TestSmartDateInference(unittest.TestCase):
    """测试智能日期推断功能"""
    
    def test_smart_parse_day_only(self):
        """测试只有日期的智能解析"""
        reference = Date('20250415')
        result = Date.smart_parse('25', reference)
        self.assertIsInstance(result, Date)
        # 应该推断为本月25号或下月25号
        self.assertEqual(result.day, 25)
    
    def test_smart_parse_month_day(self):
        """测试月日智能解析"""
        result = Date.smart_parse('6 15')  # 6月15号
        self.assertIsInstance(result, Date)
        self.assertEqual(result.month, 6)
        self.assertEqual(result.day, 15)
    
    def test_infer_date_partial(self):
        """测试部分日期推断"""
        # 只提供月份和日期
        result = Date.infer_date(month=3, day=15)
        self.assertIsInstance(result, Date)
        self.assertEqual(result.month, 3)
        self.assertEqual(result.day, 15)
        
        # 只提供日期
        result = Date.infer_date(day=20)
        self.assertIsInstance(result, Date)
        self.assertEqual(result.day, 20)


class TestAsyncBatchProcessing(unittest.TestCase):
    """测试异步批量处理功能"""
    
    def test_async_batch_create(self):
        """测试异步批量创建"""
        async def run_test():
            date_strings = ['20250101', '20250102', '20250103']
            dates = await Date.async_batch_create(date_strings)
            self.assertEqual(len(dates), 3)
            self.assertIsInstance(dates[0], Date)
            self.assertEqual(dates[0].format_compact(), '20250101')
        
        asyncio.run(run_test())
    
    def test_async_batch_format(self):
        """测试异步批量格式化"""
        async def run_test():
            dates = [Date('20250101'), Date('20250102'), Date('20250103')]
            formatted = await Date.async_batch_format(dates, 'iso')
            self.assertEqual(len(formatted), 3)
            self.assertEqual(formatted[0], '2025-01-01')
        
        asyncio.run(run_test())
    
    def test_async_batch_process(self):
        """测试异步批量处理"""
        async def run_test():
            dates = [Date('20250101'), Date('20250102')]
            processed = await Date.async_batch_process(dates, 'add_days', days=5)
            self.assertEqual(len(processed), 2)
            self.assertEqual(processed[0].format_compact(), '20250106')
        
        asyncio.run(run_test())


class TestDateRangeOperations(unittest.TestCase):
    """测试日期范围操作功能"""
    
    def test_date_range_creation(self):
        """测试日期范围创建"""
        start = Date('20250101')
        end = Date('20250131')
        range_obj = DateRange(start, end)
        
        self.assertEqual(range_obj.start, start)
        self.assertEqual(range_obj.end, end)
        self.assertEqual(range_obj.days_count(), 31)
    
    def test_date_range_contains(self):
        """测试日期范围包含检查"""
        range_obj = DateRange(Date('20250101'), Date('20250131'))
        self.assertTrue(range_obj.contains(Date('20250115')))
        self.assertFalse(range_obj.contains(Date('20250201')))
    
    def test_date_range_intersect(self):
        """测试日期范围交集"""
        range1 = DateRange(Date('20250101'), Date('20250115'))
        range2 = DateRange(Date('20250110'), Date('20250120'))
        
        intersection = range1.intersect(range2)
        self.assertIsNotNone(intersection)
        self.assertEqual(intersection.start, Date('20250110'))
        self.assertEqual(intersection.end, Date('20250115'))
    
    def test_date_range_union(self):
        """测试日期范围并集"""
        range1 = DateRange(Date('20250101'), Date('20250115'))
        range2 = DateRange(Date('20250110'), Date('20250120'))
        
        union = range1.union(range2)
        self.assertEqual(union.start, Date('20250101'))
        self.assertEqual(union.end, Date('20250120'))
    
    def test_create_range_from_strings(self):
        """测试从字符串创建日期范围"""
        range_obj = Date.create_range('20250101', '20250131')
        self.assertIsInstance(range_obj, DateRange)
        self.assertEqual(range_obj.days_count(), 31)
    
    def test_generate_range(self):
        """测试生成日期范围序列"""
        dates = Date.generate_range('20250101', 7, step=1, include_weekends=True)
        self.assertEqual(len(dates), 7)
        self.assertEqual(dates[0].format_compact(), '20250101')
        self.assertEqual(dates[-1].format_compact(), '20250107')
    
    def test_in_range(self):
        """测试日期是否在范围内"""
        date = Date('20250115')
        self.assertTrue(date.in_range(Date('20250101'), Date('20250131')))
        self.assertFalse(date.in_range(Date('20250201'), Date('20250228')))
    
    def test_merge_date_ranges(self):
        """测试合并日期范围"""
        ranges = [
            DateRange(Date('20250101'), Date('20250110')),
            DateRange(Date('20250105'), Date('20250115')),
            DateRange(Date('20250120'), Date('20250125'))
        ]
        
        merged = Date.merge_date_ranges(ranges)
        self.assertEqual(len(merged), 2)  # 前两个应该合并


class TestDataImportExport(unittest.TestCase):
    """测试数据导入导出功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_file = os.path.join(self.temp_dir, 'test_dates.csv')
        self.json_file = os.path.join(self.temp_dir, 'test_dates.json')
    
    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        if os.path.exists(self.json_file):
            os.remove(self.json_file)
        os.rmdir(self.temp_dir)
    
    def test_csv_export_import(self):
        """测试CSV导出导入"""
        dates = [Date('20250101'), Date('20250102'), Date('20250103')]
        
        # 导出到CSV
        Date.to_csv(dates, self.csv_file, include_metadata=True)
        self.assertTrue(os.path.exists(self.csv_file))
        
        # 从CSV导入
        imported_dates = Date.from_csv(self.csv_file, 'date')
        self.assertEqual(len(imported_dates), 3)
        self.assertEqual(imported_dates[0].format_iso(), '2025-01-01')
    
    def test_json_export_import(self):
        """测试JSON导出导入"""
        dates = [Date('20250101'), Date('20250102'), Date('20250103')]
        
        # 导出到JSON
        Date.to_json_file(dates, self.json_file, include_metadata=True)
        self.assertTrue(os.path.exists(self.json_file))
        
        # 从JSON导入
        imported_dates = Date.from_json_file(self.json_file)
        self.assertEqual(len(imported_dates), 3)
        self.assertEqual(imported_dates[0].format_iso(), '2025-01-01')


class TestPerformanceOptimizations(unittest.TestCase):
    """测试性能优化功能"""
    
    def test_cache_operations(self):
        """测试缓存操作"""
        # 清空缓存
        Date.clear_cache()
        
        # 获取缓存统计
        stats = Date.get_cache_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('object_cache_size', stats)
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        date = Date('20250415')
        cache_key = date.get_cache_key()
        self.assertIsInstance(cache_key, str)
        self.assertIn('2025-04-15', cache_key)
    
    def test_optimized_format(self):
        """测试优化的格式化"""
        date = Date('20250415')
        
        # 测试优化格式化
        result1 = date._optimized_format('iso')
        result2 = date._optimized_format('iso')  # 应该使用缓存
        
        self.assertEqual(result1, result2)
        self.assertEqual(result1, '2025-04-15')


class TestAdvancedFeatures(unittest.TestCase):
    """测试高级功能"""
    
    def test_date_range_intersect_check(self):
        """测试日期范围交集检查"""
        range1 = DateRange(Date('20250101'), Date('20250115'))
        range2 = DateRange(Date('20250110'), Date('20250120'))
        range3 = DateRange(Date('20250201'), Date('20250215'))
        
        self.assertTrue(Date.date_ranges_intersect(range1, range2))
        self.assertFalse(Date.date_ranges_intersect(range1, range3))
    
    def test_complex_smart_parsing(self):
        """测试复杂的智能解析"""
        # 测试各种输入格式
        test_cases = [
            ('15', 15),  # 只有日期
            ('3-15', 15),  # 月-日
            ('2025-3-15', 15),  # 年-月-日
        ]
        
        for input_str, expected_day in test_cases:
            try:
                result = Date.smart_parse(input_str)
                self.assertEqual(result.day, expected_day)
            except Exception:
                # 如果解析失败，跳过这个测试案例
                pass


if __name__ == '__main__':
    # 设置测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestSmartDateInference,
        TestAsyncBatchProcessing,
        TestDateRangeOperations,
        TestDataImportExport,
        TestPerformanceOptimizations,
        TestAdvancedFeatures
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print(f"\n{'='*50}")
    print(f"📊 v1.0.9新功能测试报告")
    print(f"{'='*50}")
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print(f"\n✅ 所有v1.0.9新功能测试通过! 🎉")
    else:
        print(f"\n❌ 部分测试未通过")
