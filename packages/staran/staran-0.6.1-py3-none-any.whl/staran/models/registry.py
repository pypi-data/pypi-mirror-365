"""
模型注册和管理模块

提供模型配置的注册、查询、版本管理等功能
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import os

from .config import ModelConfig
from .target import TargetDefinition


@dataclass
class ModelEntry:
    """模型注册条目"""
    model_config: ModelConfig
    target_definition: TargetDefinition
    registered_at: datetime
    status: str = "active"  # active, inactive, deprecated
    performance_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}


class ModelRegistry:
    """模型注册表"""
    
    _models: Dict[str, ModelEntry] = {}
    _version_history: Dict[str, List[str]] = {}  # 模型名称 -> 版本列表
    
    @classmethod
    def register(cls, model_config: ModelConfig, target_definition: TargetDefinition) -> str:
        """
        注册一个新模型
        
        Args:
            model_config: 模型配置
            target_definition: 目标变量定义
            
        Returns:
            模型的唯一标识符
        """
        model_id = f"{model_config.name}_{model_config.version}"
        
        # 检查是否已存在
        if model_id in cls._models:
            raise ValueError(f"模型 {model_id} 已存在")
        
        # 创建模型条目
        entry = ModelEntry(
            model_config=model_config,
            target_definition=target_definition,
            registered_at=datetime.now()
        )
        
        # 注册模型
        cls._models[model_id] = entry
        
        # 更新版本历史
        if model_config.name not in cls._version_history:
            cls._version_history[model_config.name] = []
        cls._version_history[model_config.name].append(model_config.version)
        
        print(f"✅ 模型 {model_id} 注册成功")
        return model_id
    
    @classmethod
    def get_model(cls, model_name: str, version: str = None) -> Optional[ModelEntry]:
        """
        获取模型条目
        
        Args:
            model_name: 模型名称
            version: 版本号，如果不指定则返回最新版本
            
        Returns:
            模型条目或None
        """
        if version:
            model_id = f"{model_name}_{version}"
            return cls._models.get(model_id)
        else:
            # 获取最新版本
            versions = cls._version_history.get(model_name, [])
            if not versions:
                return None
            
            latest_version = max(versions)  # 简单的字符串比较，实际应该用版本比较
            model_id = f"{model_name}_{latest_version}"
            return cls._models.get(model_id)
    
    @classmethod
    def get_model_config(cls, model_name: str, version: str = None) -> Optional[ModelConfig]:
        """获取模型配置"""
        entry = cls.get_model(model_name, version)
        return entry.model_config if entry else None
    
    @classmethod
    def get_target_definition(cls, model_name: str, version: str = None) -> Optional[TargetDefinition]:
        """获取目标变量定义"""
        entry = cls.get_model(model_name, version)
        return entry.target_definition if entry else None
    
    @classmethod
    def list_models(cls) -> List[Dict[str, Any]]:
        """列出所有注册的模型"""
        result = []
        for model_id, entry in cls._models.items():
            result.append({
                'model_id': model_id,
                'name': entry.model_config.name,
                'version': entry.model_config.version,
                'type': entry.model_config.model_type.value,
                'algorithm': entry.model_config.algorithm.value,
                'bank_code': entry.model_config.bank_code,
                'status': entry.status,
                'registered_at': entry.registered_at.isoformat(),
                'description': entry.model_config.description
            })
        return result
    
    @classmethod
    def list_versions(cls, model_name: str) -> List[str]:
        """列出模型的所有版本"""
        return cls._version_history.get(model_name, [])
    
    @classmethod
    def update_status(cls, model_name: str, status: str, version: str = None):
        """更新模型状态"""
        entry = cls.get_model(model_name, version)
        if entry:
            entry.status = status
            print(f"✅ 模型 {model_name} 状态更新为: {status}")
        else:
            print(f"❌ 模型 {model_name} 不存在")
    
    @classmethod
    def update_performance(cls, model_name: str, metrics: Dict[str, float], version: str = None):
        """更新模型性能指标"""
        entry = cls.get_model(model_name, version)
        if entry:
            entry.performance_metrics.update(metrics)
            print(f"✅ 模型 {model_name} 性能指标已更新")
        else:
            print(f"❌ 模型 {model_name} 不存在")
    
    @classmethod
    def get_model_summary(cls, model_name: str, version: str = None) -> Optional[Dict[str, Any]]:
        """获取模型详细信息摘要"""
        entry = cls.get_model(model_name, version)
        if not entry:
            return None
        
        model_config = entry.model_config
        target_def = entry.target_definition
        
        return {
            'basic_info': {
                'name': model_config.name,
                'version': model_config.version,
                'type': model_config.model_type.value,
                'algorithm': model_config.algorithm.value,
                'description': model_config.description,
                'created_by': model_config.created_by,
                'bank_code': model_config.bank_code
            },
            'feature_config': {
                'schema_name': model_config.feature_config.schema_name,
                'table_types': model_config.feature_config.table_types,
                'feature_selection': model_config.feature_config.feature_selection,
                'feature_engineering': model_config.feature_config.feature_engineering
            },
            'target_config': {
                'name': target_def.name,
                'type': target_def.target_type.value,
                'column': target_def.target_column,
                'description': target_def.description
            },
            'training_config': model_config.training_config,
            'hyperparameters': model_config.hyperparameters,
            'evaluation_metrics': model_config.evaluation_metrics,
            'registry_info': {
                'status': entry.status,
                'registered_at': entry.registered_at.isoformat(),
                'performance_metrics': entry.performance_metrics
            }
        }
    
    @classmethod
    def save_to_file(cls, filepath: str):
        """保存注册表到文件"""
        data = {
            'models': {},
            'version_history': cls._version_history,
            'saved_at': datetime.now().isoformat()
        }
        
        # 序列化模型数据
        for model_id, entry in cls._models.items():
            data['models'][model_id] = {
                'model_config': entry.model_config.to_dict(),
                'target_definition': entry.target_definition.to_dict(),
                'registered_at': entry.registered_at.isoformat(),
                'status': entry.status,
                'performance_metrics': entry.performance_metrics
            }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 模型注册表已保存到: {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str):
        """从文件加载注册表"""
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cls._version_history = data.get('version_history', {})
        cls._models = {}
        
        # 反序列化模型数据
        for model_id, entry_data in data.get('models', {}).items():
            model_config = ModelConfig.from_dict(entry_data['model_config'])
            target_definition = TargetDefinition(
                **entry_data['target_definition']
            )
            
            entry = ModelEntry(
                model_config=model_config,
                target_definition=target_definition,
                registered_at=datetime.fromisoformat(entry_data['registered_at']),
                status=entry_data.get('status', 'active'),
                performance_metrics=entry_data.get('performance_metrics', {})
            )
            
            cls._models[model_id] = entry
        
        print(f"✅ 从 {filepath} 加载了 {len(cls._models)} 个模型")


# 便捷函数
def register_model(model_config: ModelConfig, target_definition: TargetDefinition) -> str:
    """注册模型的便捷函数"""
    return ModelRegistry.register(model_config, target_definition)


def get_model_config(model_name: str, version: str = None) -> Optional[ModelConfig]:
    """获取模型配置的便捷函数"""
    return ModelRegistry.get_model_config(model_name, version)


def get_target_definition(model_name: str, version: str = None) -> Optional[TargetDefinition]:
    """获取目标变量定义的便捷函数"""
    return ModelRegistry.get_target_definition(model_name, version)


def list_available_models() -> List[Dict[str, Any]]:
    """列出可用模型的便捷函数"""
    return ModelRegistry.list_models()


def save_model_registry(filepath: str = "./models/model_registry.json"):
    """保存模型注册表的便捷函数"""
    ModelRegistry.save_to_file(filepath)


def load_model_registry(filepath: str = "./models/model_registry.json"):
    """加载模型注册表的便捷函数"""
    ModelRegistry.load_from_file(filepath)
