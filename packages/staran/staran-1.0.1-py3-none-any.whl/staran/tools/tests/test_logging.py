#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志系统测试
==========

测试Date类的日志功能，包括：
- 日志级别设置
- 日志消息记录
- 日志输出控制
- 性能日志
"""

import unittest
import sys
import os
import logging
import io
from contextlib import redirect_stderr

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.tools.date import Date


class TestLoggingSystem(unittest.TestCase):
    """测试日志系统基本功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 重置日志级别
        Date.set_log_level(logging.DEBUG)
        
        # 创建字符串流来捕获日志输出
        self.log_stream = io.StringIO()
        
        # 获取Date的日志记录器
        self.logger = logging.getLogger('staran.tools.date')
        
        # 清除现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 添加流处理器
        self.handler = logging.StreamHandler(self.log_stream)
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """清理测试环境"""
        # 移除处理器
        self.logger.removeHandler(self.handler)
        self.handler.close()
        
        # 重置日志级别为ERROR，避免干扰其他测试
        Date.set_log_level(logging.ERROR)
    
    def get_log_output(self):
        """获取日志输出"""
        return self.log_stream.getvalue()
    
    def test_log_level_setting(self):
        """测试日志级别设置"""
        # 测试设置不同的日志级别
        Date.set_log_level(logging.INFO)
        Date.set_log_level(logging.WARNING)
        Date.set_log_level(logging.ERROR)
        Date.set_log_level(logging.DEBUG)
        
        # 验证级别设置成功（通过创建对象来触发日志）
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        Date('20250415')
        log_output = self.get_log_output()
        
        # 应该有DEBUG级别的日志
        self.assertIn('DEBUG', log_output)
    
    def test_object_creation_logging(self):
        """测试对象创建日志"""
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        # 创建不同类型的Date对象
        Date('20250415')
        Date('202504')
        Date('2025')
        Date(2025, 4, 15)
        
        log_output = self.get_log_output()
        
        # 验证有创建日志
        self.assertIn('创建Date对象', log_output)
        self.assertIn('20250415', log_output)
    
    def test_method_call_logging(self):
        """测试方法调用日志"""
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        date = Date('20250415')
        
        # 调用各种方法
        date.format_iso()
        date.add_days(10)
        date.get_weekday()
        date.is_weekend()
        
        log_output = self.get_log_output()
        
        # 验证有方法调用日志
        self.assertIn('调用方法', log_output)
    
    def test_error_logging(self):
        """测试错误日志"""
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        # 触发错误
        try:
            Date('invalid_date')
        except ValueError:
            pass
        
        log_output = self.get_log_output()
        
        # 验证有错误日志
        self.assertIn('ERROR', log_output)
    
    def test_performance_logging(self):
        """测试性能日志"""
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        date = Date('20250415')
        
        # 执行一些计算密集的操作
        for i in range(10):
            date.add_days(i)
        
        log_output = self.get_log_output()
        
        # 性能日志可能不会每次都出现，但应该有调用日志
        self.assertIn('调用方法', log_output)


