#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran Tools 测试模块
==================

为staran.tools包提供全面的单元测试和集成测试。

测试模块结构：
- test_date.py - Date类的完整测试套件
- test_api_compatibility.py - API兼容性测试
- test_logging.py - 日志系统测试
- test_performance.py - 性能基准测试

使用方法：
    # 运行所有测试
    python -m unittest discover staran.tools.tests
    
    # 运行特定测试文件
    python -m unittest staran.tools.tests.test_date
    
    # 运行特定测试类
    python -m unittest staran.tools.tests.test_date.TestDateCreation
"""

__version__ = '1.0.1'
__author__ = 'StarAn'
__description__ = 'Test suite for staran.tools package'

# 测试相关的导入
try:
    import unittest
    import logging
    import sys
    import os
    
    # 添加父目录到路径，确保可以导入staran模块
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
    HAS_UNITTEST = True
except ImportError:
    HAS_UNITTEST = False

__all__ = [
    'HAS_UNITTEST',
    'run_all_tests',
    'run_test_suite'
]


def run_all_tests(verbosity=2):
    """
    运行所有测试
    
    Args:
        verbosity: 详细程度 (0=静默, 1=正常, 2=详细)
        
    Returns:
        TestResult对象
    """
    if not HAS_UNITTEST:
        print("❌ unittest模块不可用，无法运行测试")
        return None
    
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result


def run_test_suite(test_module, verbosity=2):
    """
    运行指定的测试套件
    
    Args:
        test_module: 测试模块名称 (如 'test_date')
        verbosity: 详细程度
        
    Returns:
        TestResult对象
    """
    if not HAS_UNITTEST:
        print("❌ unittest模块不可用，无法运行测试")
        return None
    
    # 导入并运行指定的测试模块
    try:
        module = __import__(f'staran.tools.tests.{test_module}', fromlist=[test_module])
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        
        return result
    except ImportError as e:
        print(f"❌ 无法导入测试模块 {test_module}: {e}")
        return None


if __name__ == "__main__":
    print("🧪 Staran Tools 测试套件")
    print("=" * 50)
    
    if HAS_UNITTEST:
        result = run_all_tests()
        if result:
            if result.wasSuccessful():
                print("✅ 所有测试通过!")
            else:
                print(f"❌ 测试失败: {len(result.failures)} 失败, {len(result.errors)} 错误")
    else:
        print("❌ 测试环境不完整，请确保Python环境正确安装")
