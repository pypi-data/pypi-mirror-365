#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
特征生成器模块
基于表结构生成各种数据分析特征
"""

from typing import List, Dict, Set, Optional
from datetime import datetime
from .schema import TableSchema, Field, FieldType
from .manager import FeatureManager, FeatureTableManager


class FeatureType:
    """特征类型常量"""
    RAW_COPY = "raw_copy"
    AGGREGATION = "aggregation"
    MOM = "mom"  # Month over Month
    YOY = "yoy"  # Year over Year
    
    @classmethod
    def get_all(cls) -> List[str]:
        """获取所有特征类型"""
        return [cls.RAW_COPY, cls.AGGREGATION, cls.MOM, cls.YOY]


class AggregationType:
    """聚合类型常量"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    VARIANCE = "variance"
    STDDEV = "stddev"
    
    @classmethod
    def get_all(cls) -> List[str]:
        """获取所有聚合类型"""
        return [cls.SUM, cls.AVG, cls.MIN, cls.MAX, cls.COUNT, cls.VARIANCE, cls.STDDEV]
    
    @classmethod
    def get_numeric_only(cls) -> List[str]:
        """获取仅适用于数值字段的聚合类型"""
        return [cls.SUM, cls.AVG, cls.MIN, cls.MAX, cls.VARIANCE, cls.STDDEV]


class FeatureConfig:
    """特征生成配置"""
    
    def __init__(self):
        # 默认只生成基础特征
        self.enabled_features = {
            FeatureType.RAW_COPY: True,
            FeatureType.AGGREGATION: True,
            FeatureType.MOM: False,  # 默认不生成
            FeatureType.YOY: False   # 默认不生成
        }
        
        # 聚合类型配置（默认只使用常用的）
        self.aggregation_types = [AggregationType.SUM, AggregationType.AVG, AggregationType.COUNT]
        
        # 环比和同比配置（默认只推一个周期）
        self.mom_periods = [1]  # 1个月环比
        self.yoy_periods = [1]  # 1年同比（12个月）
        
    def enable_feature(self, feature_type: str) -> 'FeatureConfig':
        """启用特征类型"""
        if feature_type in self.enabled_features:
            self.enabled_features[feature_type] = True
        return self
        
    def disable_feature(self, feature_type: str) -> 'FeatureConfig':
        """禁用特征类型"""
        if feature_type in self.enabled_features:
            self.enabled_features[feature_type] = False
        return self
        
    def set_aggregation_types(self, types: List[str]) -> 'FeatureConfig':
        """设置聚合类型"""
        self.aggregation_types = types
        return self
        
    def set_mom_periods(self, periods: List[int]) -> 'FeatureConfig':
        """设置环比周期"""
        self.mom_periods = periods
        return self
        
    def set_yoy_periods(self, periods: List[int]) -> 'FeatureConfig':
        """设置同比周期"""
        self.yoy_periods = periods
        return self
        
    def is_feature_enabled(self, feature_type: str) -> bool:
        """检查特征类型是否启用"""
        return self.enabled_features.get(feature_type, False)


