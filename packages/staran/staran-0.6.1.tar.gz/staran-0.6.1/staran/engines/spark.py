#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Spark数据库引擎
实现Spark SQL的生成、执行和数据下载
"""

from typing import Dict, Any, Optional, List, Callable
from .base import BaseEngine, DatabaseType


class SparkEngine(BaseEngine):
    """Spark数据库引擎"""
    
    def __init__(self, database_name: str, sql_executor: Optional[Callable] = None):
        super().__init__(database_name, sql_executor)
    
    def get_engine_type(self) -> DatabaseType:
        return DatabaseType.SPARK
    
    def get_engine_name(self) -> str:
        return "Apache Spark"
    
    # ==================== SQL生成方法 ====================
    
    def generate_create_table_sql(self, table_name: str, select_sql: str, 
                                if_not_exists: bool = True) -> str:
        """生成Spark创建表的SQL"""
        if_not_exists_clause = "IF NOT EXISTS " if if_not_exists else ""
        
        return f"""
        CREATE TABLE {if_not_exists_clause}{table_name}
        USING DELTA
        AS (
            {select_sql}
        )
        """.strip()
    
    def generate_insert_sql(self, table_name: str, select_sql: str) -> str:
        """生成Spark插入数据的SQL"""
        return f"""
        INSERT INTO {table_name} (
            {select_sql}
        )
        """.strip()
    
    def generate_drop_table_sql(self, table_name: str, if_exists: bool = True) -> str:
        """生成Spark删除表的SQL"""
        if_exists_clause = "IF EXISTS " if if_exists else ""
        return f"DROP TABLE {if_exists_clause}{table_name}"
    
    def generate_aggregation_sql(self, schema, year: int, month: int, 
                               aggregation_types: List[str]) -> str:
        """生成Spark聚合特征SQL"""
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
    
    def generate_mom_sql(self, schema, year: int, month: int, 
                       periods: List[int] = [1]) -> str:
        """生成环比特征SQL"""
        base_table = self.get_full_table_name(schema.table_name)
        pk_field = schema.primary_key
        date_field = schema.date_field
        
        # 获取可聚合字段
        agg_fields = [f for f in schema.fields if f.aggregatable]
        
        # 构建环比查询
        select_parts = [
            f"curr.{pk_field}",
            f"curr.feature_month"
        ]
        
        for field in agg_fields:
            for period in periods:
                for agg_type in ['sum', 'avg']:
                    curr_field = f"curr.{field.name}_{agg_type}"
                    prev_field = f"prev{period}.{field.name}_{agg_type}"
                    
                    # 环比增长率
                    alias = f"{field.name}_{agg_type}_mom_{period}m"
                    select_parts.append(f"""
                        CASE 
                            WHEN {prev_field} IS NULL OR {prev_field} = 0 THEN NULL
                            ELSE ({curr_field} - {prev_field}) / {prev_field}
                        END as {alias}
                    """.strip())
                    
                    # 环比差值
                    diff_alias = f"{field.name}_{agg_type}_diff_{period}m"
                    select_parts.append(f"({curr_field} - {prev_field}) as {diff_alias}")
        
        # 构建FROM子句和JOIN
        from_clause = f"""
        FROM (
            SELECT {pk_field}, feature_month, {', '.join([f'{f.name}_sum, {f.name}_avg' for f in agg_fields])}
            FROM {base_table}_aggregation_{year}_{month:02d}_1
        ) curr
        """
        
        for period in periods:
            prev_year = year
            prev_month = month - period
            if prev_month <= 0:
                prev_month += 12
                prev_year -= 1
            
            from_clause += f"""
        LEFT JOIN (
            SELECT {pk_field}, {', '.join([f'{f.name}_sum, {f.name}_avg' for f in agg_fields])}
            FROM {base_table}_aggregation_{prev_year}_{prev_month:02d}_1
        ) prev{period} ON curr.{pk_field} = prev{period}.{pk_field}
            """
        
        sql = f"SELECT {', '.join(select_parts)} {from_clause}"
        return sql.strip()
    
    # ==================== 数据下载方法 ====================
    
    def download_table_data(self, table_name: str, output_path: str, 
                          format: str = "parquet", mode: str = "overwrite",
                          **kwargs) -> Dict[str, Any]:
        """
        下载Spark表数据
        
        Args:
            table_name: 表名
            output_path: 输出路径
            format: 输出格式 (parquet, csv, json等)
            mode: 写入模式 (overwrite, append)
            **kwargs: 其他参数
            
        Returns:
            下载结果
        """
        full_table_name = self.get_full_table_name(table_name)
        
        # 构建Spark下载SQL/代码
        spark_code = f"""
        df = spark.sql("SELECT * FROM {full_table_name}")
        df.write.mode("{mode}").format("{format}").save("{output_path}")
        """
        
        try:
            if self.sql_executor:
                # 如果有执行器，尝试执行
                result = self.sql_executor(spark_code)
                return {
                    'status': 'success',
                    'message': f'数据已下载到: {output_path}',
                    'table_name': table_name,
                    'output_path': output_path,
                    'format': format,
                    'spark_code': spark_code,
                    'execution_result': result
                }
            else:
                # 模拟模式
                return {
                    'status': 'simulated',
                    'message': f'模拟下载到: {output_path}',
                    'table_name': table_name,
                    'output_path': output_path,
                    'format': format,
                    'spark_code': spark_code
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"下载失败: {str(e)}",
                'table_name': table_name,
                'error': str(e),
                'spark_code': spark_code
            }
    
    def download_query_result(self, sql: str, output_path: str, 
                            format: str = "parquet", mode: str = "overwrite",
                            **kwargs) -> Dict[str, Any]:
        """直接下载查询结果，不创建临时表"""
        spark_code = f"""
        df = spark.sql(\"\"\"
        {sql}
        \"\"\")
        df.write.mode("{mode}").format("{format}").save("{output_path}")
        """
        
        try:
            if self.sql_executor:
                result = self.sql_executor(spark_code)
                return {
                    'status': 'success',
                    'message': f'查询结果已下载到: {output_path}',
                    'output_path': output_path,
                    'format': format,
                    'spark_code': spark_code,
                    'execution_result': result
                }
            else:
                return {
                    'status': 'simulated',
                    'message': f'模拟下载查询结果到: {output_path}',
                    'output_path': output_path,
                    'format': format,
                    'spark_code': spark_code
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"下载查询结果失败: {str(e)}",
                'error': str(e),
                'spark_code': spark_code
            }
