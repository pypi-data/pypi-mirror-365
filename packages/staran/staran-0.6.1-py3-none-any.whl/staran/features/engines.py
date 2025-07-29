#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL引擎模块
支持不同数据库引擎的SQL生成
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from enum import Enum
from .schema import TableSchema, Field, FieldType


class DatabaseType(Enum):
    """数据库类型枚举"""
    SPARK = "spark"
    HIVE = "hive"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


class BaseSQLGenerator(ABC):
    """SQL生成器基类"""
    
    def __init__(self, schema: TableSchema, config):
        self.schema = schema
        self.config = config
        
    @abstractmethod
    def generate(self) -> str:
        """生成SQL"""
        pass
        
    @abstractmethod
    def get_engine_name(self) -> str:
        """获取引擎名称"""
        pass


class SparkSQLGenerator(BaseSQLGenerator):
    """Spark SQL生成器"""
    
    def get_engine_name(self) -> str:
        return "Spark SQL"
        
    def generate(self) -> str:
        """生成Spark SQL"""
        if not self.schema.is_monthly_unique:
            return self._generate_basic_aggregation_sql()
        else:
            return self._generate_monthly_feature_sql()
            
    def _generate_basic_aggregation_sql(self) -> str:
        """生成基础聚合SQL（非每人每月唯一数据）"""
        base_table = self.schema.table_name
        pk_field = self.schema.primary_key
        date_field = self.schema.date_field
        
        # 基础字段选择
        select_parts = [
            f"    {pk_field}",
            f"    year({date_field}) as year",
            f"    month({date_field}) as month"
        ]
        
        # 原始字段拷贝
        if self.config.include_raw_copy:
            for field in self.schema.get_non_aggregatable_fields():
                select_parts.append(f"    first({field.name}) as {field.name}")
                
        # 聚合统计
        if self.config.include_aggregation:
            for field in self.schema.get_aggregatable_fields():
                for agg_type in self.config.aggregation_types:
                    if self._is_agg_applicable(field, agg_type):
                        agg_expr = self._get_spark_agg_expression(field.name, agg_type)
                        select_parts.append(f"    {agg_expr} as {field.name}_{agg_type}")
        
        sql = f"""-- Spark SQL: 基础聚合分析
-- 表: {self.schema.table_name}
-- 生成时间: {{current_timestamp}}

WITH base_data AS (
    SELECT
{',\\n'.join(select_parts)}
    FROM {base_table}
    GROUP BY {pk_field}, year({date_field}), month({date_field})
)

SELECT * FROM base_data
ORDER BY {pk_field}, year, month;"""
        
        return sql
        
    def _generate_monthly_feature_sql(self) -> str:
        """生成月度特征SQL（每人每月唯一数据）"""
        base_table = self.schema.table_name
        pk_field = self.schema.primary_key
        date_field = self.schema.date_field
        
        # 构建完整的特征SQL
        sql_parts = []
        
        # 1. 基础数据CTE
        sql_parts.append(self._build_base_data_cte())
        
        # 2. 聚合特征CTE
        if self.config.include_aggregation:
            sql_parts.append(self._build_aggregation_cte())
            
        # 3. 环比特征CTE
        if self.config.include_mom:
            sql_parts.append(self._build_mom_cte())
            
        # 4. 同比特征CTE
        if self.config.include_yoy:
            sql_parts.append(self._build_yoy_cte())
            
        # 5. 最终结果
        sql_parts.append(self._build_final_select())
        
        header = f"""-- Spark SQL: 月度特征工程
-- 表: {self.schema.table_name}
-- 每人每月唯一数据特征生成
-- 生成时间: {{current_timestamp}}
"""
        
        return header + ",\n\n".join(sql_parts)
        
    def _build_base_data_cte(self) -> str:
        """构建基础数据CTE"""
        pk_field = self.schema.primary_key
        date_field = self.schema.date_field
        
        select_parts = [
            f"    {pk_field}",
            f"    {date_field}",
            f"    year({date_field}) as year",
            f"    month({date_field}) as month",
            f"    date_format({date_field}, 'yyyy-MM') as year_month"
        ]
        
        # 添加所有其他字段
        for field in self.schema.fields.values():
            if not field.is_primary_key and not field.is_date_field:
                select_parts.append(f"    {field.name}")
                
        return f"""base_data AS (
    SELECT
{',\\n'.join(select_parts)}
    FROM {self.schema.table_name}
)"""

    def _build_aggregation_cte(self) -> str:
        """构建聚合特征CTE"""
        pk_field = self.schema.primary_key
        
        select_parts = [
            f"    {pk_field}",
            "    year_month"
        ]
        
        # 原始字段拷贝
        if self.config.include_raw_copy:
            for field in self.schema.get_non_aggregatable_fields():
                select_parts.append(f"    first({field.name}) as {field.name}")
                
        # 聚合统计特征
        for field in self.schema.get_aggregatable_fields():
            for agg_type in self.config.aggregation_types:
                if self._is_agg_applicable(field, agg_type):
                    agg_expr = self._get_spark_agg_expression(field.name, agg_type)
                    select_parts.append(f"    {agg_expr} as {field.name}_{agg_type}")
                    
        return f"""agg_features AS (
    SELECT
{',\\n'.join(select_parts)}
    FROM base_data
    GROUP BY {pk_field}, year_month
)"""

    def _build_mom_cte(self) -> str:
        """构建环比特征CTE"""
        pk_field = self.schema.primary_key
        
        select_parts = [f"    a.{pk_field}", "    a.year_month"]
        
        for field in self.schema.get_aggregatable_fields():
            for agg_type in self.config.aggregation_types:
                if self._is_agg_applicable(field, agg_type):
                    field_name = f"{field.name}_{agg_type}"
                    for months in self.config.mom_months:
                        mom_expr = f"a.{field_name} - lag(a.{field_name}, {months}) OVER (PARTITION BY a.{pk_field} ORDER BY a.year_month)"
                        select_parts.append(f"    {mom_expr} as {field_name}_mom_{months}m")
                        
        return f"""mom_features AS (
    SELECT
{',\\n'.join(select_parts)}
    FROM agg_features a
)"""

    def _build_yoy_cte(self) -> str:
        """构建同比特征CTE"""
        pk_field = self.schema.primary_key
        
        select_parts = [f"    a.{pk_field}", "    a.year_month"]
        
        for field in self.schema.get_aggregatable_fields():
            for agg_type in self.config.aggregation_types:
                if self._is_agg_applicable(field, agg_type):
                    field_name = f"{field.name}_{agg_type}"
                    for months in self.config.yoy_months:
                        yoy_expr = f"a.{field_name} - lag(a.{field_name}, {months}) OVER (PARTITION BY a.{pk_field} ORDER BY a.year_month)"
                        select_parts.append(f"    {yoy_expr} as {field_name}_yoy_{months}m")
                        
        return f"""yoy_features AS (
    SELECT
{',\\n'.join(select_parts)}
    FROM agg_features a
)"""

    def _build_final_select(self) -> str:
        """构建最终SELECT"""
        pk_field = self.schema.primary_key
        
        # 构建JOIN逻辑
        joins = []
        if self.config.include_mom:
            joins.append(f"LEFT JOIN mom_features m ON a.{pk_field} = m.{pk_field} AND a.year_month = m.year_month")
        if self.config.include_yoy:
            joins.append(f"LEFT JOIN yoy_features y ON a.{pk_field} = y.{pk_field} AND a.year_month = y.year_month")
            
        select_fields = ["a.*"]
        if self.config.include_mom:
            for field in self.schema.get_aggregatable_fields():
                for agg_type in self.config.aggregation_types:
                    if self._is_agg_applicable(field, agg_type):
                        for months in self.config.mom_months:
                            select_fields.append(f"m.{field.name}_{agg_type}_mom_{months}m")
                            
        if self.config.include_yoy:
            for field in self.schema.get_aggregatable_fields():
                for agg_type in self.config.aggregation_types:
                    if self._is_agg_applicable(field, agg_type):
                        for months in self.config.yoy_months:
                            select_fields.append(f"y.{field.name}_{agg_type}_yoy_{months}m")
        
        join_clause = "\n".join(joins) if joins else ""
        
        return f"""SELECT
    {',\\n    '.join(select_fields)}
FROM agg_features a
{join_clause}
ORDER BY a.{pk_field}, a.year_month"""

    def _get_spark_agg_expression(self, field_name: str, agg_type: str) -> str:
        """获取Spark聚合表达式"""
        agg_map = {
            'sum': f'sum({field_name})',
            'avg': f'avg({field_name})',
            'min': f'min({field_name})',
            'max': f'max({field_name})',
            'count': f'count({field_name})',
            'variance': f'variance({field_name})',
            'stddev': f'stddev({field_name})'
        }
        return agg_map.get(agg_type, f'{agg_type}({field_name})')
        
    def _is_agg_applicable(self, field: Field, agg_type: str) -> bool:
        """检查聚合类型是否适用于字段"""
        # COUNT适用于所有字段
        if agg_type == 'count':
            return True
            
        # 数值聚合仅适用于数值字段
        numeric_aggs = ['sum', 'avg', 'min', 'max', 'variance', 'stddev']
        if agg_type in numeric_aggs:
            return field.field_type in [
                FieldType.INTEGER, FieldType.BIGINT, FieldType.DECIMAL,
                FieldType.DOUBLE, FieldType.FLOAT
            ]
            
        return True
