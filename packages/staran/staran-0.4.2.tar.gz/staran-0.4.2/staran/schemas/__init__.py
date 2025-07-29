"""
Staran Schemas模块 - 数据表结构定义与文档生成

提供标准化的表结构定义、字段管理和文档生成功能。
支持根据表结构生成Markdown和PDF文档供业务方使用。

主要功能:
- 表结构标准化定义
- 业务字段含义管理  
- 文档自动生成 (MD/PDF)
- 多业务领域支持
"""

from .document_generator import SchemaDocumentGenerator
from .aum import *

__all__ = [
    'SchemaDocumentGenerator',
    # AUM业务表
    'AUMBehaviorSchema',
    'AUMAssetAvgSchema', 
    'AUMAssetConfigSchema',
    'AUMMonthlyStatSchema',
    'get_aum_schemas',
    'export_aum_docs'
]

__version__ = "0.3.0"
