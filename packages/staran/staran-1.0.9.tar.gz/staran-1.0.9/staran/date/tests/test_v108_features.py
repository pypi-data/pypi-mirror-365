#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date类v1.0.8新功能测试
====================

测试v1.0.8版本新增的农历支持和多语言功能：
- 农历与公历互转
- 农历日期格式化
- 农历日期比较
- 多语言本地化
- 全局语言设置
"""

import unittest
import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date.core import Date
from staran.date.lunar import LunarDate
from staran.date.i18n import Language


class TestLunarSupport(unittest.TestCase):
    """测试农历支持功能"""
    
    def test_create_from_lunar(self):
        """测试从农历日期创建"""
        # 农历2025年正月初一
        date = Date.from_lunar(2025, 1, 1)
        self.assertIsInstance(date, Date)
        
        # 农历2025年闰四月十五
        leap_date = Date.from_lunar(2025, 4, 15, is_leap=True)
        self.assertIsInstance(leap_date, Date)
    
    def test_create_from_lunar_string(self):
        """测试从农历字符串创建"""
        # 正常月份
        date = Date.from_lunar_string("20250315")
        self.assertIsInstance(date, Date)
        
        # 闰月
        leap_date = Date.from_lunar_string("2025闰0415")
        self.assertIsInstance(leap_date, Date)
    
    def test_to_lunar(self):
        """测试转为农历"""
        date = Date("20250129")  # 2025年1月29日
        lunar = date.to_lunar()
        self.assertIsInstance(lunar, LunarDate)
        # 2025年1月29日对应农历2025年三月初十
        self.assertEqual(lunar.year, 2025)
        self.assertEqual(lunar.month, 3)
        self.assertEqual(lunar.day, 10)
    
    def test_to_lunar_string(self):
        """测试转为农历字符串"""
        date = Date("20250129")
        lunar_compact = date.to_lunar_string(compact=True)
        lunar_full = date.to_lunar_string(compact=False)
        
        self.assertIsInstance(lunar_compact, str)
        self.assertIsInstance(lunar_full, str)
        self.assertTrue("农历" in lunar_full)
    
    def test_format_lunar(self):
        """测试农历格式化"""
        date = Date("20250129")
        
        # 基本格式
        lunar_basic = date.format_lunar()
        self.assertIn("农历", lunar_basic)
        
        # 包含生肖
        lunar_zodiac = date.format_lunar(include_zodiac=True)
        self.assertIsInstance(lunar_zodiac, str)
        
        # 紧凑格式
        lunar_compact = date.format_lunar_compact()
        self.assertTrue(lunar_compact.isdigit() or '闰' in lunar_compact)
    
    def test_lunar_judgments(self):
        """测试农历判断方法"""
        # 找一个农历正月初一的日期进行测试
        date = Date.from_lunar(2025, 1, 1)
        self.assertTrue(date.is_lunar_new_year())
        self.assertTrue(date.is_lunar_month_start())
        self.assertFalse(date.is_lunar_month_mid())
        
        # 测试农历十五
        mid_date = Date.from_lunar(2025, 1, 15)
        self.assertFalse(mid_date.is_lunar_new_year())
        self.assertFalse(mid_date.is_lunar_month_start())
        self.assertTrue(mid_date.is_lunar_month_mid())
    
    def test_lunar_comparison(self):
        """测试农历比较"""
        date1 = Date.from_lunar(2025, 1, 1)
        date2 = Date.from_lunar(2025, 1, 15)
        date3 = Date.from_lunar(2025, 1, 1)
        
        # 比较测试
        self.assertEqual(date1.compare_lunar(date2), -1)  # date1 < date2
        self.assertEqual(date2.compare_lunar(date1), 1)   # date2 > date1
        self.assertEqual(date1.compare_lunar(date3), 0)   # date1 == date3
        
        # 同月测试
        self.assertTrue(date1.is_same_lunar_month(date2))
        self.assertTrue(date1.is_same_lunar_month(date3))
        
        # 同日测试
        self.assertFalse(date1.is_same_lunar_day(date2))
        self.assertTrue(date1.is_same_lunar_day(date3))


class TestMultiLanguageSupport(unittest.TestCase):
    """测试多语言支持功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 保存原始语言设置
        self.original_language = Date.get_language()
    
    def tearDown(self):
        """清理测试环境"""
        # 恢复原始语言设置
        Date.set_language(self.original_language)
    
    def test_set_global_language(self):
        """测试设置全局语言"""
        # 测试设置不同语言
        Date.set_language('en_US')
        self.assertEqual(Date.get_language(), 'en_US')
        
        Date.set_language('zh_TW')
        self.assertEqual(Date.get_language(), 'zh_TW')
        
        Date.set_language('ja_JP')
        self.assertEqual(Date.get_language(), 'ja_JP')
        
        # 测试无效语言
        with self.assertRaises(ValueError):
            Date.set_language('invalid_lang')
    
    def test_get_supported_languages(self):
        """测试获取支持的语言"""
        languages = Date.get_supported_languages()
        self.assertIsInstance(languages, dict)
        self.assertIn('zh_CN', languages)
        self.assertIn('zh_TW', languages)
        self.assertIn('ja_JP', languages)
        self.assertIn('en_US', languages)
    
    def test_format_localized(self):
        """测试本地化格式"""
        date = Date("20250415")
        
        # 中文简体
        Date.set_language('zh_CN')
        cn_format = date.format_localized()
        self.assertIn('年', cn_format)
        
        # 英语
        Date.set_language('en_US')
        en_format = date.format_localized()
        self.assertTrue('/' in en_format or '-' in en_format)
        
        # 日语
        Date.set_language('ja_JP')
        jp_format = date.format_localized()
        self.assertIn('年', jp_format)
    
    def test_format_weekday_localized(self):
        """测试本地化星期格式"""
        date = Date("20250415")  # 2025年4月15日，星期二
        
        # 中文简体
        Date.set_language('zh_CN')
        weekday_cn = date.format_weekday_localized()
        self.assertIn('星期', weekday_cn)
        
        # 英语
        Date.set_language('en_US')
        weekday_en = date.format_weekday_localized()
        self.assertIn('day', weekday_en.lower())
        
        # 日语
        Date.set_language('ja_JP')
        weekday_jp = date.format_weekday_localized()
        self.assertIn('曜日', weekday_jp)
        
        # 测试短格式
        weekday_short = date.format_weekday_localized(short=True)
        self.assertTrue(len(weekday_short) <= 3)
    
    def test_format_month_localized(self):
        """测试本地化月份格式"""
        date = Date("20250415")  # 4月
        
        # 中文
        Date.set_language('zh_CN')
        month_cn = date.format_month_localized()
        self.assertIn('月', month_cn)
        
        # 英语
        Date.set_language('en_US')
        month_en = date.format_month_localized()
        self.assertIn('Apr', month_en)
    
    def test_format_quarter_localized(self):
        """测试本地化季度格式"""
        date = Date("20250415")  # 第2季度
        
        # 中文
        Date.set_language('zh_CN')
        quarter_cn = date.format_quarter_localized()
        self.assertIn('季度', quarter_cn)
        
        # 英语
        Date.set_language('en_US')
        quarter_en = date.format_quarter_localized()
        self.assertIn('Quarter', quarter_en)
        
        # 短格式
        quarter_short = date.format_quarter_localized(short=True)
        self.assertIn('Q', quarter_short)
    
    def test_format_relative_localized(self):
        """测试本地化相对时间格式"""
        today = Date.today()
        tomorrow = today.add_days(1)
        yesterday = today.add_days(-1)
        
        # 中文
        Date.set_language('zh_CN')
        self.assertIn('今', today.format_relative_localized())
        self.assertIn('明', tomorrow.format_relative_localized())
        self.assertIn('昨', yesterday.format_relative_localized())
        
        # 英语
        Date.set_language('en_US')
        self.assertEqual('today', today.format_relative_localized())
        self.assertEqual('tomorrow', tomorrow.format_relative_localized())
        self.assertEqual('yesterday', yesterday.format_relative_localized())
    
    def test_language_consistency(self):
        """测试语言一致性"""
        date = Date("20250415")
        
        # 设置一次语言，多个方法应该保持一致
        Date.set_language('ja_JP')
        
        weekday = date.format_weekday_localized()
        month = date.format_month_localized()
        relative = date.format_relative_localized()
        
        # 都应该是日语格式
        self.assertIn('曜日', weekday)
        self.assertIn('月', month)
        self.assertIsInstance(relative, str)


