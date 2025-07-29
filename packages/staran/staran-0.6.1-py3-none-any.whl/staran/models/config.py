"""
模型配置管理模块

定义模型的核心配置信息，包括模型类型、参数、特征配置等
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class ModelType(Enum):
    """模型类型枚举"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression" 
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    ANOMALY_DETECTION = "anomaly_detection"
    RECOMMENDATION = "recommendation"


class ModelAlgorithm(Enum):
    """模型算法枚举"""
    # 分类算法
    LOGISTIC_REGRESSION = "logistic_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    SVM = "svm"
    NEURAL_NETWORK = "neural_network"
    
    # 回归算法
    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    LASSO_REGRESSION = "lasso_regression"
    
    # 聚类算法
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    HIERARCHICAL = "hierarchical"
    
    # 时间序列
    ARIMA = "arima"
    LSTM = "lstm"
    PROPHET = "prophet"


@dataclass
class FeatureConfig:
    """特征配置"""
    schema_name: str                    # 使用的schema名称 (如 'aum')
    table_types: List[str]              # 使用的表类型列表 (如 ['behavior', 'asset_avg'])
    feature_selection: bool = True      # 是否启用特征选择
    feature_engineering: bool = True    # 是否启用特征工程
    scaling: bool = True                # 是否启用特征缩放
    encoding: Dict[str, str] = field(default_factory=dict)  # 编码配置


@dataclass 
class ModelConfig:
    """模型配置类"""
    # 基本信息
    name: str                           # 模型名称
    model_type: ModelType               # 模型类型
    algorithm: ModelAlgorithm           # 使用的算法
    version: str = "1.0.0"              # 模型版本
    
    # 特征配置
    feature_config: FeatureConfig = None
    
    # 模型参数
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    
    # 训练配置
    training_config: Dict[str, Any] = field(default_factory=lambda: {
        'test_size': 0.2,
        'random_state': 42,
        'cross_validation': True,
        'cv_folds': 5
    })
    
    # 评估配置
    evaluation_metrics: List[str] = field(default_factory=list)
    
    # 银行特定配置
    bank_code: str = "generic"          # 银行代码
    business_domain: str = "generic"    # 业务领域
    
    # 元数据
    description: str = ""               # 模型描述
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"          # 创建者
    tags: List[str] = field(default_factory=list)
    
    # 部署配置
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if self.feature_config is None:
            self.feature_config = FeatureConfig(
                schema_name="generic",
                table_types=["base"]
            )
        
        # 根据模型类型设置默认评估指标
        if not self.evaluation_metrics:
            self.evaluation_metrics = self._get_default_metrics()
    
    def _get_default_metrics(self) -> List[str]:
        """根据模型类型获取默认评估指标"""
        if self.model_type == ModelType.CLASSIFICATION:
            return ['accuracy', 'precision', 'recall', 'f1_score', 'auc']
        elif self.model_type == ModelType.REGRESSION:
            return ['mae', 'mse', 'rmse', 'r2_score']
        elif self.model_type == ModelType.CLUSTERING:
            return ['silhouette_score', 'calinski_harabasz_score']
        else:
            return ['custom_metric']
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'model_type': self.model_type.value,
            'algorithm': self.algorithm.value,
            'version': self.version,
            'feature_config': {
                'schema_name': self.feature_config.schema_name,
                'table_types': self.feature_config.table_types,
                'feature_selection': self.feature_config.feature_selection,
                'feature_engineering': self.feature_config.feature_engineering,
                'scaling': self.feature_config.scaling,
                'encoding': self.feature_config.encoding
            },
            'hyperparameters': self.hyperparameters,
            'training_config': self.training_config,
            'evaluation_metrics': self.evaluation_metrics,
            'bank_code': self.bank_code,
            'business_domain': self.business_domain,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'tags': self.tags,
            'deployment_config': self.deployment_config
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfig':
        """从字典创建ModelConfig实例"""
        feature_config_data = data.get('feature_config', {})
        feature_config = FeatureConfig(
            schema_name=feature_config_data.get('schema_name', 'generic'),
            table_types=feature_config_data.get('table_types', ['base']),
            feature_selection=feature_config_data.get('feature_selection', True),
            feature_engineering=feature_config_data.get('feature_engineering', True),
            scaling=feature_config_data.get('scaling', True),
            encoding=feature_config_data.get('encoding', {})
        )
        
        return cls(
            name=data['name'],
            model_type=ModelType(data['model_type']),
            algorithm=ModelAlgorithm(data['algorithm']),
            version=data.get('version', '1.0.0'),
            feature_config=feature_config,
            hyperparameters=data.get('hyperparameters', {}),
            training_config=data.get('training_config', {}),
            evaluation_metrics=data.get('evaluation_metrics', []),
            bank_code=data.get('bank_code', 'generic'),
            business_domain=data.get('business_domain', 'generic'),
            description=data.get('description', ''),
            created_by=data.get('created_by', 'system'),
            tags=data.get('tags', []),
            deployment_config=data.get('deployment_config', {})
        )


def create_model_config(
    name: str,
    model_type: str,
    algorithm: str,
    schema_name: str = "generic",
    table_types: List[str] = None,
    bank_code: str = "generic",
    **kwargs
) -> ModelConfig:
    """
    创建模型配置的便捷函数
    
    Args:
        name: 模型名称
        model_type: 模型类型 
        algorithm: 算法名称
        schema_name: 使用的schema名称
        table_types: 使用的表类型列表
        bank_code: 银行代码
        **kwargs: 其他配置参数
        
    Returns:
        ModelConfig实例
    """
    if table_types is None:
        table_types = ["base"]
    
    feature_config = FeatureConfig(
        schema_name=schema_name,
        table_types=table_types
    )
    
    return ModelConfig(
        name=name,
        model_type=ModelType(model_type),
        algorithm=ModelAlgorithm(algorithm),
        feature_config=feature_config,
        bank_code=bank_code,
        **kwargs
    )


# 预定义的模型配置模板
PRESET_CONFIGS = {
    "aum_longtail_classification": {
        "model_type": "classification",
        "algorithm": "random_forest",
        "schema_name": "aum",
        "table_types": ["behavior", "asset_avg", "asset_config", "monthly_stat"],
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        },
        "description": "AUM长尾客户分类模型"
    },
    
    "customer_value_regression": {
        "model_type": "regression", 
        "algorithm": "gradient_boosting",
        "schema_name": "aum",
        "table_types": ["behavior", "asset_avg"],
        "hyperparameters": {
            "n_estimators": 150,
            "learning_rate": 0.1,
            "max_depth": 8
        },
        "description": "客户价值预测回归模型"
    }
}


def create_preset_config(preset_name: str, **overrides) -> ModelConfig:
    """
    基于预设模板创建模型配置
    
    Args:
        preset_name: 预设模板名称
        **overrides: 覆盖的配置参数
        
    Returns:
        ModelConfig实例
    """
    if preset_name not in PRESET_CONFIGS:
        raise ValueError(f"未知的预设配置: {preset_name}")
    
    config = PRESET_CONFIGS[preset_name].copy()
    config.update(overrides)
    
    return create_model_config(
        name=preset_name,
        **config
    )
