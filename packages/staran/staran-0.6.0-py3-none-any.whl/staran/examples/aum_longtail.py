"""
AUM代发长尾模型示例
基于Staran v0.3.0架构，使用schemas模块的预定义表结构
"""

from typing import Dict, Optional
from ..engines import create_turing_engine
from ..features import FeatureManager, FeatureConfig, FeatureType
from ..tools import Date
from ..schemas.aum import get_aum_schemas


class AUMLongtailExample:
    """AUM代发长尾模型示例类"""
    
    def __init__(self, database: str = "dwegdata03000"):
        """
        初始化AUM长尾模型示例
        
        Args:
            database: 数据库名称，默认为dwegdata03000
        """
        self.database = database
        self.engine = create_turing_engine(database)
        self.schemas = get_aum_schemas()  # 从schemas模块获取预定义的表结构
        
    def run(self, feature_date: Optional[str] = None, output_path: str = "file:///nfsHome/aum_longtail") -> Dict:
        """
        运行完整的AUM长尾模型特征工程
        
        Args:
            feature_date: 特征日期，格式为YYYYMM，默认为当前月
            output_path: 输出路径，默认为file:///nfsHome/aum_longtail
            
        Returns:
            包含所有结果的字典
        """
        if feature_date is None:
            feature_date = Date.today().format_compact()[:6]
        
        print(f"🚀 开始AUM长尾模型特征工程 - {feature_date}")
        print("="*60)
        
        results = {}
        
        # 步骤1: 生成A表特征（行为特征表）- 只生成原始拷贝和聚合特征
        print("📊 步骤1: 生成客户行为特征...")
        results['behavior'] = self._generate_behavior_features('behavior', feature_date)
        
        # 步骤2: 生成B表特征（资产平均值表）- 完整特征
        print("💰 步骤2: 生成资产平均值特征...")
        results['asset_avg'] = self._generate_full_features('asset_avg', feature_date)
        
        # 步骤3: 生成C表特征（资产配置表）- 完整特征  
        print("📈 步骤3: 生成资产配置特征...")
        results['asset_config'] = self._generate_full_features('asset_config', feature_date)
        
        # 步骤4: 生成D表特征（月度统计表）- 完整特征
        print("📋 步骤4: 生成月度统计特征...")
        results['monthly_stat'] = self._generate_full_features('monthly_stat', feature_date)
        
        # 步骤5: 导出特征表
        print("💾 步骤5: 导出特征表...")
        results['exports'] = self._export_features(feature_date, output_path)
        
        print("="*60)
        print("✅ AUM长尾模型特征工程完成！")
        return results
    
    def _generate_behavior_features(self, table_type: str, feature_date: str) -> Dict:
        """生成行为特征（A表）- 只生成原始拷贝和聚合特征"""
        schema = self.schemas[table_type]
        manager = FeatureManager(self.engine, self.database)
        
        # A表特征配置：只启用原始拷贝和聚合
        config = FeatureConfig()
        config.enable_feature(FeatureType.RAW_COPY)
        config.enable_feature(FeatureType.AGGREGATION)
        config.disable_feature(FeatureType.MOM)  # 不生成环比
        config.disable_feature(FeatureType.YOY)  # 不生成同比
        
        print(f"   🔧 生成{schema.table_name}的特征...")
        result = manager.generate_features(
            schema=schema,
            config=config,
            feature_date=feature_date
        )
        
        feature_count = manager.count_features(schema, config)
        print(f"   ✅ A表特征生成完成: {feature_count}个特征")
        return result
    
    def _generate_full_features(self, table_type: str, feature_date: str) -> Dict:
        """生成完整特征（B、C、D表）- 聚合+5个月环比+1年同比"""
        schema = self.schemas[table_type]
        manager = FeatureManager(self.engine, self.database)
        
        # B、C、D表特征配置：完整特征集
        config = FeatureConfig()
        config.enable_feature(FeatureType.AGGREGATION)
        config.enable_feature(FeatureType.MOM, mom_windows=[5])    # 5个月环比
        config.enable_feature(FeatureType.YOY, yoy_windows=[12])  # 1年同比
        
        print(f"   🔧 生成{schema.table_name}的特征...")
        result = manager.generate_features(
            schema=schema,
            config=config,
            feature_date=feature_date
        )
        
        feature_count = manager.count_features(schema, config)
        print(f"   ✅ {table_type}表特征生成完成: {feature_count}个特征")
        return result
    
    def _export_features(self, feature_date: str, output_path: str) -> Dict:
        """导出所有特征表到指定路径"""
        file_prefixes = {
            'behavior': 'aum_behavior_features',
            'asset_avg': 'aum_asset_avg_features',
            'asset_config': 'aum_asset_config_features',
            'monthly_stat': 'monthly_stat_features'
        }
        
        results = {}
        for table_type, file_prefix in file_prefixes.items():
            print(f"   💾 导出{table_type}表...")
            
            # 构建特征表名
            table_name = f"{self.schemas[table_type].table_name}_{feature_date}_f001"
            
            result = self.engine.download_table_data(
                table_name=f"{self.database}.{table_name}",
                output_path=f"{output_path}/{file_prefix}_{feature_date}.parquet",
                mode="cluster"
            )
            
            results[table_type] = result
            print(f"   ✅ 导出 {table_type}: {result.get('status', 'unknown')}")
        
        return results
    
    def get_summary(self) -> Dict:
        """获取示例摘要信息"""
        summary = {
            'database': self.database,
            'tables': {},
            'total_features': 0
        }
        
        for table_type, schema in self.schemas.items():
            try:
                manager = FeatureManager(self.engine, self.database)
                
                if table_type == 'behavior':
                    # A表只有原始拷贝和聚合特征
                    config = FeatureConfig()
                    config.enable_feature(FeatureType.RAW_COPY)
                    config.enable_feature(FeatureType.AGGREGATION)
                    config.disable_feature(FeatureType.MOM)
                    config.disable_feature(FeatureType.YOY)
                else:
                    # B、C、D表包含完整特征：聚合+5个月MoM+1年YoY
                    config = FeatureConfig()
                    config.enable_feature(FeatureType.AGGREGATION, mom_windows=[5], yoy_windows=[12])
                
                feature_count = manager.count_features(schema, config)
                summary['tables'][table_type] = {
                    'table_name': schema.table_name,
                    'field_count': len(schema.fields),
                    'feature_count': feature_count,
                    'features': {
                        'total': feature_count,
                        'aggregation': len(schema.fields),  # 估算
                        'mom': len(schema.fields) * 5 if table_type != 'behavior' else 0,
                        'yoy': len(schema.fields) * 1 if table_type != 'behavior' else 0
                    }
                }
                summary['total_features'] += feature_count
            except Exception as e:
                # 在模拟模式下返回预估数量
                base_fields = len(schema.fields)
                if table_type == 'behavior':
                    estimated_features = base_fields * 2  # 原始拷贝 + 聚合
                    agg_count = base_fields
                    mom_count = 0
                    yoy_count = 0
                else:
                    estimated_features = base_fields * 8  # 聚合 + MoM + YoY 组合
                    agg_count = base_fields
                    mom_count = base_fields * 5
                    yoy_count = base_fields * 1
                
                summary['tables'][table_type] = {
                    'table_name': schema.table_name,
                    'field_count': base_fields,
                    'feature_count': estimated_features,
                    'mode': 'estimated',
                    'features': {
                        'total': estimated_features,
                        'aggregation': agg_count,
                        'mom': mom_count,
                        'yoy': yoy_count
                    }
                }
                summary['total_features'] += estimated_features
        
        return summary


# 简化的API函数
def create_aum_example(database: str = "dwegdata03000") -> AUMLongtailExample:
    """
    一键创建AUM长尾模型示例
    
    Args:
        database: 数据库名称，默认为dwegdata03000
        
    Returns:
        AUMLongtailExample实例
    """
    return AUMLongtailExample(database)


def run_aum_example(feature_date: Optional[str] = None, 
                   database: str = "dwegdata03000",
                   output_path: str = "file:///nfsHome/aum_longtail") -> Dict:
    """
    一键运行AUM长尾模型特征工程
    
    Args:
        feature_date: 特征日期，格式为YYYYMM，默认为当前月
        database: 数据库名称，默认为dwegdata03000
        output_path: 输出路径，默认为file:///nfsHome/aum_longtail
        
    Returns:
        包含所有结果的字典
        
    Example:
        >>> results = run_aum_example('202507')
        >>> print(f"生成特征数: {len(results)}")
    """
    example = create_aum_example(database)
    return example.run(feature_date, output_path)


__all__ = [
    'AUMLongtailExample',
    'create_aum_example', 
    'run_aum_example'
]