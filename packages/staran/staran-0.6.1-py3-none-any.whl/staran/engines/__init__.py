#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库引擎模块
提供统一的数据库引擎接口
"""

# 基础组件
from .base import BaseEngine, DatabaseType

# 具体引擎实现
from .spark import SparkEngine
from .hive import HiveEngine

# 图灵平台引擎 (可选导入)
try:
    from .turing import TuringEngine, create_turing_engine
    _TURING_AVAILABLE = True
except ImportError:
    TuringEngine = None
    create_turing_engine = None
    _TURING_AVAILABLE = False

# 便捷创建函数
def create_engine(engine_type: str, database_name: str, **kwargs) -> BaseEngine:
    """
    创建数据库引擎的便捷函数
    
    Args:
        engine_type: 引擎类型 ('spark', 'hive', 'turing')
        database_name: 数据库名称
        **kwargs: 其他参数
        
    Returns:
        数据库引擎实例
    """
    engine_type = engine_type.lower()
    
    if engine_type == 'spark':
        return SparkEngine(database_name, **kwargs)
    elif engine_type == 'hive':
        return HiveEngine(database_name, **kwargs)
    elif engine_type == 'turing':
        if not _TURING_AVAILABLE:
            raise ImportError("TuringEngine不可用，请确保turingPythonLib已安装")
        return TuringEngine(database_name, **kwargs)
    else:
        raise ValueError(f"不支持的引擎类型: {engine_type}")

# 主要导出
__all__ = [
    'BaseEngine',
    'DatabaseType',
    'SparkEngine',
    'HiveEngine',
    'create_engine'
]

# 如果图灵引擎可用，添加到导出
if _TURING_AVAILABLE:
    __all__.extend([
        'TuringEngine',
        'create_turing_engine'
    ])
