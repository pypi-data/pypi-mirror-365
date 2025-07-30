#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran 集成功能模块
==================

包含与外部库和服务的集成功能：
- 数据可视化集成
- REST API服务器
"""

try:
    from .visualization import DateVisualization, ChartData, TimeSeriesPoint
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    DateVisualization = None
    ChartData = None
    TimeSeriesPoint = None

try:
    from .api_server import StaranAPIServer, StaranAPIHandler
    API_SERVER_AVAILABLE = True
except ImportError:
    API_SERVER_AVAILABLE = False
    StaranAPIServer = None
    StaranAPIHandler = None

__all__ = [
    'DateVisualization',
    'ChartData', 
    'TimeSeriesPoint',
    'StaranAPIServer',
    'StaranAPIHandler',
    'VISUALIZATION_AVAILABLE',
    'API_SERVER_AVAILABLE'
]
