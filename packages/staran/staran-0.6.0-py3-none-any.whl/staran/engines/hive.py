#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hive数据库引擎
实现Hive SQL的生成、执行和数据下载
"""

from typing import Dict, Any, Optional, List, Callable
from .base import BaseEngine, DatabaseType


class HiveEngine(BaseEngine):
    """Hive数据库引擎"""
    
    def __init__(self, database_name: str, sql_executor: Optional[Callable] = None):
        super().__init__(database_name, sql_executor)
    
    def get_engine_type(self) -> DatabaseType:
        return DatabaseType.HIVE
    
    def get_engine_name(self) -> str:
        return "Apache Hive"
    
    # ==================== SQL生成方法 ====================
    
    def generate_create_table_sql(self, table_name: str, select_sql: str, 
                                if_not_exists: bool = True) -> str:
        """生成Hive创建表的SQL"""
        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        
        return f"""
        CREATE TABLE {if_not_exists_clause}{table_name}
        STORED AS PARQUET
        AS (
            {select_sql}
        )
        """.strip()
    
    def generate_insert_sql(self, table_name: str, select_sql: str) -> str:
        """生成Hive插入数据的SQL"""
        return f"""
        INSERT INTO TABLE {table_name} (
            {select_sql}
        )
        """.strip()
    
    def generate_drop_table_sql(self, table_name: str, if_exists: bool = True) -> str:
        """生成Hive删除表的SQL"""
        if_exists_clause = "IF EXISTS " if if_exists else ""
        return f"DROP TABLE {if_exists_clause}{table_name}"
    
    def generate_aggregation_sql(self, schema, year: int, month: int, 
                               aggregation_types: List[str]) -> str:
        """生成Hive聚合特征SQL"""
        base_table = self.get_full_table_name(schema.table_name)
        pk_field = schema.primary_key
        date_field = schema.date_field
        
        # 获取可聚合字段
        agg_fields = [field for field in schema.fields.values() if field.aggregatable]
        
        # 构建聚合选择语句
        select_parts = [
            pk_field, 
            f"'{year}-{month:02d}-01' as feature_month",
            f"COUNT(*) as record_count"
        ]
        
        for field in agg_fields:
            for agg_type in aggregation_types:
                alias = f"{field.name}_{agg_type}"
                if agg_type.lower() == 'sum':
                    select_parts.append(f"SUM(CAST({field.name} AS DOUBLE)) as {alias}")
                elif agg_type.lower() == 'avg':
                    select_parts.append(f"AVG(CAST({field.name} AS DOUBLE)) as {alias}")
                elif agg_type.lower() == 'count':
                    select_parts.append(f"COUNT({field.name}) as {alias}")
                elif agg_type.lower() == 'max':
                    select_parts.append(f"MAX(CAST({field.name} AS DOUBLE)) as {alias}")
                elif agg_type.lower() == 'min':
                    select_parts.append(f"MIN(CAST({field.name} AS DOUBLE)) as {alias}")
                else:
                    select_parts.append(f"{agg_type.upper()}({field.name}) as {alias}")
        
        sql = f"""
        SELECT {', '.join(select_parts)}
        FROM {base_table}
        WHERE year({date_field}) = {year} 
          AND month({date_field}) = {month}
        GROUP BY {pk_field}
        """.strip()
        
        return sql
    
    # ==================== 数据下载方法 ====================
    
    def download_table_data(self, table_name: str, output_path: str, 
                          format: str = "textfile", delimiter: str = "\t",
                          **kwargs) -> Dict[str, Any]:
        """
        下载Hive表数据
        
        Args:
            table_name: 表名
            output_path: 输出路径
            format: 输出格式 (textfile, parquet等)
            delimiter: 分隔符 (仅对textfile有效)
            **kwargs: 其他参数
            
        Returns:
            下载结果
        """
        full_table_name = self.get_full_table_name(table_name)
        
        # 构建Hive导出SQL
        if format.lower() == "textfile":
            export_sql = f"""
            INSERT OVERWRITE DIRECTORY '{output_path}'
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY '{delimiter}'
            SELECT * FROM {full_table_name}
            """
        else:
            # 对于其他格式，使用CREATE TABLE AS的方式
            temp_table = f"temp_export_{table_name.replace('.', '_')}"
            export_sql = f"""
            CREATE TABLE {temp_table}
            STORED AS {format.upper()}
            LOCATION '{output_path}'
            AS SELECT * FROM {full_table_name}
            """
        
        try:
            if self.sql_executor:
                result = self.sql_executor(export_sql)
                return {
                    'status': 'success',
                    'message': f'数据已导出到: {output_path}',
                    'table_name': table_name,
                    'output_path': output_path,
                    'format': format,
                    'export_sql': export_sql,
                    'execution_result': result
                }
            else:
                return {
                    'status': 'simulated',
                    'message': f'模拟导出到: {output_path}',
                    'table_name': table_name,
                    'output_path': output_path,
                    'format': format,
                    'export_sql': export_sql
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"导出失败: {str(e)}",
                'table_name': table_name,
                'error': str(e),
                'export_sql': export_sql
            }
