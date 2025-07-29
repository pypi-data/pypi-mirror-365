"""
新疆工行银行配置模块

专门针对新疆工行代发长尾客户的配置：
- 数据库表结构定义（代发长尾客户专用）
- 业务规则配置
- 模型配置（提升模型和防流失模型）

数据库: xinjiang_icbc_daifa_longtail
业务范围: 代发长尾客户
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass 
class XinjiangICBCConfig:
    """新疆工行配置类"""
    
    # 数据库配置
    database_name: str = "xinjiang_icbc_daifa_longtail"
    schema_name: str = "daifa_longtail"
    
    # 业务配置
    business_domain: str = "代发长尾客户"
    customer_segment: str = "代发长尾"
    
    # 模型配置
    available_models: List[str] = None
    
    # 业务规则
    longtail_asset_min: float = 10000  # 长尾客户最小资产
    longtail_asset_max: float = 100000  # 长尾客户最大资产
    upgrade_target: float = 3000  # 提升目标金额
    churn_threshold: float = 1500  # 流失阈值金额
    
    def __post_init__(self):
        if self.available_models is None:
            self.available_models = [
                "daifa_longtail_upgrade_3k",    # 代发长尾提升3k模型
                "daifa_longtail_churn_1_5k"     # 代发长尾防流失1.5k模型
            ]


def get_xinjiang_icbc_tables() -> Dict[str, str]:
    """获取新疆工行代发长尾客户表配置"""
    return {
        # 代发长尾客户行为表
        "daifa_longtail_behavior": "xinjiang_icbc_daifa_hlwj_dfcw_f1_f4_wy",
        
        # 代发长尾客户资产平均表  
        "daifa_longtail_asset_avg": "xinjiang_icbc_daifa_hlwj_zi_chan_avg_wy",
        
        # 代发长尾客户资产配置表
        "daifa_longtail_asset_config": "xinjiang_icbc_daifa_hlwj_zi_chan_config_wy",
        
        # 代发长尾客户月度统计表
        "daifa_longtail_monthly_stat": "xinjiang_icbc_daifa_hlwj_monthly_stat_wy"
    }


def get_xinjiang_icbc_models() -> Dict[str, Dict]:
    """获取新疆工行代发长尾客户模型配置"""
    return {
        "daifa_longtail_upgrade_3k": {
            "name": "代发长尾客户提升3k预测模型",
            "description": "预测下个月代发长尾客户资产提升3000元的概率",
            "target": "upgrade_3k_next_month",
            "model_type": "binary_classification",
            "business_objective": "识别有潜力提升资产的代发长尾客户",
            "target_threshold": 3000,
            "prediction_window": "1_month"
        },
        
        "daifa_longtail_churn_1_5k": {
            "name": "代发长尾客户防流失1.5k预测模型", 
            "description": "预测下个月代发长尾客户流失1500元资产的风险",
            "target": "churn_1_5k_next_month",
            "model_type": "binary_classification", 
            "business_objective": "识别有流失风险的代发长尾客户",
            "target_threshold": 1500,
            "prediction_window": "1_month"
        }
    }


# 创建默认配置实例
xinjiang_icbc_config = XinjiangICBCConfig()
