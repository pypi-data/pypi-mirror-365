"""
Staran Models Module - v0.5.0

专业的机器学习模型配置和管理模块，提供：
- 模型配置管理 (ModelConfig)
- 目标变量定义 (TargetDefinition) 
- 银行特定配置支持
- SQL驱动的target生成
- 模型部署和版本管理

支持的模型类型：
- 分类模型 (Classification)
- 回归模型 (Regression)
- 聚类模型 (Clustering)
- 时间序列模型 (TimeSeries)

支持的银行：
- 工商银行 (ICBC)
- 通用配置 (Generic)
"""

from .config import ModelConfig, ModelType, create_model_config
from .target import TargetDefinition, TargetType, create_target_definition
from .registry import ModelRegistry, register_model, get_model_config, save_model_registry
from .bank_configs import BankConfig, get_bank_config, register_bank_config

# 版本信息
__version__ = "0.5.0"

# 主要导出
__all__ = [
    # 模型配置
    'ModelConfig',
    'ModelType', 
    'create_model_config',
    
    # 目标定义
    'TargetDefinition',
    'TargetType',
    'create_target_definition',
    
    # 模型注册
    'ModelRegistry',
    'register_model',
    'get_model_config',
    'save_model_registry',
    
    # 银行配置
    'BankConfig',
    'get_bank_config', 
    'register_bank_config',
]

# 便捷函数
def create_icbc_model(model_name: str, model_type: str, target_sql: str, algorithm: str = "random_forest", **kwargs):
    """创建工商银行专用模型配置的便捷函数"""
    bank_config = get_bank_config('icbc')
    model_config = create_model_config(
        name=model_name,
        model_type=model_type,
        algorithm=algorithm,
        bank_code="icbc",
        **kwargs
    )
    
    target_config = create_target_definition(
        name=f"{model_name}_target",
        target_type="sql_based",
        sql_query=target_sql,
        bank_code="icbc"
    )
    
    return register_model(model_config, target_config)

def list_available_models():
    """列出所有可用的模型配置"""
    return ModelRegistry.list_models()

def get_model_summary(model_name: str):
    """获取模型配置摘要"""
    return ModelRegistry.get_model_summary(model_name)
