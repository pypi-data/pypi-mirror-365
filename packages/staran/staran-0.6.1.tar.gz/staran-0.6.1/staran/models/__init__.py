"""
staran.models v0.6.0 - 新疆工行代发长尾客户模型管理

专门针对新疆工行代发长尾客户的两个核心模型：
1. 代发长尾客户提升3k预测模型 (daifa_longtail_upgrade_3k)
2. 代发长尾客户防流失1.5k预测模型 (daifa_longtail_churn_1_5k)

主要功能：
- 模型配置管理
- SQL驱动的目标变量定义
- 模型注册和版本控制
- 新疆工行特定配置
"""

from .config import ModelConfig, create_model_config
from .target import TargetDefinition, create_target_definition
from .registry import ModelRegistry, register_model, save_model_registry
from .daifa_models import (
    create_daifa_longtail_upgrade_model,
    create_daifa_longtail_churn_model,
    get_available_daifa_models,
    create_both_daifa_models
)

# 便捷函数
def create_xinjiang_icbc_models(output_dir: str = "./xinjiang_models") -> dict:
    """为新疆工行创建两个代发长尾客户模型"""
    return create_both_daifa_models(output_dir)

def list_available_models() -> list:
    """列出所有可用的代发长尾客户模型"""
    return get_available_daifa_models()

def get_model_summary() -> dict:
    """获取模型概述信息"""
    return {
        "version": "0.6.0",
        "bank": "新疆工行",
        "business_domain": "代发长尾客户",
        "models": [
            {
                "name": "daifa_longtail_upgrade_3k",
                "description": "预测下个月代发长尾客户资产提升3k的概率",
                "target_amount": 3000,
                "model_type": "binary_classification"
            },
            {
                "name": "daifa_longtail_churn_1_5k", 
                "description": "预测下个月代发长尾客户流失1.5k资产的风险",
                "target_amount": 1500,
                "model_type": "binary_classification"
            }
        ]
    }

__all__ = [
    # 核心组件
    'ModelConfig', 'TargetDefinition', 'ModelRegistry',
    
    # 创建函数
    'create_model_config', 'create_target_definition', 'register_model',
    
    # 代发长尾模型
    'create_daifa_longtail_upgrade_model', 'create_daifa_longtail_churn_model',
    'create_both_daifa_models', 'get_available_daifa_models',
    
    # 便捷函数
    'create_xinjiang_icbc_models', 'list_available_models', 'get_model_summary',
    'save_model_registry'
]

__version__ = "0.6.0"