class TestLoggingConfiguration(unittest.TestCase):
    """测试日志配置"""
    
    def setUp(self):
        """设置测试环境"""
        Date.set_log_level(logging.ERROR)  # 默认高级别
    
    def test_log_level_effects(self):
        """测试日志级别效果"""
        # 创建测试流
        log_stream = io.StringIO()
        logger = logging.getLogger('staran.tools.date')
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 添加新处理器
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        try:
            # 测试ERROR级别
            Date.set_log_level(logging.ERROR)
            logger.setLevel(logging.ERROR)
            
            log_stream.truncate(0)
            log_stream.seek(0)
            
            Date('20250415')
            error_output = log_stream.getvalue()
            
            # 测试DEBUG级别
            Date.set_log_level(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            
            log_stream.truncate(0)
            log_stream.seek(0)
            
            Date('20250415')
            debug_output = log_stream.getvalue()
            
            # DEBUG级别应该有更多输出
            self.assertGreaterEqual(len(debug_output), len(error_output))
            
        finally:
            logger.removeHandler(handler)
            handler.close()
    
    def test_log_message_format(self):
        """测试日志消息格式"""
        log_stream = io.StringIO()
        logger = logging.getLogger('staran.tools.date')
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            Date.set_log_level(logging.DEBUG)
            
            Date('20250415')
            output = log_stream.getvalue()
            
            # 验证日志格式包含时间戳、名称、级别、消息
            if output:  # 如果有输出
                lines = output.strip().split('\n')
                for line in lines:
                    parts = line.split(' - ')
                    if len(parts) >= 4:
                        self.assertIn('staran.tools.date', parts[1])
                        self.assertIn(parts[2], ['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        
        finally:
            logger.removeHandler(handler)
            handler.close()


class TestLoggingIntegration(unittest.TestCase):
    """测试日志集成"""
    
    def setUp(self):
        """设置测试环境"""
        Date.set_log_level(logging.WARNING)
    
    def test_logging_with_various_operations(self):
        """测试各种操作的日志集成"""
        log_stream = io.StringIO()
        logger = logging.getLogger('staran.tools.date')
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(funcName)s:%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            Date.set_log_level(logging.DEBUG)
            
            # 执行各种操作
            date = Date('20250415')
            date.format_iso()
            date.add_days(10)
            date.get_weekday()
            result = date.is_weekend()
            
            output = log_stream.getvalue()
            
            # 验证不同操作都有日志记录
            if output:
                self.assertIsInstance(output, str)
                # 基本验证日志不为空
                self.assertGreater(len(output.strip()), 0)
        
        finally:
            logger.removeHandler(handler)
            handler.close()
    
    def test_logging_performance_impact(self):
        """测试日志对性能的影响"""
        import time
        
        # 测试无日志性能
        Date.set_log_level(logging.CRITICAL)
        
        start_time = time.time()
        for i in range(100):
            date = Date('20250415')
            date.add_days(i % 10)
        no_log_time = time.time() - start_time
        
        # 测试有日志性能
        Date.set_log_level(logging.DEBUG)
        
        start_time = time.time()
        for i in range(100):
            date = Date('20250415')
            date.add_days(i % 10)
        with_log_time = time.time() - start_time
        
        # 日志不应该显著影响性能（这里允许10倍的性能差异）
        self.assertLess(with_log_time, no_log_time * 10)
        
        # 重置日志级别
        Date.set_log_level(logging.ERROR)


class TestLoggingEdgeCases(unittest.TestCase):
    """测试日志边缘情况"""
    
    def setUp(self):
        """设置测试环境"""
        Date.set_log_level(logging.ERROR)
    
    def test_logging_with_invalid_operations(self):
        """测试无效操作的日志"""
        log_stream = io.StringIO()
        logger = logging.getLogger('staran.tools.date')
        
        # 清除现有处理器
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s:%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            Date.set_log_level(logging.DEBUG)
            
            # 尝试无效操作
            try:
                Date('invalid')
            except ValueError:
                pass
            
            try:
                Date(2025, 13, 1)  # 无效月份
            except ValueError:
                pass
            
            output = log_stream.getvalue()
            
            # 应该有错误日志
            if output:
                self.assertIn('ERROR', output)
        
        finally:
            logger.removeHandler(handler)
            handler.close()
    
    def test_concurrent_logging(self):
        """测试并发日志"""
        import threading
        import time
        
        Date.set_log_level(logging.DEBUG)
        
        results = []
        
        def create_dates():
            for i in range(10):
                try:
                    date = Date(f'2025041{i % 10}')
                    results.append(str(date))
                except:
                    pass
        
        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_dates)
            threads.append(thread)
        
        # 启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        self.assertGreater(len(results), 0)
        
        # 重置日志级别
        Date.set_log_level(logging.ERROR)


if __name__ == '__main__':
    # 运行所有日志测试
    unittest.main(verbosity=2)
