"""
Staran Schemas模块 - 新疆工行代发长尾客户表结构定义

提供新疆工行代发长尾客户的标准化表结构定义和字段管理功能。

主要功能:
- 代发长尾客户表结构定义
- 业务字段含义管理  
- 新疆工行专用配置
- 表结构文档生成
"""

from ..tools.document_generator import SchemaDocumentGenerator
from .aum import *

__all__ = [
    'SchemaDocumentGenerator',
    # 新疆工行代发长尾客户表
    'XinjiangICBCDaifaLongtailBehaviorSchema',
    'XinjiangICBCDaifaLongtailAssetAvgSchema', 
    'XinjiangICBCDaifaLongtailAssetConfigSchema',
    'XinjiangICBCDaifaLongtailMonthlyStatSchema',
    'get_xinjiang_icbc_daifa_longtail_schemas',
    'export_xinjiang_icbc_daifa_longtail_docs'
]

__version__ = "0.6.0"
