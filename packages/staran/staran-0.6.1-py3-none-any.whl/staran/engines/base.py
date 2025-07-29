#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库引擎基类
定义统一的SQL生成、执行和数据下载接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from datetime import datetime


class DatabaseType(Enum):
    """数据库类型枚举"""
    SPARK = "spark"
    HIVE = "hive"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


class BaseEngine(ABC):
    """
    数据库引擎基类
    整合SQL生成、执行和数据下载功能
    """
    
    def __init__(self, database_name: str, sql_executor: Optional[Callable] = None):
        """
        初始化引擎
        
        Args:
            database_name: 数据库名称
            sql_executor: SQL执行器函数 (可选)
        """
        self.database_name = database_name
        self.sql_executor = sql_executor
        self.execution_history = []
    
    @abstractmethod
    def get_engine_type(self) -> DatabaseType:
        """获取引擎类型"""
        pass
    
    @abstractmethod
    def get_engine_name(self) -> str:
        """获取引擎名称"""
        pass
    
    # ==================== SQL生成方法 ====================
    
    @abstractmethod
    def generate_create_table_sql(self, table_name: str, select_sql: str, 
                                if_not_exists: bool = True) -> str:
        """生成创建表的SQL"""
        pass
    
    @abstractmethod
    def generate_insert_sql(self, table_name: str, select_sql: str) -> str:
        """生成插入数据的SQL"""
        pass
    
    @abstractmethod
    def generate_drop_table_sql(self, table_name: str, if_exists: bool = True) -> str:
        """生成删除表的SQL"""
        pass
    
    def generate_aggregation_sql(self, schema, year: int, month: int, 
                               aggregation_types: List[str]) -> str:
        """生成聚合特征SQL (可被子类重写)"""
        base_table = self.get_full_table_name(schema.table_name)
        pk_field = schema.primary_key
        date_field = schema.date_field
        
        # 获取可聚合字段
        agg_fields = [field for field in schema.fields.values() if field.aggregatable]
        
        # 构建聚合选择语句
        select_parts = [pk_field, f"'{year}-{month:02d}-01' as feature_month"]
        
        for field in agg_fields:
            for agg_type in aggregation_types:
                alias = f"{field.name}_{agg_type}"
                select_parts.append(f"{agg_type.upper()}({field.name}) as {alias}")
        
        sql = f"""
        SELECT {', '.join(select_parts)}
        FROM {base_table}
        WHERE YEAR({date_field}) = {year} 
          AND MONTH({date_field}) = {month}
        GROUP BY {pk_field}
        """
        
        return sql.strip()
    
    # ==================== SQL执行方法 ====================
    
    def execute_sql(self, sql: str, description: str = "") -> Any:
        """
        执行SQL语句
        
        Args:
            sql: SQL语句
            description: 执行描述
            
        Returns:
            执行结果
        """
        if self.sql_executor:
            result = self.sql_executor(sql)
            self.execution_history.append({
                'sql': sql,
                'description': description,
                'timestamp': datetime.now(),
                'result': result
            })
            return result
        else:
            print(f"SQL (未执行): {description or 'SQL语句'}")
            print(f"  {sql[:100]}...")
            return None
    
    def create_table(self, table_name: str, select_sql: str, 
                    execute: bool = False) -> Dict[str, Any]:
        """
        创建表
        
        Args:
            table_name: 表名
            select_sql: 选择SQL
            execute: 是否立即执行
            
        Returns:
            操作结果
        """
        full_table_name = self.get_full_table_name(table_name)
        create_sql = self.generate_create_table_sql(full_table_name, select_sql)
        
        result = {
            'table_name': table_name,
            'full_table_name': full_table_name,
            'sql': create_sql,
            'executed': execute
        }
        
        if execute:
            exec_result = self.execute_sql(create_sql, f"创建表 {table_name}")
            result['execution_result'] = exec_result
            result['status'] = 'success' if exec_result is not None else 'simulated'
        else:
            result['status'] = 'prepared'
        
        return result
    
    # ==================== 数据下载方法 ====================
    
    @abstractmethod
    def download_table_data(self, table_name: str, output_path: str, 
                          **kwargs) -> Dict[str, Any]:
        """
        下载表数据 (子类必须实现)
        
        Args:
            table_name: 表名
            output_path: 输出路径
            **kwargs: 其他参数
            
        Returns:
            下载结果
        """
        pass
    
    def download_query_result(self, sql: str, output_path: str, 
                            **kwargs) -> Dict[str, Any]:
        """
        下载查询结果 (默认实现，子类可重写)
        
        Args:
            sql: 查询SQL
            output_path: 输出路径
            **kwargs: 其他参数
            
        Returns:
            下载结果
        """
        # 创建临时表然后下载
        temp_table = f"temp_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 创建临时表
            self.create_table(temp_table, sql, execute=True)
            
            # 下载数据
            result = self.download_table_data(temp_table, output_path, **kwargs)
            
            # 清理临时表
            self.drop_table(temp_table, execute=True)
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"下载查询结果失败: {str(e)}",
                'error': str(e)
            }
    
    # ==================== 工具方法 ====================
    
    def get_full_table_name(self, table_name: str) -> str:
        """获取完整的表名（包含数据库名）"""
        if '.' in table_name:
            return table_name  # 已经包含数据库名
        return f"{self.database_name}.{table_name}"
    
    def generate_table_name(self, base_name: str, year: int, month: int, 
                          suffix: str = "raw") -> str:
        """
        生成标准化的表名
        格式: {base_name}_{yyyy}_{MM}_{suffix}
        """
        return f"{base_name}_{year}_{month:02d}_{suffix}"
    
    def drop_table(self, table_name: str, execute: bool = False) -> Dict[str, Any]:
        """删除表"""
        full_table_name = self.get_full_table_name(table_name)
        drop_sql = self.generate_drop_table_sql(full_table_name)
        
        result = {
            'table_name': table_name,
            'full_table_name': full_table_name,
            'sql': drop_sql,
            'executed': execute
        }
        
        if execute:
            exec_result = self.execute_sql(drop_sql, f"删除表 {table_name}")
            result['execution_result'] = exec_result
            result['status'] = 'success' if exec_result is not None else 'simulated'
        else:
            result['status'] = 'prepared'
        
        return result
    
    def get_execution_history(self) -> List[Dict]:
        """获取SQL执行历史"""
        return self.execution_history.copy()
    
    def clear_history(self):
        """清空执行历史"""
        self.execution_history.clear()
    
    def __str__(self):
        return f"{self.__class__.__name__}(db={self.database_name}, type={self.get_engine_type().value})"
