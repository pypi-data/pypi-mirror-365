"""
staran.banks - 银行配置模块

该模块包含不同银行的特定配置，包括：
- 数据库连接配置
- 表结构定义
- 业务规则设置
- 模型配置

支持的银行：
- xinjiang_icbc: 新疆工行配置

版本: 0.6.0
"""

from .xinjiang_icbc import (
    XinjiangICBCConfig,
    get_xinjiang_icbc_tables,
    get_xinjiang_icbc_models,
    xinjiang_icbc_config
)

__all__ = [
    'XinjiangICBCConfig',
    'xinjiang_icbc_config',
    'get_xinjiang_icbc_tables', 
    'get_xinjiang_icbc_models'
]

__version__ = "0.6.0"
