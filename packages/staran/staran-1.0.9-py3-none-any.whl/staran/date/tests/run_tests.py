#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
彩色测试运行器 v1.0.9
==================

为Staran项目提供美观的彩色测试输出，支持v1.0.9新功能测试。
"""

import unittest
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date.tests.test_core import *

# 尝试导入v1.0.8和v1.0.9的新功能测试
try:
    from staran.date.tests.test_v108_features import *
    V108_AVAILABLE = True
except ImportError:
    V108_AVAILABLE = False

try:
    from staran.date.tests.test_v109_features import *
    V109_AVAILABLE = True
except ImportError:
    V109_AVAILABLE = False

try:
    from staran.date.tests.test_enhancements import *
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False


class ColoredTestResult(unittest.TextTestResult):
    """彩色测试结果"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.verbosity = verbosity
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
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


class ColoredTestRunner(unittest.TextTestRunner):
    """彩色测试运行器"""
    
    def __init__(self, **kwargs):
        kwargs['resultclass'] = ColoredTestResult
        super().__init__(**kwargs)


def main():
    """主函数"""
    print(f"{chr(129514)} Staran v1.0.9 测试套件")
    print("=" * 50)
    print(f"Python版本: {sys.version}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 显示可用的测试模块
    available_modules = ["核心功能测试"]
    if V108_AVAILABLE:
        available_modules.append("v1.0.8新功能测试")
    if V109_AVAILABLE:
        available_modules.append("v1.0.9新功能测试")
    if ENHANCEMENTS_AVAILABLE:
        available_modules.append("增强功能测试")
    
    print(f"可用测试模块: {', '.join(available_modules)}")
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加核心测试
    core_tests = loader.loadTestsFromModule(sys.modules[__name__])
    suite.addTests(core_tests)
    
    # 尝试添加其他测试模块
    test_counts = {"核心功能": core_tests.countTestCases()}
    
    if V108_AVAILABLE:
        try:
            import staran.date.tests.test_v108_features as v108_module
            v108_tests = loader.loadTestsFromModule(v108_module)
            suite.addTests(v108_tests)
            test_counts["v1.0.8新功能"] = v108_tests.countTestCases()
        except Exception as e:
            print(f"警告: 无法加载v1.0.8测试: {e}")
    
    if V109_AVAILABLE:
        try:
            import staran.date.tests.test_v109_features as v109_module
            v109_tests = loader.loadTestsFromModule(v109_module)
            suite.addTests(v109_tests)
            test_counts["v1.0.9新功能"] = v109_tests.countTestCases()
        except Exception as e:
            print(f"警告: 无法加载v1.0.9测试: {e}")
    
    if ENHANCEMENTS_AVAILABLE:
        try:
            import staran.date.tests.test_enhancements as enh_module
            enh_tests = loader.loadTestsFromModule(enh_module)
            suite.addTests(enh_tests)
            test_counts["增强功能"] = enh_tests.countTestCases()
        except Exception as e:
            print(f"警告: 无法加载增强功能测试: {e}")
    
    # 运行测试
    runner = ColoredTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # 生成详细报告
    print("\n" + "=" * 50)
    print(f"{chr(128202)} 测试报告")
    print("=" * 50)
    print(f"运行时间: {end_time - start_time:.3f}秒")
    
    # 显示各模块测试数量
    total_tests = sum(test_counts.values())
    print(f"测试分布:")
    for module, count in test_counts.items():
        print(f"  {module}: {count}项")
    
    print(f"测试总数: {result.testsRun}")
    success_count = result.testsRun - len(result.failures) - len(result.errors)
    print(f"成功: {success_count}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if success_count > 0:
        success_rate = (success_count / result.testsRun) * 100
        print(f"成功率: {success_rate:.1f}%")
    
    if result.failures or result.errors:
        print(f"\n{chr(10060)} 测试失败! 失败: {len(result.failures)}, 错误: {len(result.errors)}")
        return 1
    else:
        print(f"\n{chr(9989)} 所有测试通过! {chr(127881)}")
        return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
