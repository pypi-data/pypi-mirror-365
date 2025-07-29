"""
目标变量定义模块

提供基于SQL的目标变量定义和生成功能
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import re


class TargetType(Enum):
    """目标变量类型"""
    BINARY_CLASSIFICATION = "binary_classification"    # 二分类
    MULTI_CLASSIFICATION = "multi_classification"      # 多分类
    REGRESSION = "regression"                           # 回归
    RANKING = "ranking"                                 # 排序
    CLUSTERING = "clustering"                           # 聚类
    SQL_BASED = "sql_based"                            # 基于SQL的自定义目标


class TargetEncoding(Enum):
    """目标变量编码方式"""
    NONE = "none"                    # 不编码
    LABEL_ENCODING = "label"         # 标签编码
    ONE_HOT = "one_hot"             # 独热编码
    ORDINAL = "ordinal"             # 序数编码
    BINARY = "binary"               # 二进制编码


@dataclass
class TargetDefinition:
    """目标变量定义类"""
    # 基本信息
    name: str                                   # 目标变量名称
    target_type: TargetType                     # 目标类型
    description: str = ""                       # 描述
    
    # SQL定义 (核心功能)
    sql_query: str = ""                         # 生成目标变量的SQL查询
    target_column: str = "target"               # 目标列名
    
    # 数据信息
    data_type: str = "float"                    # 数据类型
    encoding: TargetEncoding = TargetEncoding.NONE  # 编码方式
    
    # 分类相关
    class_labels: List[str] = field(default_factory=list)  # 类别标签
    class_weights: Dict[str, float] = field(default_factory=dict)  # 类别权重
    
    # 回归相关
    min_value: Optional[float] = None           # 最小值
    max_value: Optional[float] = None           # 最大值
    normalization: bool = False                 # 是否标准化
    
    # 时间相关
    time_window: str = ""                       # 时间窗口 (如 "30_days", "3_months")
    prediction_horizon: str = ""                # 预测时间范围
    
    # 银行特定
    bank_code: str = "generic"                  # 银行代码
    business_rules: Dict[str, Any] = field(default_factory=dict)  # 业务规则
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    
    # 验证配置
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.sql_query and self.target_type != TargetType.SQL_BASED:
            self.sql_query = self._generate_default_sql()
        
        # 验证SQL语法
        if self.sql_query:
            self._validate_sql()
    
    def _generate_default_sql(self) -> str:
        """根据目标类型生成默认SQL"""
        if self.target_type == TargetType.BINARY_CLASSIFICATION:
            return f"""
            SELECT party_id, 
                   CASE WHEN condition THEN 1 ELSE 0 END as {self.target_column}
            FROM source_table 
            WHERE data_dt = '{{data_dt}}'
            """
        elif self.target_type == TargetType.REGRESSION:
            return f"""
            SELECT party_id,
                   target_value as {self.target_column}
            FROM source_table
            WHERE data_dt = '{{data_dt}}'
            """
        else:
            return ""
    
    def _validate_sql(self):
        """验证SQL语法基本正确性"""
        sql = self.sql_query.strip().upper()
        
        # 基本SQL结构检查 (支持WITH语句)
        if not (sql.startswith('SELECT') or sql.startswith('WITH')):
            raise ValueError("SQL查询必须以SELECT或WITH开始")
        
        # 检查是否包含目标列
        if self.target_column.upper() not in sql:
            print(f"警告: SQL中未找到目标列 '{self.target_column}'")
        
        # 检查参数占位符
        placeholders = re.findall(r'\{(\w+)\}', self.sql_query)
        if placeholders:
            print(f"发现参数占位符: {placeholders}")
    
    def generate_sql(self, **params) -> str:
        """
        生成最终的SQL查询，替换参数占位符
        
        Args:
            **params: SQL参数字典
            
        Returns:
            最终的SQL查询字符串
        """
        sql = self.sql_query
        
        # 替换参数占位符
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            sql = sql.replace(placeholder, str(value))
        
        return sql
    
    def get_sample_sql(self, data_dt: str = "20250728") -> str:
        """获取示例SQL"""
        return self.generate_sql(data_dt=data_dt)
    
    def validate_target_values(self, values: List[Any]) -> bool:
        """验证目标值是否符合定义"""
        if self.target_type == TargetType.BINARY_CLASSIFICATION:
            unique_values = set(values)
            return unique_values.issubset({0, 1, 0.0, 1.0})
        
        elif self.target_type == TargetType.MULTI_CLASSIFICATION:
            if self.class_labels:
                unique_values = set(values)
                return unique_values.issubset(set(self.class_labels))
        
        elif self.target_type == TargetType.REGRESSION:
            if self.min_value is not None and self.max_value is not None:
                return all(self.min_value <= v <= self.max_value for v in values)
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'target_type': self.target_type.value,
            'description': self.description,
            'sql_query': self.sql_query,
            'target_column': self.target_column,
            'data_type': self.data_type,
            'encoding': self.encoding.value,
            'class_labels': self.class_labels,
            'class_weights': self.class_weights,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'normalization': self.normalization,
            'time_window': self.time_window,
            'prediction_horizon': self.prediction_horizon,
            'bank_code': self.bank_code,
            'business_rules': self.business_rules,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'version': self.version,
            'tags': self.tags,
            'validation_rules': self.validation_rules
        }


def create_target_definition(
    name: str,
    target_type: str,
    sql_query: str,
    target_column: str = "target",
    bank_code: str = "generic",
    **kwargs
) -> TargetDefinition:
    """
    创建目标变量定义的便捷函数
    
    Args:
        name: 目标变量名称
        target_type: 目标类型
        sql_query: SQL查询
        target_column: 目标列名
        bank_code: 银行代码
        **kwargs: 其他配置参数
        
    Returns:
        TargetDefinition实例
    """
    return TargetDefinition(
        name=name,
        target_type=TargetType(target_type),
        sql_query=sql_query,
        target_column=target_column,
        bank_code=bank_code,
        **kwargs
    )


# 预定义的目标变量模板
TARGET_TEMPLATES = {
    "aum_longtail_purchase": {
        "target_type": "binary_classification",
        "description": "AUM长尾客户未来购买预测",
        "sql_query": """
        SELECT 
            a.party_id,
            CASE 
                WHEN b.purchase_amount > 0 THEN 1 
                ELSE 0 
            END as target
        FROM 
            bi_hlwj_dfcw_f1_f4_wy a
        LEFT JOIN (
            SELECT party_id, SUM(productamount_sum) as purchase_amount
            FROM bi_hlwj_dfcw_f1_f4_wy
            WHERE data_dt BETWEEN '{start_dt}' AND '{end_dt}'
            GROUP BY party_id
        ) b ON a.party_id = b.party_id
        WHERE a.data_dt = '{feature_dt}'
        """,
        "target_column": "target",
        "time_window": "30_days",
        "class_labels": ["no_purchase", "purchase"]
    },
    
    "customer_value_prediction": {
        "target_type": "regression",
        "description": "客户价值预测",
        "sql_query": """
        SELECT 
            party_id,
            asset_total_bal as target
        FROM 
            bi_hlwj_zi_chan_avg_wy
        WHERE 
            data_dt = '{target_dt}'
        """,
        "target_column": "target",
        "data_type": "float",
        "normalization": True
    },
    
    "risk_level_classification": {
        "target_type": "multi_classification", 
        "description": "风险等级分类",
        "sql_query": """
        SELECT 
            party_id,
            CASE 
                WHEN asset_total_bal < 10000 THEN 'low_risk'
                WHEN asset_total_bal < 100000 THEN 'medium_risk'
                ELSE 'high_risk'
            END as target
        FROM 
            bi_hlwj_zi_chan_avg_wy
        WHERE 
            data_dt = '{data_dt}'
        """,
        "target_column": "target",
        "class_labels": ["low_risk", "medium_risk", "high_risk"]
    }
}


def create_preset_target(preset_name: str, **overrides) -> TargetDefinition:
    """
    基于预设模板创建目标变量定义
    
    Args:
        preset_name: 预设模板名称
        **overrides: 覆盖的配置参数
        
    Returns:
        TargetDefinition实例
    """
    if preset_name not in TARGET_TEMPLATES:
        raise ValueError(f"未知的目标变量模板: {preset_name}")
    
    template = TARGET_TEMPLATES[preset_name].copy()
    template.update(overrides)
    
    return create_target_definition(
        name=preset_name,
        **template
    )


def create_icbc_target(name: str, sql_query: str, target_type: str = "binary_classification", **kwargs) -> TargetDefinition:
    """创建工商银行专用目标变量定义"""
    return create_target_definition(
        name=name,
        target_type=target_type,
        sql_query=sql_query,
        bank_code="icbc",
        business_rules={
            "data_retention_days": 90,
            "privacy_compliance": True,
            "audit_required": True
        },
        **kwargs
    )