class TestLanguageDirectOverride(unittest.TestCase):
    """测试语言覆盖功能"""
    
    def test_language_override(self):
        """测试单次使用时覆盖语言设置"""
        Date.set_language('zh_CN')  # 设置全局为中文
        date = Date("20250415")
        
        # 全局中文格式
        cn_format = date.format_weekday_localized()
        self.assertIn('星期', cn_format)
        
        # 单次覆盖为英语
        en_format = date.format_weekday_localized(language_code='en_US')
        self.assertIn('day', en_format.lower())
        
        # 全局设置仍然是中文
        self.assertEqual(Date.get_language(), 'zh_CN')
        cn_format2 = date.format_weekday_localized()
        self.assertIn('星期', cn_format2)


class TestLunarDateClass(unittest.TestCase):
    """测试LunarDate类功能"""
    
    def test_lunar_date_creation(self):
        """测试农历日期创建"""
        lunar = LunarDate(2025, 3, 15)
        self.assertEqual(lunar.year, 2025)
        self.assertEqual(lunar.month, 3)
        self.assertEqual(lunar.day, 15)
        self.assertFalse(lunar.is_leap)
        
        # 测试闰月
        leap_lunar = LunarDate(2025, 4, 15, is_leap=True)
        self.assertTrue(leap_lunar.is_leap)
    
    def test_lunar_solar_conversion(self):
        """测试农历公历互转"""
        # 创建农历日期
        lunar = LunarDate(2025, 1, 1)  # 农历正月初一
        
        # 转为公历
        solar = lunar.to_solar()
        self.assertIsInstance(solar, datetime.date)
        
        # 再转回农历
        lunar2 = LunarDate.from_solar(solar)
        self.assertEqual(lunar.year, lunar2.year)
        self.assertEqual(lunar.month, lunar2.month)
        self.assertEqual(lunar.day, lunar2.day)
        self.assertEqual(lunar.is_leap, lunar2.is_leap)
    
    def test_lunar_formatting(self):
        """测试农历格式化"""
        lunar = LunarDate(2025, 3, 15)
        
        # 中文格式
        chinese = lunar.format_chinese()
        self.assertIn('农历', chinese)
        self.assertIn('三月', chinese)
        self.assertIn('十五', chinese)
        
        # 紧凑格式
        compact = lunar.format_compact()
        self.assertEqual(compact, '20250315')
        
        # ISO样式格式
        iso_like = lunar.format_iso_like()
        self.assertEqual(iso_like, '2025-03-15')
    
    def test_lunar_comparison(self):
        """测试农历比较"""
        lunar1 = LunarDate(2025, 1, 1)
        lunar2 = LunarDate(2025, 1, 15)
        lunar3 = LunarDate(2025, 1, 1)
        
        self.assertTrue(lunar1 < lunar2)
        self.assertTrue(lunar2 > lunar1)
        self.assertEqual(lunar1, lunar3)
        self.assertTrue(lunar1 <= lunar2)
        self.assertTrue(lunar2 >= lunar1)
    
    def test_ganzhi_zodiac(self):
        """测试天干地支和生肖"""
        lunar = LunarDate(2025, 1, 1)
        
        ganzhi = lunar.get_ganzhi_year()
        self.assertIsInstance(ganzhi, str)
        self.assertEqual(len(ganzhi), 2)
        
        zodiac = lunar.get_zodiac()
        self.assertIsInstance(zodiac, str)
        self.assertEqual(len(zodiac), 1)


if __name__ == '__main__':
    # 运行测试
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestLunarSupport))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiLanguageSupport))
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageDirectOverride))
    suite.addTests(loader.loadTestsFromTestCase(TestLunarDateClass))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果统计
    print(f"\n{'='*60}")
    print(f"🧪 Staran v1.0.8 新功能测试结果")
    print(f"{'='*60}")
    print(f"测试总数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.failures:
        print(f"\n失败的测试:")
        for test, trace in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n错误的测试:")
        for test, trace in result.errors:
            print(f"  - {test}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"成功率: {success_rate:.1f}%")
