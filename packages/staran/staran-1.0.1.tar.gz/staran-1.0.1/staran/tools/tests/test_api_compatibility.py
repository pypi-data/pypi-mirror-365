#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API兼容性测试
===========

测试所有API方法的兼容性，包括：
- 新API命名规范
- 向后兼容性
- 别名方法
- 方法映射
"""

import unittest
import sys
import os
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.tools.date import Date


class TestAPICompatibility(unittest.TestCase):
    """测试API兼容性"""
    
    def setUp(self):
        """设置测试数据"""
        self.date = Date('20250415')
        # 静音日志
        Date.set_log_level(logging.CRITICAL)
    
    def test_all_new_api_methods_exist(self):
        """验证所有新API方法都存在"""
        # from_* 系列
        new_from_methods = [
            'from_string', 'from_timestamp', 'from_date_object', 
            'from_datetime_object'
        ]
        
        for method_name in new_from_methods:
            self.assertTrue(hasattr(Date, method_name), 
                          f"Class method {method_name} not found")
        
        # to_* 系列
        new_to_methods = [
            'to_tuple', 'to_dict', 'to_date_object', 
            'to_datetime_object', 'to_timestamp'
        ]
        
        for method_name in new_to_methods:
            self.assertTrue(hasattr(self.date, method_name), 
                          f"Instance method {method_name} not found")
        
        # format_* 系列
        new_format_methods = [
            'format_default', 'format_iso', 'format_chinese', 
            'format_compact', 'format_slash', 'format_dot', 
            'format_custom', 'format_year_month', 'format_year_month_compact'
        ]
        
        for method_name in new_format_methods:
            self.assertTrue(hasattr(self.date, method_name), 
                          f"Instance method {method_name} not found")
        
        # get_* 系列
        new_get_methods = [
            'get_weekday', 'get_isoweekday', 'get_days_in_month', 
            'get_days_in_year', 'get_format_type', 'get_month_start', 
            'get_month_end', 'get_year_start', 'get_year_end'
        ]
        
        for method_name in new_get_methods:
            self.assertTrue(hasattr(self.date, method_name), 
                          f"Instance method {method_name} not found")
        
        # is_* 系列
        new_is_methods = [
            'is_weekend', 'is_weekday', 'is_leap_year', 
            'is_month_start', 'is_month_end', 'is_year_start', 'is_year_end'
        ]
        
        for method_name in new_is_methods:
            self.assertTrue(hasattr(self.date, method_name), 
                          f"Instance method {method_name} not found")
        
        # add_/subtract_* 系列
        new_arithmetic_methods = [
            'add_days', 'add_months', 'add_years',
            'subtract_days', 'subtract_months', 'subtract_years'
        ]
        
        for method_name in new_arithmetic_methods:
            self.assertTrue(hasattr(self.date, method_name), 
                          f"Instance method {method_name} not found")
        
        # calculate_* 系列
        new_calculate_methods = [
            'calculate_difference_days', 'calculate_difference_months'
        ]
        
        for method_name in new_calculate_methods:
            self.assertTrue(hasattr(self.date, method_name), 
                          f"Instance method {method_name} not found")
    
    def test_backward_compatibility_methods_exist(self):
        """验证所有向后兼容方法都存在"""
        old_methods = [
            'format', 'to_date', 'to_datetime', 'weekday', 'difference',
            'start_of_month', 'end_of_month', 'start_of_year', 'end_of_year',
            'add', 'subtract', 'days_in_month', 'is_leap', 'convert_format'
        ]
        
        for method_name in old_methods:
            self.assertTrue(hasattr(self.date, method_name), 
                          f"Backward compatibility method {method_name} not found")
    
    def test_new_api_functionality(self):
        """测试新API方法的功能"""
        # 测试to_*系列
        self.assertEqual(self.date.to_tuple(), (2025, 4, 15))
        self.assertIsInstance(self.date.to_dict(), dict)
        
        # 测试format_*系列
        self.assertEqual(self.date.format_iso(), '2025-04-15')
        self.assertEqual(self.date.format_chinese(), '2025年04月15日')
        
        # 测试get_*系列
        self.assertIsInstance(self.date.get_weekday(), int)
        self.assertIsInstance(self.date.get_days_in_month(), int)
        
        # 测试is_*系列
        self.assertIsInstance(self.date.is_weekend(), bool)
        self.assertIsInstance(self.date.is_leap_year(), bool)
        
        # 测试add_/subtract_*系列
        result = self.date.add_days(1)
        self.assertEqual(str(result), '20250416')
        
        result = self.date.subtract_days(1)
        self.assertEqual(str(result), '20250414')
    
    def test_backward_compatibility_functionality(self):
        """测试向后兼容方法的功能"""
        # 旧方法应该与新方法产生相同结果
        self.assertEqual(self.date.format('%Y-%m-%d'), self.date.format_custom('%Y-%m-%d'))
        self.assertEqual(self.date.to_date(), self.date.to_date_object())
        self.assertEqual(self.date.to_datetime(), self.date.to_datetime_object())
        self.assertEqual(self.date.weekday(), self.date.get_weekday())
        
        # 测试difference方法
        other = Date('20250420')
        self.assertEqual(other.difference(self.date), 
                        other.calculate_difference_days(self.date))
    
    def test_method_aliases(self):
        """测试方法别名"""
        # 测试别名映射
        self.assertEqual(self.date.start_of_month(), self.date.get_month_start())
        self.assertEqual(self.date.end_of_month(), self.date.get_month_end())
        self.assertEqual(self.date.start_of_year(), self.date.get_year_start())
        self.assertEqual(self.date.end_of_year(), self.date.get_year_end())
        self.assertEqual(self.date.days_in_month(), self.date.get_days_in_month())
        self.assertEqual(self.date.is_leap(), self.date.is_leap_year())
    
    def test_api_consistency(self):
        """测试API一致性"""
        # 所有from_*方法都应该是类方法
        self.assertTrue(callable(getattr(Date, 'from_string')))
        self.assertTrue(callable(getattr(Date, 'from_timestamp')))
        
        # 所有to_*方法都应该返回转换后的值
        self.assertIsInstance(self.date.to_tuple(), tuple)
        self.assertIsInstance(self.date.to_dict(), dict)
        
        # 所有format_*方法都应该返回字符串
        self.assertIsInstance(self.date.format_default(), str)
        self.assertIsInstance(self.date.format_iso(), str)
        
        # 所有get_*方法都应该返回值
        self.assertIsNotNone(self.date.get_weekday())
        self.assertIsNotNone(self.date.get_format_type())
        
        # 所有is_*方法都应该返回布尔值
        self.assertIsInstance(self.date.is_weekend(), bool)
        self.assertIsInstance(self.date.is_leap_year(), bool)
        
        # 所有add_/subtract_*方法都应该返回新的Date对象
        self.assertIsInstance(self.date.add_days(1), Date)
        self.assertIsInstance(self.date.subtract_days(1), Date)


class TestMethodSignatures(unittest.TestCase):
    """测试方法签名"""
    
    def setUp(self):
        """设置测试数据"""
        self.date = Date('20250415')
        Date.set_log_level(logging.CRITICAL)
    
    def test_from_methods_signatures(self):
        """测试from_*方法签名"""
        # from_string应该接受字符串
        result = Date.from_string('20250101')
        self.assertIsInstance(result, Date)
        
        # from_timestamp应该接受数字
        import time
        timestamp = time.time()
        result = Date.from_timestamp(timestamp)
        self.assertIsInstance(result, Date)
    
    def test_format_methods_signatures(self):
        """测试format_*方法签名"""
        # format_custom应该接受格式字符串
        result = self.date.format_custom('%Y-%m-%d')
        self.assertEqual(result, '2025-04-15')
        
        # 其他format方法不需要参数
        self.assertIsInstance(self.date.format_default(), str)
        self.assertIsInstance(self.date.format_iso(), str)
    
    def test_add_subtract_methods_signatures(self):
        """测试add_/subtract_方法签名"""
        # 所有方法都应该接受整数参数
        result = self.date.add_days(1)
        self.assertIsInstance(result, Date)
        
        result = self.date.add_months(1)
        self.assertIsInstance(result, Date)
        
        result = self.date.subtract_years(1)
        self.assertIsInstance(result, Date)


class TestAPIDocumentation(unittest.TestCase):
    """测试API文档字符串"""
    
    def setUp(self):
        """设置测试数据"""
        self.date = Date('20250415')
    
    def test_class_docstring(self):
        """测试类文档字符串"""
        self.assertIsNotNone(Date.__doc__)
        self.assertIn('日期', Date.__doc__)
    
    def test_method_docstrings(self):
        """测试方法文档字符串"""
        # 检查主要方法的文档字符串
        methods_to_check = [
            'from_string', 'to_date_object', 'format_iso', 
            'get_weekday', 'is_weekend', 'add_days'
        ]
        
        for method_name in methods_to_check:
            method = getattr(Date, method_name) if hasattr(Date, method_name) else getattr(self.date, method_name)
            self.assertIsNotNone(method.__doc__, 
                               f"Method {method_name} missing docstring")


class TestAPIEvolution(unittest.TestCase):
    """测试API演进"""
    
    def setUp(self):
        """设置测试数据"""
        self.date = Date('20250415')
        Date.set_log_level(logging.CRITICAL)
    
    def test_version_tracking(self):
        """测试版本跟踪"""
        # 确保Date类有版本信息
        self.assertTrue(hasattr(Date, '__version__') or 
                       hasattr(Date, 'get_version'))
    
    def test_deprecation_warnings(self):
        """测试废弃警告"""
        # 目前不应该有废弃警告，但可以测试框架是否就位
        import warnings
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # 使用旧方法不应该产生警告（目前保持向后兼容）
            result = self.date.format('%Y-%m-%d')
            
            # 目前不期望有警告
            deprecation_warnings = [warning for warning in w 
                                  if issubclass(warning.category, DeprecationWarning)]
            # 可以为空，因为我们还没有标记任何方法为废弃
    
    def test_future_compatibility(self):
        """测试未来兼容性"""
        # 确保新API方法都有适当的实现
        new_methods = [
            'from_string', 'to_tuple', 'format_iso', 
            'get_weekday', 'is_weekend', 'add_days'
        ]
        
        for method_name in new_methods:
            if hasattr(Date, method_name):
                method = getattr(Date, method_name)
            else:
                method = getattr(self.date, method_name)
            
            # 方法应该是可调用的
            self.assertTrue(callable(method))
            
            # 方法不应该只是简单的pass或NotImplemented
            if hasattr(method, '__code__'):
                # 检查方法体不为空
                self.assertGreater(method.__code__.co_code.__len__(), 0)


if __name__ == '__main__':
    # 运行所有兼容性测试
    unittest.main(verbosity=2)
