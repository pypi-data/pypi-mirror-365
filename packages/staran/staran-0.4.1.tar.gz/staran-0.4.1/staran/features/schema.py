#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
表结构定义模块
定义数据库表的字段、类型和分析特性
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


class FieldType(Enum):
    """字段类型枚举"""
    STRING = "string"
    INTEGER = "int"
    BIGINT = "bigint" 
    DECIMAL = "decimal"
    DOUBLE = "double"
    FLOAT = "float"
    DATE = "date"
    TIMESTAMP = "timestamp"
    BOOLEAN = "boolean"


@dataclass
class Field:
    """字段定义"""
    name: str
    field_type: FieldType
    is_primary_key: bool = False
    is_date_field: bool = False
    aggregatable: bool = False
    nullable: bool = True
    comment: str = ""
    
    def __post_init__(self):
        """初始化后处理"""
        # 数值类型默认可聚合
        if self.field_type in [FieldType.INTEGER, FieldType.BIGINT, 
                              FieldType.DECIMAL, FieldType.DOUBLE, FieldType.FLOAT]:
            if not hasattr(self, '_aggregatable_set'):
                self.aggregatable = True
                
    def set_aggregatable(self, aggregatable: bool):
        """设置是否可聚合"""
        self.aggregatable = aggregatable
        self._aggregatable_set = True
        return self


class TableSchema:
    """表结构定义类"""
    
    def __init__(self, table_name: str, comment: str = ""):
        """
        初始化表结构
        
        Args:
            table_name: 表名
            comment: 表注释
        """
        self.table_name = table_name
        self.comment = comment
        self.fields: Dict[str, Field] = {}
        self.primary_key: Optional[str] = None
        self.date_field: Optional[str] = None
        self.is_monthly_unique: bool = False
        
    def add_field(self, name: str, field_type: Union[str, FieldType], 
                  aggregatable: bool = None, nullable: bool = True, 
                  comment: str = "") -> 'TableSchema':
        """
        添加字段
        
        Args:
            name: 字段名
            field_type: 字段类型
            aggregatable: 是否可聚合（None时自动判断）
            nullable: 是否可空
            comment: 字段注释
            
        Returns:
            self: 支持链式调用
        """
        if isinstance(field_type, str):
            field_type = FieldType(field_type.lower())
            
        field = Field(
            name=name,
            field_type=field_type,
            nullable=nullable,
            comment=comment
        )
        
        if aggregatable is not None:
            field.set_aggregatable(aggregatable)
            
        self.fields[name] = field
        return self
        
    def add_primary_key(self, name: str, field_type: Union[str, FieldType],
                       comment: str = "主键") -> 'TableSchema':
        """添加主键字段"""
        if isinstance(field_type, str):
            field_type = FieldType(field_type.lower())
            
        field = Field(
            name=name,
            field_type=field_type,
            is_primary_key=True,
            nullable=False,
            comment=comment
        )
        field.set_aggregatable(False)
        
        self.fields[name] = field
        self.primary_key = name
        return self
        
    def add_date_field(self, name: str, field_type: Union[str, FieldType] = FieldType.DATE,
                      comment: str = "日期字段") -> 'TableSchema':
        """添加日期字段"""
        if isinstance(field_type, str):
            field_type = FieldType(field_type.lower())
            
        field = Field(
            name=name,
            field_type=field_type,
            is_date_field=True,
            nullable=False,
            comment=comment
        )
        field.set_aggregatable(False)
        
        self.fields[name] = field
        self.date_field = name
        return self
        
    def set_monthly_unique(self, is_unique: bool = True) -> 'TableSchema':
        """设置是否为每人每月唯一数据"""
        self.is_monthly_unique = is_unique
        return self
        
    def get_aggregatable_fields(self) -> List[Field]:
        """获取可聚合字段列表"""
        return [field for field in self.fields.values() if field.aggregatable]
        
    def get_non_aggregatable_fields(self) -> List[Field]:
        """获取不可聚合字段列表（用于原始拷贝）"""
        return [field for field in self.fields.values() 
                if not field.aggregatable and not field.is_primary_key and not field.is_date_field]
        
    def validate(self) -> bool:
        """验证表结构"""
        if not self.primary_key:
            raise ValueError("表必须定义主键")
            
        if not self.date_field:
            raise ValueError("表必须定义日期字段")
            
        if self.primary_key not in self.fields:
            raise ValueError(f"主键字段 {self.primary_key} 不存在")
            
        if self.date_field not in self.fields:
            raise ValueError(f"日期字段 {self.date_field} 不存在")
            
        return True
        
    def __str__(self) -> str:
        """字符串表示"""
        lines = [f"Table: {self.table_name}"]
        if self.comment:
            lines.append(f"Comment: {self.comment}")
            
        lines.append(f"Primary Key: {self.primary_key}")
        lines.append(f"Date Field: {self.date_field}")
        lines.append(f"Monthly Unique: {self.is_monthly_unique}")
        lines.append("Fields:")
        
        for field in self.fields.values():
            flag_str = ""
            if field.is_primary_key:
                flag_str += "[PK]"
            if field.is_date_field:
                flag_str += "[DATE]"
            if field.aggregatable:
                flag_str += "[AGG]"
                
            lines.append(f"  {field.name}: {field.field_type.value} {flag_str}")
            
        return "\n".join(lines)