class FeatureGenerator:
    """特征生成器"""
    
    def __init__(self, 
                 schema: TableSchema, 
                 feature_manager: Optional[FeatureManager] = None,
                 config: FeatureConfig = None):
        """
        初始化特征生成器
        
        Args:
            schema: 表结构定义
            feature_manager: SQL管理器（可选）
            config: 特征生成配置
        """
        self.schema = schema
        self.feature_manager = feature_manager
        self.config = config or FeatureConfig()
        
        # 验证表结构
        self.schema.validate()
        
        # 如果有SQL管理器，初始化特征表管理器
        self.table_manager = None
        if self.feature_manager:
            self.table_manager = FeatureTableManager(self.feature_manager)
        
    def generate_feature_by_type(self, 
                                feature_type: str,
                                year: int,
                                month: int,
                                feature_num: int = 1) -> Dict[str, str]:
        """
        按特征类型生成SQL
        
        Args:
            feature_type: 特征类型（raw_copy, aggregation, mom, yoy）
            year: 年份
            month: 月份
            feature_num: 特征编号
            
        Returns:
            Dict包含SQL和表名信息
        """
        if not self.config.is_feature_enabled(feature_type):
            raise ValueError(f"特征类型 {feature_type} 未启用")
            
        # 生成对应类型的SQL
        if feature_type == FeatureType.RAW_COPY:
            sql = self._generate_raw_copy_sql()
        elif feature_type == FeatureType.AGGREGATION:
            sql = self._generate_aggregation_sql()
        elif feature_type == FeatureType.MOM:
            sql = self._generate_mom_sql()
        elif feature_type == FeatureType.YOY:
            sql = self._generate_yoy_sql()
        else:
            raise ValueError(f"不支持的特征类型: {feature_type}")
        
        result = {
            'feature_type': feature_type,
            'sql': sql,
            'year': year,
            'month': month,
            'feature_num': feature_num
        }
        
        # 如果有SQL管理器，生成表名
        if self.feature_manager:
            table_name = self.feature_manager.generate_feature_table_name(
                self.schema.table_name, year, month, feature_num
            )
            result['table_name'] = table_name
            
        return result
    
    def create_feature_table(self,
                           feature_type: str,
                           year: int,
                           month: int,
                           feature_num: int = 1,
                           execute: bool = False) -> str:
        """
        创建特征表
        
        Args:
            feature_type: 特征类型
            year: 年份
            month: 月份
            feature_num: 特征编号
            execute: 是否立即执行
            
        Returns:
            特征表名
        """
        if not self.table_manager:
            raise ValueError("需要SQL管理器才能创建特征表")
            
        feature_info = self.generate_feature_by_type(feature_type, year, month, feature_num)
        
        return self.table_manager.create_feature_table(
            base_table=self.schema.table_name,
            year=year,
            month=month,
            feature_num=feature_num,
            sql=feature_info['sql'],
            execute=execute
        )
    
    def _generate_raw_copy_sql(self) -> str:
        """生成原始字段拷贝SQL"""
        pk_field = self.schema.primary_key
        date_field = self.schema.date_field
        
        select_parts = [
            f"    {pk_field}",
            f"    year({date_field}) as year",
            f"    month({date_field}) as month",
            f"    date_format({date_field}, 'yyyy-MM') as year_month"
        ]
        
        # 添加非聚合字段
        for field in self.schema.get_non_aggregatable_fields():
            select_parts.append(f"    first({field.name}) as {field.name}")
            
        base_table = self.feature_manager.get_full_table_name(self.schema.table_name) if self.feature_manager else self.schema.table_name
        
        return f"""SELECT
{',\\n'.join(select_parts)}
FROM {base_table}
GROUP BY {pk_field}, year({date_field}), month({date_field})
ORDER BY {pk_field}, year, month"""

    def _generate_aggregation_sql(self) -> str:
        """生成聚合统计SQL"""
        pk_field = self.schema.primary_key
        date_field = self.schema.date_field
        
        select_parts = [
            f"    {pk_field}",
            f"    year({date_field}) as year", 
            f"    month({date_field}) as month",
            f"    date_format({date_field}, 'yyyy-MM') as year_month"
        ]
        
        # 聚合统计特征
        for field in self.schema.get_aggregatable_fields():
            for agg_type in self.config.aggregation_types:
                if self._is_agg_applicable(field, agg_type):
                    agg_expr = self._get_agg_expression(field.name, agg_type)
                    select_parts.append(f"    {agg_expr} as {field.name}_{agg_type}")
                    
        base_table = self.feature_manager.get_full_table_name(self.schema.table_name) if self.feature_manager else self.schema.table_name
        
        return f"""SELECT
{',\\n'.join(select_parts)}
FROM {base_table}
GROUP BY {pk_field}, year({date_field}), month({date_field})
ORDER BY {pk_field}, year, month"""

    def _generate_mom_sql(self) -> str:
        """生成环比特征SQL"""
        if not self.schema.is_monthly_unique:
            raise ValueError("环比特征需要每人每月唯一数据")
            
        pk_field = self.schema.primary_key
        date_field = self.schema.date_field
        
        # 需要先有基础聚合数据
        base_sql = self._generate_aggregation_sql()
        
        select_parts = [
            f"    {pk_field}",
            "    year_month"
        ]
        
        # 环比特征
        for field in self.schema.get_aggregatable_fields():
            for agg_type in self.config.aggregation_types:
                if self._is_agg_applicable(field, agg_type):
                    field_name = f"{field.name}_{agg_type}"
                    for period in self.config.mom_periods:
                        mom_expr = f"{field_name} - lag({field_name}, {period}) OVER (PARTITION BY {pk_field} ORDER BY year_month)"
                        select_parts.append(f"    {mom_expr} as {field_name}_mom_{period}m")
                        
        return f"""WITH base_agg AS (
{base_sql}
)
SELECT
{',\\n'.join(select_parts)}
FROM base_agg
ORDER BY {pk_field}, year_month"""

    def _generate_yoy_sql(self) -> str:
        """生成同比特征SQL"""
        if not self.schema.is_monthly_unique:
            raise ValueError("同比特征需要每人每月唯一数据")
            
        pk_field = self.schema.primary_key
        
        # 需要先有基础聚合数据
        base_sql = self._generate_aggregation_sql()
        
        select_parts = [
            f"    {pk_field}",
            "    year_month"
        ]
        
        # 同比特征
        for field in self.schema.get_aggregatable_fields():
            for agg_type in self.config.aggregation_types:
                if self._is_agg_applicable(field, agg_type):
                    field_name = f"{field.name}_{agg_type}"
                    for period in self.config.yoy_periods:
                        months = period * 12  # 年转换为月
                        yoy_expr = f"{field_name} - lag({field_name}, {months}) OVER (PARTITION BY {pk_field} ORDER BY year_month)"
                        select_parts.append(f"    {yoy_expr} as {field_name}_yoy_{period}y")
                        
        return f"""WITH base_agg AS (
{base_sql}
)
SELECT
{',\\n'.join(select_parts)}
FROM base_agg
ORDER BY {pk_field}, year_month"""
        
    def generate_feature_list(self) -> Dict[str, List[str]]:
        """
        生成特征列表
        
        Returns:
            Dict[str, List[str]]: 按类型分组的特征列表
        """
        features = {
            'raw_copy': [],
            'aggregation': [],
            'mom': [],
            'yoy': []
        }
        
        # 1. 原始字段拷贝
        if self.config.is_feature_enabled(FeatureType.RAW_COPY):
            features['raw_copy'] = [
                field.name for field in self.schema.get_non_aggregatable_fields()
            ]
            
        # 2. 聚合统计特征
        if self.config.is_feature_enabled(FeatureType.AGGREGATION):
            for field in self.schema.get_aggregatable_fields():
                for agg_type in self.config.aggregation_types:
                    if self._is_agg_applicable(field, agg_type):
                        feature_name = f"{field.name}_{agg_type}"
                        features['aggregation'].append(feature_name)
                        
        # 3. 环比特征
        if self.config.is_feature_enabled(FeatureType.MOM) and self.schema.is_monthly_unique:
            for field in self.schema.get_aggregatable_fields():
                for agg_type in self.config.aggregation_types:
                    if self._is_agg_applicable(field, agg_type):
                        for period in self.config.mom_periods:
                            feature_name = f"{field.name}_{agg_type}_mom_{period}m"
                            features['mom'].append(feature_name)
                            
        # 4. 同比特征
        if self.config.is_feature_enabled(FeatureType.YOY) and self.schema.is_monthly_unique:
            for field in self.schema.get_aggregatable_fields():
                for agg_type in self.config.aggregation_types:
                    if self._is_agg_applicable(field, agg_type):
                        for period in self.config.yoy_periods:
                            feature_name = f"{field.name}_{agg_type}_yoy_{period}y"
                            features['yoy'].append(feature_name)
                            
        return features
        
    def _is_agg_applicable(self, field: Field, agg_type: str) -> bool:
        """检查聚合类型是否适用于字段"""
        # COUNT适用于所有字段
        if agg_type == AggregationType.COUNT:
            return True
            
        # 数值聚合仅适用于数值字段
        if agg_type in AggregationType.get_numeric_only():
            return field.field_type in [
                FieldType.INTEGER, FieldType.BIGINT, FieldType.DECIMAL,
                FieldType.DOUBLE, FieldType.FLOAT
            ]
            
        return True
        
    def _get_agg_expression(self, field_name: str, agg_type: str) -> str:
        """获取聚合表达式"""
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
        
    def generate_spark_sql(self) -> str:
        """生成Spark SQL（兼容旧接口）"""
        if not self.schema.is_monthly_unique:
            return self._generate_aggregation_sql()
        else:
            # 生成完整的特征SQL（包含所有启用的特征）
            return self._generate_complete_feature_sql()
            
    def _generate_complete_feature_sql(self) -> str:
        """生成完整的特征SQL"""
        base_table = self.feature_manager.get_full_table_name(self.schema.table_name) if self.feature_manager else self.schema.table_name
        pk_field = self.schema.primary_key
        date_field = self.schema.date_field
        
        sql_parts = []
        
        # 基础数据CTE
        sql_parts.append(self._build_base_data_cte())
        
        # 聚合特征CTE
        if self.config.is_feature_enabled(FeatureType.AGGREGATION):
            sql_parts.append(self._build_aggregation_cte())
            
        # 环比特征CTE
        if self.config.is_feature_enabled(FeatureType.MOM):
            sql_parts.append(self._build_mom_cte())
            
        # 同比特征CTE
        if self.config.is_feature_enabled(FeatureType.YOY):
            sql_parts.append(self._build_yoy_cte())
            
        # 最终结果
        sql_parts.append(self._build_final_select())
        
        header = f"""-- Spark SQL: 特征工程
-- 表: {self.schema.table_name}
-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return header + ",\n\n".join(sql_parts)
        
    def _build_base_data_cte(self) -> str:
        """构建基础数据CTE"""
        pk_field = self.schema.primary_key
        date_field = self.schema.date_field
        base_table = self.feature_manager.get_full_table_name(self.schema.table_name) if self.feature_manager else self.schema.table_name
        
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
    FROM {base_table}
)"""

    def _build_aggregation_cte(self) -> str:
        """构建聚合特征CTE"""
        pk_field = self.schema.primary_key
        
        select_parts = [
            f"    {pk_field}",
            "    year_month"
        ]
        
        # 原始字段拷贝
        if self.config.is_feature_enabled(FeatureType.RAW_COPY):
            for field in self.schema.get_non_aggregatable_fields():
                select_parts.append(f"    first({field.name}) as {field.name}")
                
        # 聚合统计特征
        for field in self.schema.get_aggregatable_fields():
            for agg_type in self.config.aggregation_types:
                if self._is_agg_applicable(field, agg_type):
                    agg_expr = self._get_agg_expression(field.name, agg_type)
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
                    for period in self.config.mom_periods:
                        mom_expr = f"a.{field_name} - lag(a.{field_name}, {period}) OVER (PARTITION BY a.{pk_field} ORDER BY a.year_month)"
                        select_parts.append(f"    {mom_expr} as {field_name}_mom_{period}m")
                        
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
                    for period in self.config.yoy_periods:
                        months = period * 12  # 年转换为月
                        yoy_expr = f"a.{field_name} - lag(a.{field_name}, {months}) OVER (PARTITION BY a.{pk_field} ORDER BY a.year_month)"
                        select_parts.append(f"    {yoy_expr} as {field_name}_yoy_{period}y")
                        
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
        if self.config.is_feature_enabled(FeatureType.MOM):
            joins.append(f"LEFT JOIN mom_features m ON a.{pk_field} = m.{pk_field} AND a.year_month = m.year_month")
        if self.config.is_feature_enabled(FeatureType.YOY):
            joins.append(f"LEFT JOIN yoy_features y ON a.{pk_field} = y.{pk_field} AND a.year_month = y.year_month")
            
        select_fields = ["a.*"]
        if self.config.is_feature_enabled(FeatureType.MOM):
            for field in self.schema.get_aggregatable_fields():
                for agg_type in self.config.aggregation_types:
                    if self._is_agg_applicable(field, agg_type):
                        for period in self.config.mom_periods:
                            select_fields.append(f"m.{field.name}_{agg_type}_mom_{period}m")
                            
        if self.config.is_feature_enabled(FeatureType.YOY):
            for field in self.schema.get_aggregatable_fields():
                for agg_type in self.config.aggregation_types:
                    if self._is_agg_applicable(field, agg_type):
                        for period in self.config.yoy_periods:
                            select_fields.append(f"y.{field.name}_{agg_type}_yoy_{period}y")
        
        join_clause = "\n".join(joins) if joins else ""
        
        return f"""SELECT
    {',\\n    '.join(select_fields)}
FROM agg_features a
{join_clause}
ORDER BY a.{pk_field}, a.year_month"""
        
    def get_feature_summary(self) -> Dict[str, int]:
        """获取特征统计摘要"""
        features = self.generate_feature_list()
        return {
            'total': sum(len(feature_list) for feature_list in features.values()),
            'raw_copy': len(features['raw_copy']),
            'aggregation': len(features['aggregation']),
            'mom': len(features['mom']),
            'yoy': len(features['yoy'])
        }
        
    def print_feature_summary(self):
        """打印特征摘要"""
        features = self.generate_feature_list()
        summary = self.get_feature_summary()
        
        print(f"特征生成摘要 - 表: {self.schema.table_name}")
        print("=" * 50)
        print(f"总特征数: {summary['total']}")
        print(f"原始拷贝: {summary['raw_copy']} (启用: {self.config.is_feature_enabled(FeatureType.RAW_COPY)})")
        print(f"聚合统计: {summary['aggregation']} (启用: {self.config.is_feature_enabled(FeatureType.AGGREGATION)})")
        print(f"环比特征: {summary['mom']} (启用: {self.config.is_feature_enabled(FeatureType.MOM)})")
        print(f"同比特征: {summary['yoy']} (启用: {self.config.is_feature_enabled(FeatureType.YOY)})")
        print()
        
        for category, feature_list in features.items():
            if feature_list:
                print(f"{category.upper()} ({len(feature_list)}):")
                for feature in feature_list[:5]:  # 只显示前5个
                    print(f"  - {feature}")
                if len(feature_list) > 5:
                    print(f"  ... 还有 {len(feature_list) - 5} 个特征")
                print()
