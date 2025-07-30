#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
彩色测试运行器
=======    print(f"{chr(129514)} Staran v1.0.2 测试套件")====

为Staran项目提供美观的彩色测试输出。
"""

import unittest
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date.tests.test_core import *


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
    print(f"{chr(129514)} Staran v1.0.1 测试套件")
    print("=" * 50)
    print(f"Python版本: {sys.version}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # 运行测试
    runner = ColoredTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # 生成报告
    print("\n" + "=" * 50)
    print(f"{chr(128202)} 测试报告")
    print("=" * 50)
    print(f"运行时间: {end_time - start_time:.3f}秒")
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
