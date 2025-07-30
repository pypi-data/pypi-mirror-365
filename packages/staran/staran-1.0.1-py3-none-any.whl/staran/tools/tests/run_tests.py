#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整测试套件运行器
===============

运行所有测试并生成测试报告
"""

import unittest
import sys
import os
import logging
import time
from io import StringIO

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# 导入所有测试模块
from test_date import *
from test_api_compatibility import *
from test_logging import *

# 静音Date类的日志，避免干扰测试输出
from staran.tools.date import Date
Date.set_log_level(logging.CRITICAL)


class ColoredTextTestResult(unittest.TextTestResult):
    """带颜色的测试结果输出"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.verbosity = verbosity  # 确保verbosity属性存在
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'end': '\033[0m',
            'bold': '\033[1m'
        }
    
    def addSuccess(self, test):
        super().addSuccess(test)
        if self.verbosity > 1:
            self.stream.write(f"{self.colors['green']}✓{self.colors['end']} ")
            self.stream.writeln(f"{self.colors['green']}{self.getDescription(test)}{self.colors['end']}")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.write(f"{self.colors['red']}✗{self.colors['end']} ")
            self.stream.writeln(f"{self.colors['red']}{self.getDescription(test)}{self.colors['end']}")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.write(f"{self.colors['red']}✗{self.colors['end']} ")
            self.stream.writeln(f"{self.colors['red']}{self.getDescription(test)}{self.colors['end']}")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.write(f"{self.colors['yellow']}⊝{self.colors['end']} ")
            self.stream.writeln(f"{self.colors['yellow']}{self.getDescription(test)} (skipped: {reason}){self.colors['end']}")


class ColoredTestRunner(unittest.TextTestRunner):
    """带颜色的测试运行器"""
    
    def __init__(self, **kwargs):
        kwargs['resultclass'] = ColoredTextTestResult
        super().__init__(**kwargs)


def create_test_suite():
    """创建完整测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试模块
    test_modules = [
        'test_date',
        'test_api_compatibility', 
        'test_logging'
    ]
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            module_suite = loader.loadTestsFromModule(module)
            suite.addTest(module_suite)
        except ImportError as e:
            print(f"警告: 无法导入测试模块 {module_name}: {e}")
    
    return suite


def run_test_category(category_name, test_classes):
    """运行特定类别的测试"""
    print(f"\n{'='*60}")
    print(f"运行 {category_name} 测试")
    print(f"{'='*60}")
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTest(tests)
    
    runner = ColoredTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    print(f"\n{category_name} 测试完成")
    print(f"运行时间: {end_time - start_time:.2f}秒")
    print(f"测试总数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    return result


def main():
    """主函数"""
    print("Staran Date 库测试套件")
    print("="*60)
    print(f"Python 版本: {sys.version}")
    print(f"测试开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = []
    
    # 1. 核心功能测试
    print("\n🔧 运行核心功能测试...")
    core_tests = [
        TestDateCreation,
        TestDateClassMethods,
        TestDateConversion,
        TestDateFormatting,
        TestDateGetters,
        TestDatePredicates,
        TestDateArithmetic,
        TestDateComparison,
        TestDateCalculation,
        TestDateErrorHandling,
        TestBackwardCompatibility
    ]
    
    core_result = run_test_category("核心功能", core_tests)
    all_results.append(("核心功能", core_result))
    
    # 2. API兼容性测试
    print("\n🔄 运行API兼容性测试...")
    api_tests = [
        TestAPICompatibility,
        TestMethodSignatures,
        TestAPIDocumentation,
        TestAPIEvolution
    ]
    
    api_result = run_test_category("API兼容性", api_tests)
    all_results.append(("API兼容性", api_result))
    
    # 3. 日志系统测试
    print("\n📝 运行日志系统测试...")
    logging_tests = [
        TestLoggingSystem,
        TestLoggingConfiguration,
        TestLoggingIntegration,
        TestLoggingEdgeCases
    ]
    
    logging_result = run_test_category("日志系统", logging_tests)
    all_results.append(("日志系统", logging_result))
    
    # 生成总结报告
    print("\n" + "="*60)
    print("测试总结报告")
    print("="*60)
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    
    for category, result in all_results:
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        total_skipped += len(result.skipped)
        
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
        
        print(f"{category:20} | 测试: {result.testsRun:3d} | 成功率: {success_rate:6.1f}% | 失败: {len(result.failures):2d} | 错误: {len(result.errors):2d}")
    
    print("-" * 60)
    overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"{'总计':20} | 测试: {total_tests:3d} | 成功率: {overall_success_rate:6.1f}% | 失败: {total_failures:2d} | 错误: {total_errors:2d}")
    
    # 详细失败和错误报告
    if total_failures > 0 or total_errors > 0:
        print("\n" + "="*60)
        print("失败和错误详情")
        print("="*60)
        
        for category, result in all_results:
            if result.failures:
                print(f"\n{category} - 失败:")
                for test, traceback in result.failures:
                    print(f"  ✗ {test}")
                    print(f"    {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else '详见完整日志'}")
            
            if result.errors:
                print(f"\n{category} - 错误:")
                for test, traceback in result.errors:
                    print(f"  ✗ {test}")
                    print(f"    {traceback.split('\\n')[-2] if '\\n' in traceback else traceback}")
    
    print(f"\n测试完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 返回适当的退出码
    if total_failures > 0 or total_errors > 0:
        print(f"\n❌ 测试失败! 失败: {total_failures}, 错误: {total_errors}")
        return 1
    else:
        print(f"\n✅ 所有测试通过! 总计 {total_tests} 个测试")
        return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
