"""
银行特定配置模块

为不同银行提供定制化的配置和业务规则
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


class BankCode(Enum):
    """银行代码枚举"""
    ICBC = "icbc"           # 工商银行
    CCB = "ccb"             # 建设银行
    BOC = "boc"             # 中国银行
    ABC = "abc"             # 农业银行
    CMB = "cmb"             # 招商银行
    GENERIC = "generic"     # 通用配置


@dataclass
class BankConfig:
    """银行配置类"""
    # 基本信息
    bank_code: str                              # 银行代码
    bank_name: str                              # 银行名称
    region: str = "cn"                          # 地区代码
    
    # 数据库配置
    database_config: Dict[str, Any] = field(default_factory=dict)
    
    # 表名映射 (不同银行的表名可能不同)
    table_mappings: Dict[str, str] = field(default_factory=dict)
    
    # 字段映射 (不同银行的字段名可能不同)
    field_mappings: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    # 业务规则
    business_rules: Dict[str, Any] = field(default_factory=dict)
    
    # 合规要求
    compliance_rules: Dict[str, Any] = field(default_factory=dict)
    
    # 数据处理规则
    data_processing_rules: Dict[str, Any] = field(default_factory=dict)
    
    # 模型部署配置
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    
    # 特征工程配置
    feature_engineering_config: Dict[str, Any] = field(default_factory=dict)
    
    def get_table_name(self, standard_table: str) -> str:
        """获取银行特定的表名"""
        return self.table_mappings.get(standard_table, standard_table)
    
    def get_field_name(self, table: str, standard_field: str) -> str:
        """获取银行特定的字段名"""
        table_fields = self.field_mappings.get(table, {})
        return table_fields.get(standard_field, standard_field)
    
    def get_business_rule(self, rule_name: str, default=None):
        """获取业务规则"""
        return self.business_rules.get(rule_name, default)
    
    def validate_compliance(self, operation: str) -> bool:
        """验证操作是否符合合规要求"""
        compliance_checks = self.compliance_rules.get(operation, {})
        # 这里可以实现具体的合规检查逻辑
        return compliance_checks.get('enabled', True)


# 银行配置注册表
_BANK_CONFIGS: Dict[str, BankConfig] = {}


def register_bank_config(config: BankConfig):
    """注册银行配置"""
    _BANK_CONFIGS[config.bank_code] = config
    print(f"✅ 银行配置 {config.bank_code} ({config.bank_name}) 注册成功")


def get_bank_config(bank_code: str) -> Optional[BankConfig]:
    """获取银行配置"""
    return _BANK_CONFIGS.get(bank_code)


def list_bank_configs() -> List[Dict[str, str]]:
    """列出所有银行配置"""
    return [
        {
            'bank_code': config.bank_code,
            'bank_name': config.bank_name,
            'region': config.region
        }
        for config in _BANK_CONFIGS.values()
    ]


# 预定义银行配置
def create_icbc_config() -> BankConfig:
    """创建工商银行配置"""
    return BankConfig(
        bank_code="icbc",
        bank_name="中国工商银行",
        region="cn",
        
        database_config={
            "default_database": "dwegdata03000",
            "connection_pool_size": 10,
            "query_timeout": 300
        },
        
        table_mappings={
            "behavior_table": "bi_hlwj_dfcw_f1_f4_wy",
            "asset_avg_table": "bi_hlwj_zi_chan_avg_wy", 
            "asset_config_table": "bi_hlwj_zi_chang_month_total_zb",
            "monthly_stat_table": "bi_hlwj_realy_month_stat_wy"
        },
        
        field_mappings={
            "behavior_table": {
                "customer_id": "party_id",
                "date_field": "data_dt"
            }
        },
        
        business_rules={
            "data_retention_days": 90,
            "min_sample_size": 1000,
            "max_features": 500,
            "risk_threshold": 0.8,
            "aum_threshold": 100000,
            "longtail_definition": {
                "asset_threshold": 50000,
                "activity_threshold": 0.3
            }
        },
        
        compliance_rules={
            "data_export": {
                "enabled": True,
                "approval_required": True,
                "encryption_required": True
            },
            "model_deployment": {
                "enabled": True,
                "testing_required": True,
                "documentation_required": True
            },
            "feature_selection": {
                "enabled": True,
                "sensitive_data_allowed": False,
                "audit_trail_required": True
            }
        },
        
        data_processing_rules={
            "missing_value_strategy": "median",
            "outlier_detection": True,
            "outlier_threshold": 3.0,
            "feature_scaling": "standard",
            "categorical_encoding": "one_hot"
        },
        
        deployment_config={
            "platform": "turing",
            "environment": "production",
            "monitoring_enabled": True,
            "auto_scaling": True,
            "backup_required": True
        },
        
        feature_engineering_config={
            "time_windows": ["1_month", "3_months", "6_months", "1_year"],
            "aggregation_functions": ["sum", "avg", "max", "min", "std"],
            "interaction_features": True,
            "polynomial_features": False,
            "target_encoding": True
        }
    )


def create_generic_config() -> BankConfig:
    """创建通用银行配置"""
    return BankConfig(
        bank_code="generic",
        bank_name="通用银行配置",
        region="generic",
        
        database_config={
            "default_database": "default_db",
            "connection_pool_size": 5,
            "query_timeout": 180
        },
        
        table_mappings={
            "behavior_table": "customer_behavior",
            "asset_avg_table": "customer_assets",
            "asset_config_table": "asset_config", 
            "monthly_stat_table": "monthly_stats"
        },
        
        business_rules={
            "data_retention_days": 30,
            "min_sample_size": 100,
            "max_features": 100
        },
        
        compliance_rules={
            "data_export": {"enabled": True},
            "model_deployment": {"enabled": True}
        },
        
        data_processing_rules={
            "missing_value_strategy": "mean",
            "outlier_detection": False,
            "feature_scaling": "none"
        }
    )


# 初始化默认银行配置
def initialize_default_configs():
    """初始化默认银行配置"""
    # 注册工商银行配置
    register_bank_config(create_icbc_config())
    
    # 注册通用配置
    register_bank_config(create_generic_config())


# 自动初始化
initialize_default_configs()


# 新疆工行特定配置
def create_xinjiang_icbc_config() -> BankConfig:
    """创建新疆工商银行配置"""
    base_config = create_icbc_config()
    
    # 基于基础工行配置进行定制
    base_config.bank_code = "xinjiang_icbc"
    base_config.bank_name = "新疆工商银行"
    base_config.region = "xinjiang"
    
    # 新疆特定的业务规则
    base_config.business_rules.update({
        "regional_compliance": True,
        "minority_customer_support": True,
        "language_support": ["zh", "ug"],  # 中文和维吾尔语
        "timezone": "Asia/Urumqi",
        "currency_support": ["CNY"],
        "cross_border_transaction": True
    })
    
    # 新疆特定的数据处理规则
    base_config.data_processing_rules.update({
        "character_encoding": "utf-8",
        "regional_holidays": True,
        "time_zone_conversion": True
    })
    
    return base_config


# 注册新疆工行配置
register_bank_config(create_xinjiang_icbc_config())
