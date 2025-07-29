"""
新疆工行代发长尾客户专用模型定义

包含两个核心模型：
1. 代发长尾客户提升3k预测模型
2. 代发长尾客户防流失1.5k预测模型

基于新疆工行代发长尾客户数据库和业务规则
"""

from typing import Dict, List
from .config import create_model_config
from .target import create_target_definition
from .registry import ModelRegistry, register_model
import os
import json
from datetime import datetime


def save_model_registry(output_path: str):
    """保存模型注册信息到文件"""
    
    def convert_to_serializable(obj):
        """递归转换对象为可序列化格式"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                result[key] = convert_to_serializable(value)
            return result
        elif hasattr(obj, 'value'):  # 枚举类型
            return obj.value
        elif isinstance(obj, (list, tuple)):
            return [convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        else:
            return obj
    
    data = {
        "models": {},
        "version_history": {},
        "saved_at": str(datetime.now())
    }
    
    # 获取所有注册的模型
    for model_id, entry in ModelRegistry._models.items():
        data["models"][model_id] = {
            "model_config": convert_to_serializable(entry.model_config),
            "target_definition": convert_to_serializable(entry.target_definition),
            "registered_at": entry.registered_at.isoformat(),
            "status": entry.status,
            "performance_metrics": entry.performance_metrics
        }
    
    data["version_history"] = ModelRegistry._version_history.copy()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 模型注册信息已保存到: {output_path}")
    return output_path


def create_daifa_longtail_upgrade_model() -> Dict:
    """创建代发长尾客户提升3k预测模型"""
    
    # 模型配置
    model_config = create_model_config(
        name="xinjiang_icbc_daifa_longtail_upgrade_3k",
        model_type="classification",
        algorithm="gradient_boosting",
        version="1.0.0",
        schema_name="daifa_longtail",
        table_types=["daifa_longtail_behavior", "daifa_longtail_asset_avg", 
                    "daifa_longtail_asset_config", "daifa_longtail_monthly_stat"],
        hyperparameters={
            "n_estimators": 300,
            "learning_rate": 0.05,
            "max_depth": 12,
            "min_samples_split": 20,
            "min_samples_leaf": 10,
            "subsample": 0.8,
            "random_state": 42
        },
        bank_code="xinjiang_icbc",
        business_domain="代发长尾客户",
        description="新疆工行代发长尾客户下个月资产提升3k预测模型",
        tags=["daifa", "longtail", "upgrade", "3k", "xinjiang_icbc"]
    )
    
    # 目标定义 - 预测下个月提升3k
    target_definition = create_target_definition(
        name="daifa_longtail_upgrade_3k_target",
        target_type="binary_classification",
        description="新疆工行代发长尾客户下个月资产提升3000元预测目标",
        sql_query="""
        WITH customer_baseline AS (
            -- 获取代发长尾客户基础信息（当月）
            SELECT 
                b.party_id,
                b.asset_total_bal as current_asset,
                b.salary_amount as current_salary,
                b.longtail_score,
                b.upgrade_potential,
                CASE 
                    WHEN b.asset_total_bal BETWEEN 10000 AND 100000 THEN 1 
                    ELSE 0 
                END as is_daifa_longtail
            FROM xinjiang_icbc_daifa_hlwj_monthly_stat_wy b
            WHERE b.data_dt = '{baseline_date}'
        ),
        
        next_month_performance AS (
            -- 计算下个月的资产变化
            SELECT 
                party_id,
                asset_total_bal as next_month_asset,
                salary_amount as next_month_salary,
                monthly_deposit_amount,
                monthly_withdraw_amount
            FROM xinjiang_icbc_daifa_hlwj_monthly_stat_wy
            WHERE data_dt = '{next_month_date}'
        ),
        
        asset_change AS (
            -- 计算资产变化情况
            SELECT 
                cb.party_id,
                cb.current_asset,
                nmp.next_month_asset,
                (nmp.next_month_asset - cb.current_asset) as asset_change,
                nmp.monthly_deposit_amount,
                cb.upgrade_potential
            FROM customer_baseline cb
            INNER JOIN next_month_performance nmp ON cb.party_id = nmp.party_id
            WHERE cb.is_daifa_longtail = 1  -- 只关注代发长尾客户
        )
        
        SELECT 
            party_id,
            CASE 
                -- 代发长尾客户资产提升3k的判断标准
                WHEN asset_change >= 3000  -- 资产增长达到3000元
                     AND monthly_deposit_amount > asset_change * 0.7  -- 主要通过存入实现
                     AND upgrade_potential >= 0.6  -- 提升潜力评分较高
                THEN 1 
                ELSE 0 
            END as upgrade_3k_target,
            
            -- 辅助分析字段
            current_asset,
            next_month_asset,
            asset_change,
            monthly_deposit_amount,
            upgrade_potential
            
        FROM asset_change
        """,
        target_column="upgrade_3k_target",
        class_labels=["no_upgrade", "upgrade_3k"],
        class_weights={"no_upgrade": 1.0, "upgrade_3k": 2.5},  # 提升类样本权重更高
        time_window="1_month",
        prediction_horizon="1_month",
        bank_code="xinjiang_icbc",
        business_rules={
            "min_asset_threshold": 10000,      # 代发长尾最小资产
            "max_asset_threshold": 100000,     # 代发长尾最大资产
            "upgrade_target_amount": 3000,     # 提升目标金额
            "deposit_contribution_ratio": 0.7, # 存入贡献占比
            "min_upgrade_potential": 0.6       # 最小提升潜力
        }
    )
    
    return {
        "model_config": model_config,
        "target_definition": target_definition,
        "model_type": "upgrade_prediction"
    }


def create_daifa_longtail_churn_model() -> Dict:
    """创建代发长尾客户防流失1.5k预测模型"""
    
    # 模型配置
    model_config = create_model_config(
        name="xinjiang_icbc_daifa_longtail_churn_1_5k",
        model_type="classification",
        algorithm="random_forest",  # 防流失模型使用随机森林
        version="1.0.0",
        schema_name="daifa_longtail",
        table_types=["daifa_longtail_behavior", "daifa_longtail_asset_avg", 
                    "daifa_longtail_asset_config", "daifa_longtail_monthly_stat"],
        hyperparameters={
            "n_estimators": 200,
            "max_depth": 10,
            "min_samples_split": 15,
            "min_samples_leaf": 8,
            "max_features": "sqrt",
            "random_state": 42,
            "class_weight": "balanced"  # 处理不平衡数据
        },
        bank_code="xinjiang_icbc",
        business_domain="代发长尾客户",
        description="新疆工行代发长尾客户下个月流失1.5k资产风险预测模型",
        tags=["daifa", "longtail", "churn", "1_5k", "risk_prevention"]
    )
    
    # 目标定义 - 预测下个月流失1.5k风险
    target_definition = create_target_definition(
        name="daifa_longtail_churn_1_5k_target",
        target_type="binary_classification",
        description="新疆工行代发长尾客户下个月流失1500元资产风险预测目标",
        sql_query="""
        WITH customer_baseline AS (
            -- 获取代发长尾客户基础信息（当月）
            SELECT 
                b.party_id,
                b.asset_total_bal as current_asset,
                b.salary_amount as current_salary,
                b.longtail_score,
                b.churn_risk,
                b.login_days,
                CASE 
                    WHEN b.asset_total_bal BETWEEN 10000 AND 100000 THEN 1 
                    ELSE 0 
                END as is_daifa_longtail
            FROM xinjiang_icbc_daifa_hlwj_monthly_stat_wy b
            WHERE b.data_dt = '{baseline_date}'
        ),
        
        next_month_performance AS (
            -- 计算下个月的资产变化和行为
            SELECT 
                party_id,
                asset_total_bal as next_month_asset,
                monthly_withdraw_amount,
                login_days as next_month_login_days
            FROM xinjiang_icbc_daifa_hlwj_monthly_stat_wy
            WHERE data_dt = '{next_month_date}'
        ),
        
        churn_analysis AS (
            -- 分析流失风险情况
            SELECT 
                cb.party_id,
                cb.current_asset,
                nmp.next_month_asset,
                (cb.current_asset - nmp.next_month_asset) as asset_decrease,
                nmp.monthly_withdraw_amount,
                cb.churn_risk,
                cb.login_days,
                nmp.next_month_login_days
            FROM customer_baseline cb
            INNER JOIN next_month_performance nmp ON cb.party_id = nmp.party_id
            WHERE cb.is_daifa_longtail = 1  -- 只关注代发长尾客户
        )
        
        SELECT 
            party_id,
            CASE 
                -- 代发长尾客户流失1.5k的判断标准
                WHEN asset_decrease >= 1500  -- 资产减少达到1500元
                     AND monthly_withdraw_amount >= 1500  -- 主要通过取出导致
                     AND (
                         churn_risk >= 0.7  -- 流失风险评分高
                         OR next_month_login_days <= login_days * 0.5  -- 活跃度大幅下降
                     )
                THEN 1 
                ELSE 0 
            END as churn_1_5k_target,
            
            -- 辅助分析字段
            current_asset,
            next_month_asset,
            asset_decrease,
            monthly_withdraw_amount,
            churn_risk,
            login_days,
            next_month_login_days
            
        FROM churn_analysis
        """,
        target_column="churn_1_5k_target",
        class_labels=["no_churn", "churn_1_5k"],
        class_weights={"no_churn": 1.0, "churn_1_5k": 3.0},  # 流失类样本权重更高
        time_window="1_month",
        prediction_horizon="1_month",
        bank_code="xinjiang_icbc",
        business_rules={
            "min_asset_threshold": 10000,        # 代发长尾最小资产
            "max_asset_threshold": 100000,       # 代发长尾最大资产
            "churn_threshold_amount": 1500,      # 流失阈值金额
            "min_churn_risk": 0.7,               # 最小流失风险
            "activity_decline_ratio": 0.5        # 活跃度下降比例
        }
    )
    
    return {
        "model_config": model_config,
        "target_definition": target_definition,
        "model_type": "churn_prevention"
    }


def create_both_daifa_models(output_dir: str = "./xinjiang_models") -> Dict:
    """创建两个代发长尾客户模型并注册"""
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建提升模型
    upgrade_model = create_daifa_longtail_upgrade_model()
    upgrade_id = register_model(
        upgrade_model["model_config"], 
        upgrade_model["target_definition"]
    )
    
    # 创建防流失模型
    churn_model = create_daifa_longtail_churn_model()
    churn_id = register_model(
        churn_model["model_config"], 
        churn_model["target_definition"]
    )
    
    # 保存注册信息到指定目录
    registry_path = os.path.join(output_dir, "model_registry.json")
    save_model_registry(registry_path)
    
    return {
        "upgrade_model": {
            "model_id": upgrade_id,
            "config": upgrade_model["model_config"],
            "target": upgrade_model["target_definition"]
        },
        "churn_model": {
            "model_id": churn_id,
            "config": churn_model["model_config"],
            "target": churn_model["target_definition"]
        },
        "registry_path": registry_path,
        "output_dir": output_dir
    }


def get_available_daifa_models() -> List[str]:
    """获取所有可用的代发长尾客户模型"""
    return [
        "daifa_longtail_upgrade_3k",   # 代发长尾客户提升3k模型
        "daifa_longtail_churn_1_5k"    # 代发长尾客户防流失1.5k模型
    ]


# 导出函数
__all__ = [
    'create_daifa_longtail_upgrade_model',
    'create_daifa_longtail_churn_model', 
    'create_both_daifa_models',
    'get_available_daifa_models'
]
