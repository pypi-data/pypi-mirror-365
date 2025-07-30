#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date类v1.0.10新功能测试
======================

测试v1.0.10版本新增的功能：
- 时区支持
- 日期表达式解析
- 二十四节气
- 数据可视化
- 增强日期范围操作
"""

import unittest
import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date.core.core import Date, DateRange
from staran.date import get_version_info, parse_expression

class TestV1010TimezoneSupport(unittest.TestCase):
    """测试时区支持功能"""
    
    def setUp(self):
        self.date = Date("2025-07-29")
    
    def test_get_supported_timezones(self):
        """测试获取支持的时区"""
        try:
            timezones = Date.get_supported_timezones()
            self.assertIsInstance(timezones, list)
            if timezones:  # 如果功能可用
                self.assertIn('UTC', timezones)
                self.assertIn('UTC+8', timezones)
        except NotImplementedError:
            self.skipTest("时区功能不可用")
    
    def test_get_timezone_info(self):
        """测试获取时区信息"""
        try:
            tz_info = self.date.get_timezone_info('UTC+8')
            self.assertIsInstance(tz_info, dict)
            self.assertIn('name', tz_info)
            self.assertIn('current_offset', tz_info)
            self.assertIn('offset_string', tz_info)
        except NotImplementedError:
            self.skipTest("时区功能不可用")
    
    def test_timezone_conversion(self):
        """测试时区转换"""
        try:
            time_part = datetime.time(12, 0, 0)
            result = self.date.to_timezone('UTC+8', time_part)
            self.assertIsInstance(result, datetime.datetime)
            self.assertEqual(result.date(), self.date.to_date_object())
        except NotImplementedError:
            self.skipTest("时区功能不可用")

class TestV1010ExpressionParsing(unittest.TestCase):
    """测试日期表达式解析功能"""
    
    def test_simple_expressions(self):
        """测试简单表达式"""
        try:
            # 基本表达式
            today = Date.today()
            
            tomorrow = parse_expression("明天")
            if tomorrow:  # 如果功能可用
                expected_tomorrow = today.add_days(1)
                self.assertEqual(tomorrow.to_date_object(), expected_tomorrow.to_date_object())
            
            yesterday = parse_expression("昨天")
            if yesterday:
                expected_yesterday = today.add_days(-1)
                self.assertEqual(yesterday.to_date_object(), expected_yesterday.to_date_object())
        except NotImplementedError:
            self.skipTest("表达式解析功能不可用")
    
    def test_detailed_parsing(self):
        """测试详细解析"""
        try:
            result = Date.parse_expression_detailed("明天")
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
            self.assertIn('confidence', result)
            self.assertIn('matched_pattern', result)
        except NotImplementedError:
            self.skipTest("表达式解析功能不可用")
    
    def test_expression_matching(self):
        """测试表达式匹配"""
        try:
            today = Date.today()
            self.assertTrue(today.matches_expression("今天"))
        except NotImplementedError:
            self.skipTest("表达式解析功能不可用")

class TestV1010SolarTerms(unittest.TestCase):
    """测试二十四节气功能"""
    
    def setUp(self):
        self.date = Date("2025-07-29")
        self.year = 2025
    
    def test_get_year_solar_terms(self):
        """测试获取年份节气"""
        try:
            terms = Date.get_year_solar_terms(self.year)
            self.assertIsInstance(terms, list)
            if terms:  # 如果功能可用
                self.assertEqual(len(terms), 24)
                # 检查第一个节气
                first_term = terms[0]
                self.assertEqual(first_term.name, '立春')
        except NotImplementedError:
            self.skipTest("节气功能不可用")
    
    def test_get_season_solar_terms(self):
        """测试获取季节节气"""
        try:
            spring_terms = Date.get_season_solar_terms(self.year, '春季')
            self.assertIsInstance(spring_terms, list)
            if spring_terms:  # 如果功能可用
                self.assertEqual(len(spring_terms), 6)
                self.assertEqual(spring_terms[0].name, '立春')
        except NotImplementedError:
            self.skipTest("节气功能不可用")
    
    def test_solar_term_queries(self):
        """测试节气查询"""
        try:
            # 获取当前最近节气
            current_term = self.date.get_solar_term()
            if current_term:  # 如果功能可用
                self.assertIsNotNone(current_term.name)
                self.assertIsNotNone(current_term.season)
            
            # 获取下一个节气
            next_term = self.date.get_next_solar_term()
            if next_term:
                self.assertIsNotNone(next_term.name)
            
            # 获取上一个节气
            prev_term = self.date.get_previous_solar_term()
            if prev_term:
                self.assertIsNotNone(prev_term.name)
            
            # 到下个节气的天数
            days = self.date.days_to_next_solar_term()
            self.assertIsInstance(days, int)
            self.assertGreaterEqual(days, 0)
            
        except NotImplementedError:
            self.skipTest("节气功能不可用")
    
    def test_is_solar_term(self):
        """测试是否节气日"""
        try:
            is_term = self.date.is_solar_term()
            self.assertIsInstance(is_term, bool)
        except NotImplementedError:
            self.skipTest("节气功能不可用")
    
    def test_solar_term_season(self):
        """测试获取节气季节"""
        try:
            season = self.date.get_solar_term_season()
            self.assertIsInstance(season, str)
        except NotImplementedError:
            self.skipTest("节气功能不可用")

class TestV1010Visualization(unittest.TestCase):
    """测试数据可视化功能"""
    
    def setUp(self):
        self.dates = [Date("2025-07-29"), Date("2025-07-30"), Date("2025-07-31")]
        self.events = ["事件1", "事件2", "事件3"]
    
    def test_create_timeline_chart(self):
        """测试创建时间轴图表"""
        try:
            from staran.date import create_timeline_chart
            chart_data = create_timeline_chart(self.dates, self.events, 'echarts')
            
            self.assertIsNotNone(chart_data)
            self.assertEqual(chart_data.chart_type, 'timeline')
            self.assertEqual(chart_data.library, 'echarts')
            self.assertIsInstance(chart_data.data, list)
        except (NotImplementedError, ImportError):
            self.skipTest("可视化功能不可用")
    
    def test_create_calendar_heatmap(self):
        """测试创建日历热力图"""
        try:
            date_values = {
                Date("2025-07-29"): 85,
                Date("2025-07-30"): 92,
                Date("2025-07-31"): 78
            }
            
            chart_data = Date.create_calendar_heatmap(date_values, 2025, 'echarts')
            
            self.assertIsNotNone(chart_data)
            self.assertEqual(chart_data.chart_type, 'calendar_heatmap')
            self.assertEqual(chart_data.library, 'echarts')
        except NotImplementedError:
            self.skipTest("可视化功能不可用")
    
    def test_create_time_series_chart(self):
        """测试创建时间序列图"""
        try:
            time_series_data = [
                (Date("2025-07-29"), 100),
                (Date("2025-07-30"), 120),
                (Date("2025-07-31"), 95)
            ]
            
            chart_data = Date.create_time_series_chart(time_series_data, 'echarts')
            
            self.assertIsNotNone(chart_data)
            self.assertEqual(chart_data.chart_type, 'time_series')
            self.assertEqual(chart_data.library, 'echarts')
        except NotImplementedError:
            self.skipTest("可视化功能不可用")
    
    def test_create_date_distribution_chart(self):
        """测试创建日期分布图"""
        try:
            chart_data = Date.create_date_distribution_chart(self.dates, 'month', 'echarts')
            
            self.assertIsNotNone(chart_data)
            self.assertEqual(chart_data.chart_type, 'distribution')
            self.assertEqual(chart_data.library, 'echarts')
        except NotImplementedError:
            self.skipTest("可视化功能不可用")

class TestV1010EnhancedDateRanges(unittest.TestCase):
    """测试增强的日期范围功能"""
    
    def setUp(self):
        self.start_date = Date("2025-07-29")
        self.end_date = Date("2025-08-15")
    
    def test_create_range_to(self):
        """测试创建到指定日期的范围"""
        date_range = self.start_date.create_range_to(self.end_date)
        
        self.assertIsInstance(date_range, DateRange)
        self.assertEqual(date_range.start, self.start_date)
        self.assertEqual(date_range.end, self.end_date)
    
    def test_create_range_with_days(self):
        """测试创建指定天数的范围"""
        # 未来10天
        future_range = self.start_date.create_range_with_days(10)
        self.assertEqual(future_range.start, self.start_date)
        self.assertEqual(future_range.end, self.start_date.add_days(10))
        
        # 过去5天
        past_range = self.start_date.create_range_with_days(-5)
        self.assertEqual(past_range.start, self.start_date.add_days(-5))
        self.assertEqual(past_range.end, self.start_date)
    
    def test_in_range(self):
        """测试是否在范围内"""
        test_date = Date("2025-08-01")
        
        # 在范围内
        self.assertTrue(test_date.in_range(self.start_date, self.end_date))
        
        # 不在范围内
        out_of_range_date = Date("2025-09-01")
        self.assertFalse(out_of_range_date.in_range(self.start_date, self.end_date))
    
    def test_create_date_sequence(self):
        """测试创建日期序列"""
        sequence = Date.create_date_sequence(self.start_date, self.start_date.add_days(6), 2)
        
        self.assertIsInstance(sequence, list)
        self.assertEqual(len(sequence), 4)  # 0, 2, 4, 6天
        self.assertEqual(sequence[0], self.start_date)
        self.assertEqual(sequence[1], self.start_date.add_days(2))
    
    def test_find_common_dates(self):
        """测试查找共同日期"""
        list1 = [Date("2025-07-29"), Date("2025-07-30"), Date("2025-07-31")]
        list2 = [Date("2025-07-30"), Date("2025-07-31"), Date("2025-08-01")]
        list3 = [Date("2025-07-31"), Date("2025-08-01"), Date("2025-08-02")]
        
        common_dates = Date.find_common_dates([list1, list2, list3])
        
        self.assertIsInstance(common_dates, list)
        self.assertEqual(len(common_dates), 1)
        self.assertEqual(common_dates[0], Date("2025-07-31"))

class TestV1010UtilityMethods(unittest.TestCase):
    """测试v1.0.10实用工具方法"""
    
    def setUp(self):
        self.date = Date("2025-07-29")
    
    def test_get_version_info(self):
        """测试获取版本信息"""
        version_info = self.date.get_version_info()
        
        self.assertIsInstance(version_info, dict)
        self.assertIn('version', version_info)
        self.assertEqual(version_info['version'], '1.0.10')
        self.assertIn('enhanced_features', version_info)
        self.assertIn('available_modules', version_info)
        self.assertIn('api_count', version_info)
    
    def test_get_feature_status(self):
        """测试获取功能状态"""
        feature_status = Date.get_feature_status()
        
        self.assertIsInstance(feature_status, dict)
        self.assertIn('core_date_operations', feature_status)
        self.assertTrue(feature_status['core_date_operations'])
        self.assertIn('lunar_calendar', feature_status)
        self.assertTrue(feature_status['lunar_calendar'])
        self.assertIn('multilingual_support', feature_status)
        self.assertTrue(feature_status['multilingual_support'])
    
    def test_help_system(self):
        """测试帮助系统"""
        # 测试创建方法帮助
        help_creation = self.date.help('creation')
        self.assertIsInstance(help_creation, str)
        self.assertIn('Date', help_creation)
        
        # 测试格式化帮助
        help_formatting = self.date.help('formatting')
        self.assertIsInstance(help_formatting, str)
        self.assertIn('format', help_formatting)
        
        # 测试计算帮助
        help_calculations = self.date.help('calculations')
        self.assertIsInstance(help_calculations, str)
        self.assertIn('add_days', help_calculations)
        
        # 测试全部帮助
        help_all = self.date.help('all')
        self.assertIsInstance(help_all, str)
        self.assertIn('Date', help_all)

class TestV1010Integration(unittest.TestCase):
    """测试v1.0.10集成功能"""
    
    def test_version_consistency(self):
        """测试版本一致性"""
        from staran.date import __version__, get_version_info
        
        # 检查模块版本
        self.assertEqual(__version__, "1.0.10")
        
        # 检查版本信息函数
        version_info = get_version_info()
        self.assertEqual(version_info['version'], "1.0.10")
    
    def test_backwards_compatibility(self):
        """测试向后兼容性"""
        # 确保所有v1.0.8和v1.0.9的功能仍然可用
        date = Date("2025-07-29")
        
        # 基础功能
        self.assertEqual(date.format_iso(), "2025-07-29")
        self.assertEqual(date.format_chinese(), "2025年07月29日")
        
        # 农历功能
        lunar = date.to_lunar()
        self.assertIsNotNone(lunar)
        
        # 多语言功能
        Date.set_language('zh_CN')
        localized = date.format_localized()
        self.assertIsInstance(localized, str)
        
        # 计算功能
        tomorrow = date.add_days(1)
        self.assertEqual(tomorrow.to_date_object(), datetime.date(2025, 7, 30))
    
    def test_api_count_increase(self):
        """测试API数量增加"""
        date = Date("2025-07-29")
        version_info = date.get_version_info()
        
        # v1.0.10应该比之前版本有更多API
        api_count = version_info['api_count']
        self.assertGreater(api_count, 120)  # 应该超过120个API方法

# 测试运行器
class TestV1010Runner:
    """v1.0.10测试运行器"""
    
    @staticmethod
    def run_all_tests():
        """运行所有v1.0.10测试"""
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # 添加所有测试类
        test_classes = [
            TestV1010TimezoneSupport,
            TestV1010ExpressionParsing,
            TestV1010SolarTerms,
            TestV1010Visualization,
            TestV1010EnhancedDateRanges,
            TestV1010UtilityMethods,
            TestV1010Integration
        ]
        
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result
    
    @staticmethod
    def run_specific_test(test_class_name: str):
        """运行特定测试类"""
        test_classes = {
            'timezone': TestV1010TimezoneSupport,
            'expressions': TestV1010ExpressionParsing,
            'solar_terms': TestV1010SolarTerms,
            'visualization': TestV1010Visualization,
            'ranges': TestV1010EnhancedDateRanges,
            'utilities': TestV1010UtilityMethods,
            'integration': TestV1010Integration
        }
        
        test_class = test_classes.get(test_class_name)
        if test_class:
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2)
            return runner.run(suite)
        else:
            print(f"测试类 '{test_class_name}' 不存在")
            print(f"可用的测试类: {list(test_classes.keys())}")

if __name__ == "__main__":
    print("🧪 Staran v1.0.10 新功能测试")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        print(f"运行特定测试: {test_name}")
        TestV1010Runner.run_specific_test(test_name)
    else:
        print("运行所有v1.0.10新功能测试")
        result = TestV1010Runner.run_all_tests()
        
        # 输出结果摘要
        print(f"\n" + "=" * 50)
        print(f"测试摘要:")
        print(f"  运行测试数: {result.testsRun}")
        print(f"  失败数: {len(result.failures)}")
        print(f"  错误数: {len(result.errors)}")
        print(f"  跳过数: {len(result.skipped)}")
        
        if result.failures:
            print(f"\n失败的测试:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print(f"\n错误的测试:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        
        if result.skipped:
            print(f"\n跳过的测试:")
            for test, reason in result.skipped:
                print(f"  - {test}: {reason}")
        
        success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
        print(f"\n成功率: {success_rate:.1f}%")
        
        if result.wasSuccessful():
            print("✅ 所有测试通过！")
        else:
            print("❌ 部分测试失败")
