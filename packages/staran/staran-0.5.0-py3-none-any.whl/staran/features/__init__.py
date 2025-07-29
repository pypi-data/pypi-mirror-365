# 特征工程核心模块

# 核心组件
from .schema import TableSchema, Field, FieldType
from .generator import FeatureGenerator, FeatureConfig, FeatureType, AggregationType
from .manager import FeatureManager, FeatureTableManager

# 引擎模块
from ..engines import DatabaseType, SparkEngine, HiveEngine, create_engine

# 图灵引擎 (可选导入)
try:
    from ..engines import TuringEngine, create_turing_engine
    _TURING_AVAILABLE = True
except ImportError:
    TuringEngine = None
    create_turing_engine = None
    _TURING_AVAILABLE = False

# 便利函数
def create_feature_manager(database_name: str, engine_type: str = "spark", 
                         **kwargs) -> FeatureManager:
    """创建特征管理器的便利函数"""
    return FeatureManager(database_name, engine_type, **kwargs)

def quick_create_and_download(database_name: str, table_name: str, year: int, month: int, 
                            save_path: str, engine_type: str = "turing", **kwargs):
    """快速创建和下载的便利函数"""
    if engine_type == "turing" and not _TURING_AVAILABLE:
        raise ImportError("图灵引擎不可用，请确保turingPythonLib已安装")
    
    manager = FeatureManager(database_name, engine_type, **kwargs)
    return manager.download_table_data(table_name, save_path)

# 主要导出
__all__ = [
    'TableSchema',
    'Field', 
    'FieldType',
    'FeatureGenerator',
    'FeatureConfig',
    'FeatureType',
    'AggregationType',
    'FeatureManager',
    'FeatureTableManager',
    'DatabaseType',
    'SparkEngine',
    'HiveEngine',
    'create_engine',
    'create_feature_manager'
]

# 如果图灵引擎可用，添加到导出
if _TURING_AVAILABLE:
    __all__.extend([
        'TuringEngine',
        'create_turing_engine',
        'quick_create_and_download'
    ])
