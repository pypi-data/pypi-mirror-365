#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
特征管理器
负责特征工程的核心管理功能，基于新的引擎架构
"""

from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from ..engines import BaseEngine, create_engine, DatabaseType


class FeatureManager:
    """
    特征管理器 - 使用引擎架构的核心特征管理
    """
    
    def __init__(self, database_name: str, engine_type: str = "spark", 
                 sql_executor: Optional[Callable] = None):
        """
        初始化特征管理器
        
        Args:
            database_name: 数据库名称
            engine_type: 引擎类型 ('spark', 'hive', 'turing')
            sql_executor: SQL执行器函数 (可选，仅用于非turing引擎)
        """
        self.database_name = database_name
        self.engine_type = engine_type
        
        # 创建数据库引擎
        self.engine = create_engine(
            engine_type=engine_type,
            database_name=database_name,
            sql_executor=sql_executor
        )
    
    # 委托给引擎的方法
    def execute_sql(self, sql: str, description: str = "") -> Any:
        """执行SQL语句"""
        return self.engine.execute_sql(sql, description)
    
    def get_full_table_name(self, table_name: str) -> str:
        """获取完整的表名（包含数据库名）"""
        return self.engine.get_full_table_name(table_name)
    
    def generate_table_name(self, base_name: str, year: int, month: int, 
                          suffix: str = "raw") -> str:
        """
        生成标准化的表名
        格式: {base_name}_{yyyy}_{MM}_{suffix}
        """
        return self.engine.generate_table_name(base_name, year, month, suffix)
    
    def create_table(self, table_name: str, select_sql: str, 
                    execute: bool = False, **kwargs) -> Dict[str, Any]:
        """创建表"""
        return self.engine.create_table(table_name, select_sql, execute, **kwargs)
    
    def drop_table(self, table_name: str, execute: bool = False) -> Dict[str, Any]:
        """删除表"""
        return self.engine.drop_table(table_name, execute)
    
    def download_table_data(self, table_name: str, output_path: str, 
                          **kwargs) -> Dict[str, Any]:
        """下载表数据"""
        return self.engine.download_table_data(table_name, output_path, **kwargs)
    
    def download_query_result(self, sql: str, output_path: str, 
                            **kwargs) -> Dict[str, Any]:
        """下载查询结果"""
        return self.engine.download_query_result(sql, output_path, **kwargs)
    
    def get_execution_history(self) -> List[Dict]:
        """获取SQL执行历史"""
        return self.engine.get_execution_history()
    
    def clear_history(self):
        """清空执行历史"""
        self.engine.clear_history()
    
    def __str__(self):
        return f"FeatureManager(engine={self.engine})"


class FeatureTableManager:
    """
    特征表管理器
    负责特征表的创建、删除、管理等操作
    """
    
    def __init__(self, feature_manager: FeatureManager):
        """
        初始化表管理器
        
        Args:
            feature_manager: 特征管理器实例
        """
        self.feature_manager = feature_manager
        self.created_tables = []
    
    def create_feature_table(self, base_name: str, year: int, month: int, 
                           version: int, sql: str, execute: bool = False,
                           **kwargs) -> str:
        """
        创建特征表
        
        Args:
            base_name: 基础表名
            year: 年份
            month: 月份
            version: 版本号
            sql: 创建表的SQL
            execute: 是否立即执行
            **kwargs: 传递给引擎的其他参数
            
        Returns:
            创建的表名
        """
        table_name = self.feature_manager.generate_table_name(base_name, year, month)
        
        result = self.feature_manager.create_table(table_name, sql, execute, **kwargs)
        
        if execute and result.get('status') == 'success':
            self.created_tables.append(table_name)
        
        return table_name
    
    def drop_feature_table(self, table_name: str, execute: bool = False) -> str:
        """
        删除特征表
        
        Args:
            table_name: 表名
            execute: 是否立即执行
            
        Returns:
            删除表的SQL
        """
        result = self.feature_manager.drop_table(table_name, execute)
        
        if execute and result.get('status') == 'success':
            if table_name in self.created_tables:
                self.created_tables.remove(table_name)
        
        return result.get('sql', '')
    
    def get_created_tables(self) -> List[str]:
        """获取已创建的表列表"""
        return self.created_tables.copy()
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在（简单检查，实际需要查询数据库）"""
        return table_name in self.created_tables
