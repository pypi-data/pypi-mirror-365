#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran REST API 服务模块 v1.0.10
==============================

提供HTTP API服务支持，用于远程调用Staran日期处理功能。

主要功能：
- REST API 服务器
- 日期处理API端点
- 数据验证和错误处理
- API文档生成
- 多种响应格式支持
"""

import json
import datetime
import traceback
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """API响应类"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now().isoformat()

class StaranAPIHandler(BaseHTTPRequestHandler):
    """Staran API 请求处理器"""
    
    def __init__(self, *args, **kwargs):
        # 导入核心模块
        try:
            from .core import Date
            from .lunar import LunarDate
            from .solar_terms import SolarTerms
            from .timezone import Timezone
            from .expressions import DateExpressionParser
            from .visualization import DateVisualization
            
            self.Date = Date
            self.LunarDate = LunarDate
            self.SolarTerms = SolarTerms
            self.Timezone = Timezone
            self.DateExpressionParser = DateExpressionParser
            self.DateVisualization = DateVisualization
        except ImportError as e:
            logger.error(f"导入模块失败: {e}")
        
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            query_params = parse_qs(parsed_path.query)
            
            # 路由分发
            if path == '/':
                self._handle_root()
            elif path == '/api/health':
                self._handle_health()
            elif path == '/api/date/create':
                self._handle_date_create(query_params)
            elif path == '/api/date/format':
                self._handle_date_format(query_params)
            elif path == '/api/date/calculate':
                self._handle_date_calculate(query_params)
            elif path == '/api/lunar/convert':
                self._handle_lunar_convert(query_params)
            elif path == '/api/solar-terms':
                self._handle_solar_terms(query_params)
            elif path == '/api/timezone/convert':
                self._handle_timezone_convert(query_params)
            elif path == '/api/expression/parse':
                self._handle_expression_parse(query_params)
            elif path == '/api/visualization/data':
                self._handle_visualization_data(query_params)
            elif path == '/api/docs':
                self._handle_api_docs()
            else:
                self._send_error_response(404, "API_NOT_FOUND", "API端点不存在")
                
        except Exception as e:
            logger.error(f"处理GET请求时出错: {e}")
            self._send_error_response(500, "INTERNAL_ERROR", str(e))
    
    def do_POST(self):
        """处理POST请求"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                request_data = json.loads(post_data) if post_data else {}
            except json.JSONDecodeError:
                self._send_error_response(400, "INVALID_JSON", "无效的JSON格式")
                return
            
            # 路由分发
            if path == '/api/date/batch':
                self._handle_date_batch(request_data)
            elif path == '/api/visualization/create':
                self._handle_visualization_create(request_data)
            else:
                self._send_error_response(404, "API_NOT_FOUND", "API端点不存在")
                
        except Exception as e:
            logger.error(f"处理POST请求时出错: {e}")
            self._send_error_response(500, "INTERNAL_ERROR", str(e))
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self._send_cors_headers()
        self.send_response(200)
        self.end_headers()
    
    def _send_response(self, response: APIResponse, status_code: int = 200):
        """发送API响应"""
        self._send_cors_headers()
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        response_json = json.dumps(asdict(response), ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_error_response(self, status_code: int, error_code: str, error_message: str):
        """发送错误响应"""
        response = APIResponse(
            success=False,
            error=error_message,
            error_code=error_code
        )
        self._send_response(response, status_code)
    
    def _send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def _get_param(self, params: Dict, key: str, default: Any = None, required: bool = False):
        """获取参数值"""
        if key in params:
            return params[key][0] if isinstance(params[key], list) else params[key]
        elif required:
            raise ValueError(f"缺少必需参数: {key}")
        else:
            return default
    
    # API端点处理方法
    def _handle_root(self):
        """处理根路径"""
        response = APIResponse(
            success=True,
            data={
                "name": "Staran API Server",
                "version": "1.0.10",
                "description": "Staran日期处理REST API服务",
                "endpoints": [
                    "/api/health",
                    "/api/date/create",
                    "/api/date/format", 
                    "/api/date/calculate",
                    "/api/date/batch",
                    "/api/lunar/convert",
                    "/api/solar-terms",
                    "/api/timezone/convert",
                    "/api/expression/parse",
                    "/api/visualization/data",
                    "/api/visualization/create",
                    "/api/docs"
                ]
            }
        )
        self._send_response(response)
    
    def _handle_health(self):
        """健康检查"""
        response = APIResponse(
            success=True,
            data={"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}
        )
        self._send_response(response)
    
    def _handle_date_create(self, params: Dict):
        """创建日期"""
        try:
            date_str = self._get_param(params, 'date', required=True)
            format_str = self._get_param(params, 'format')
            
            if format_str:
                date_obj = self.Date.from_string(date_str, format_str)
            else:
                date_obj = self.Date(date_str)
            
            response = APIResponse(
                success=True,
                data={
                    "date": date_obj.format_iso(),
                    "year": date_obj.year,
                    "month": date_obj.month,
                    "day": date_obj.day,
                    "weekday": date_obj.weekday(),
                    "formatted": {
                        "iso": date_obj.format_iso(),
                        "chinese": date_obj.format_chinese(),
                        "readable": date_obj.format_readable()
                    }
                }
            )
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "DATE_CREATE_ERROR", str(e))
    
    def _handle_date_format(self, params: Dict):
        """格式化日期"""
        try:
            date_str = self._get_param(params, 'date', required=True)
            format_type = self._get_param(params, 'format', 'iso')
            language = self._get_param(params, 'language', 'zh_CN')
            
            date_obj = self.Date(date_str)
            
            formatted_result = {}
            
            if format_type == 'iso':
                formatted_result['result'] = date_obj.format_iso()
            elif format_type == 'chinese':
                formatted_result['result'] = date_obj.format_chinese()
            elif format_type == 'readable':
                formatted_result['result'] = date_obj.format_readable()
            elif format_type == 'localized':
                self.Date.set_language(language)
                formatted_result['result'] = date_obj.format_localized()
            elif format_type == 'all':
                self.Date.set_language(language)
                formatted_result = {
                    'iso': date_obj.format_iso(),
                    'chinese': date_obj.format_chinese(),
                    'readable': date_obj.format_readable(),
                    'localized': date_obj.format_localized(),
                    'weekday': date_obj.format_weekday_localized(),
                    'month': date_obj.format_month_localized()
                }
            else:
                formatted_result['result'] = date_obj.format_custom(format_type)
            
            response = APIResponse(success=True, data=formatted_result)
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "DATE_FORMAT_ERROR", str(e))
    
    def _handle_date_calculate(self, params: Dict):
        """日期计算"""
        try:
            date_str = self._get_param(params, 'date', required=True)
            operation = self._get_param(params, 'operation', required=True)
            value = int(self._get_param(params, 'value', 0))
            
            date_obj = self.Date(date_str)
            
            if operation == 'add_days':
                result_date = date_obj.add_days(value)
            elif operation == 'add_months':
                result_date = date_obj.add_months(value)
            elif operation == 'add_years':
                result_date = date_obj.add_years(value)
            elif operation == 'subtract_days':
                result_date = date_obj.subtract_days(value)
            elif operation == 'subtract_months':
                result_date = date_obj.subtract_months(value)
            elif operation == 'subtract_years':
                result_date = date_obj.subtract_years(value)
            else:
                raise ValueError(f"不支持的操作: {operation}")
            
            response = APIResponse(
                success=True,
                data={
                    "original_date": date_obj.format_iso(),
                    "operation": operation,
                    "value": value,
                    "result_date": result_date.format_iso(),
                    "difference_days": result_date.calculate_days_difference(date_obj)
                }
            )
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "DATE_CALCULATE_ERROR", str(e))
    
    def _handle_date_batch(self, request_data: Dict):
        """批量日期处理"""
        try:
            dates = request_data.get('dates', [])
            operation = request_data.get('operation', 'format')
            options = request_data.get('options', {})
            
            results = []
            
            for date_str in dates:
                try:
                    date_obj = self.Date(date_str)
                    
                    if operation == 'format':
                        format_type = options.get('format', 'iso')
                        if format_type == 'iso':
                            result = date_obj.format_iso()
                        elif format_type == 'chinese':
                            result = date_obj.format_chinese()
                        else:
                            result = date_obj.format_custom(format_type)
                    elif operation == 'add_days':
                        days = options.get('days', 0)
                        result = date_obj.add_days(days).format_iso()
                    elif operation == 'to_lunar':
                        lunar = date_obj.to_lunar()
                        result = {
                            'year': lunar.year,
                            'month': lunar.month,
                            'day': lunar.day,
                            'formatted': lunar.format_chinese()
                        }
                    else:
                        result = date_obj.format_iso()
                    
                    results.append({
                        'input': date_str,
                        'result': result,
                        'success': True
                    })
                    
                except Exception as e:
                    results.append({
                        'input': date_str,
                        'error': str(e),
                        'success': False
                    })
            
            response = APIResponse(
                success=True,
                data={
                    'operation': operation,
                    'total_count': len(dates),
                    'success_count': sum(1 for r in results if r['success']),
                    'results': results
                }
            )
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "BATCH_PROCESS_ERROR", str(e))
    
    def _handle_lunar_convert(self, params: Dict):
        """农历转换"""
        try:
            date_str = self._get_param(params, 'date', required=True)
            direction = self._get_param(params, 'direction', 'solar_to_lunar')
            
            if direction == 'solar_to_lunar':
                date_obj = self.Date(date_str)
                lunar = date_obj.to_lunar()
                result = {
                    'solar_date': date_obj.format_iso(),
                    'lunar_year': lunar.year,
                    'lunar_month': lunar.month,
                    'lunar_day': lunar.day,
                    'lunar_formatted': lunar.format_chinese(),
                    'ganzhi_year': lunar.get_ganzhi_year(),
                    'zodiac': lunar.get_zodiac()
                }
            elif direction == 'lunar_to_solar':
                # 解析农历日期参数
                year = int(self._get_param(params, 'year', required=True))
                month = int(self._get_param(params, 'month', required=True))
                day = int(self._get_param(params, 'day', required=True))
                is_leap = self._get_param(params, 'is_leap', 'false').lower() == 'true'
                
                date_obj = self.Date.from_lunar(year, month, day, is_leap)
                result = {
                    'lunar_date': f"{year}-{month:02d}-{day:02d}",
                    'solar_date': date_obj.format_iso(),
                    'solar_formatted': date_obj.format_chinese()
                }
            else:
                raise ValueError(f"不支持的转换方向: {direction}")
            
            response = APIResponse(success=True, data=result)
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "LUNAR_CONVERT_ERROR", str(e))
    
    def _handle_solar_terms(self, params: Dict):
        """二十四节气查询"""
        try:
            year = int(self._get_param(params, 'year', datetime.date.today().year))
            term_name = self._get_param(params, 'term')
            
            if term_name:
                # 查询特定节气
                solar_term = self.SolarTerms.find_solar_term_by_name(year, term_name)
                if solar_term:
                    result = {
                        'name': solar_term.name,
                        'date': solar_term.date.strftime('%Y-%m-%d'),
                        'season': solar_term.season,
                        'description': solar_term.description,
                        'climate_features': solar_term.climate_features,
                        'traditional_activities': solar_term.traditional_activities,
                        'agricultural_guidance': solar_term.agricultural_guidance
                    }
                else:
                    raise ValueError(f"未找到节气: {term_name}")
            else:
                # 查询全年节气
                all_terms = self.SolarTerms.get_all_solar_terms(year)
                result = []
                for term in all_terms:
                    result.append({
                        'name': term.name,
                        'date': term.date.strftime('%Y-%m-%d'),
                        'season': term.season,
                        'description': term.description
                    })
            
            response = APIResponse(success=True, data=result)
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "SOLAR_TERMS_ERROR", str(e))
    
    def _handle_timezone_convert(self, params: Dict):
        """时区转换"""
        try:
            date_str = self._get_param(params, 'date', required=True)
            time_str = self._get_param(params, 'time', '00:00:00')
            from_tz = self._get_param(params, 'from_tz', required=True)
            to_tz = self._get_param(params, 'to_tz', required=True)
            
            # 解析日期时间
            date_part = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            time_part = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
            dt = datetime.datetime.combine(date_part, time_part)
            
            # 时区转换
            converted_dt = self.Timezone.convert_timezone(dt, from_tz, to_tz)
            
            result = {
                'original_datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'original_timezone': from_tz,
                'converted_datetime': converted_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'converted_timezone': to_tz,
                'timezone_info': {
                    'from': self.Timezone.get_timezone_display_info(from_tz),
                    'to': self.Timezone.get_timezone_display_info(to_tz)
                }
            }
            
            response = APIResponse(success=True, data=result)
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "TIMEZONE_CONVERT_ERROR", str(e))
    
    def _handle_expression_parse(self, params: Dict):
        """日期表达式解析"""
        try:
            expression = self._get_param(params, 'expression', required=True)
            
            parser = self.DateExpressionParser()
            parse_result = parser.parse(expression)
            
            if parse_result.success:
                result = {
                    'success': True,
                    'parsed_date': parse_result.date.strftime('%Y-%m-%d'),
                    'confidence': parse_result.confidence,
                    'matched_pattern': parse_result.matched_pattern,
                    'extracted_components': parse_result.extracted_components
                }
            else:
                result = {
                    'success': False,
                    'message': '无法解析表达式'
                }
            
            response = APIResponse(success=True, data=result)
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "EXPRESSION_PARSE_ERROR", str(e))
    
    def _handle_visualization_data(self, params: Dict):
        """获取可视化数据"""
        try:
            chart_type = self._get_param(params, 'type', required=True)
            library = self._get_param(params, 'library', 'echarts')
            
            viz = self.DateVisualization()
            
            if chart_type == 'calendar_heatmap':
                year = int(self._get_param(params, 'year', datetime.date.today().year))
                # 生成示例数据
                import random
                date_values = {}
                start_date = datetime.date(year, 1, 1)
                for i in range(365):
                    date = start_date + datetime.timedelta(days=i)
                    date_values[date] = random.randint(0, 100)
                
                chart_data = viz.create_calendar_heatmap(date_values, year, library)
                
            elif chart_type == 'solar_terms':
                year = int(self._get_param(params, 'year', datetime.date.today().year))
                chart_data = viz.create_solar_terms_chart(year, library)
                
            else:
                raise ValueError(f"不支持的图表类型: {chart_type}")
            
            response = APIResponse(success=True, data=asdict(chart_data))
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "VISUALIZATION_DATA_ERROR", str(e))
    
    def _handle_visualization_create(self, request_data: Dict):
        """创建可视化图表"""
        try:
            chart_type = request_data.get('type', 'timeline')
            library = request_data.get('library', 'echarts')
            data = request_data.get('data', [])
            
            viz = self.DateVisualization()
            
            if chart_type == 'timeline':
                dates = [datetime.datetime.strptime(item['date'], '%Y-%m-%d').date() for item in data]
                events = [item['event'] for item in data]
                chart_data = viz.create_timeline_data(dates, events, library)
                
            elif chart_type == 'time_series':
                from .visualization import TimeSeriesPoint
                time_series = []
                for item in data:
                    date = datetime.datetime.strptime(item['date'], '%Y-%m-%d').date()
                    value = item['value']
                    point = TimeSeriesPoint(date, value, item.get('label'), item.get('category'))
                    time_series.append(point)
                chart_data = viz.create_time_series_chart(time_series, library)
                
            else:
                raise ValueError(f"不支持的图表类型: {chart_type}")
            
            response = APIResponse(success=True, data=asdict(chart_data))
            self._send_response(response)
            
        except Exception as e:
            self._send_error_response(400, "VISUALIZATION_CREATE_ERROR", str(e))
    
    def _handle_api_docs(self):
        """API文档"""
        docs = {
            "title": "Staran Date API Documentation",
            "version": "1.0.10",
            "description": "完整的日期处理REST API服务",
            "endpoints": {
                "GET /api/health": {
                    "description": "健康检查",
                    "parameters": {},
                    "response": "健康状态信息"
                },
                "GET /api/date/create": {
                    "description": "创建日期对象",
                    "parameters": {
                        "date": "日期字符串 (必需)",
                        "format": "日期格式 (可选)"
                    },
                    "response": "日期对象信息"
                },
                "GET /api/date/format": {
                    "description": "格式化日期",
                    "parameters": {
                        "date": "日期字符串 (必需)",
                        "format": "格式类型 (iso|chinese|readable|localized|all)",
                        "language": "语言代码 (zh_CN|zh_TW|ja_JP|en_US)"
                    },
                    "response": "格式化后的日期"
                },
                "GET /api/date/calculate": {
                    "description": "日期计算",
                    "parameters": {
                        "date": "日期字符串 (必需)",
                        "operation": "操作类型 (add_days|add_months|add_years|subtract_days|subtract_months|subtract_years)",
                        "value": "计算值"
                    },
                    "response": "计算结果"
                },
                "POST /api/date/batch": {
                    "description": "批量日期处理",
                    "body": {
                        "dates": ["日期字符串数组"],
                        "operation": "操作类型",
                        "options": "操作选项"
                    },
                    "response": "批量处理结果"
                },
                "GET /api/lunar/convert": {
                    "description": "农历转换",
                    "parameters": {
                        "date": "日期字符串",
                        "direction": "转换方向 (solar_to_lunar|lunar_to_solar)",
                        "year": "农历年 (lunar_to_solar时必需)",
                        "month": "农历月 (lunar_to_solar时必需)",
                        "day": "农历日 (lunar_to_solar时必需)",
                        "is_leap": "是否闰月 (lunar_to_solar时可选)"
                    },
                    "response": "转换结果"
                },
                "GET /api/solar-terms": {
                    "description": "二十四节气查询",
                    "parameters": {
                        "year": "年份",
                        "term": "节气名称 (可选，不提供则返回全年)"
                    },
                    "response": "节气信息"
                },
                "GET /api/timezone/convert": {
                    "description": "时区转换",
                    "parameters": {
                        "date": "日期字符串 (必需)",
                        "time": "时间字符串 (HH:MM:SS)",
                        "from_tz": "源时区 (必需)",
                        "to_tz": "目标时区 (必需)"
                    },
                    "response": "时区转换结果"
                },
                "GET /api/expression/parse": {
                    "description": "日期表达式解析",
                    "parameters": {
                        "expression": "日期表达式 (必需)"
                    },
                    "response": "解析结果"
                },
                "GET /api/visualization/data": {
                    "description": "获取可视化数据",
                    "parameters": {
                        "type": "图表类型 (必需)",
                        "library": "图表库 (echarts|matplotlib|plotly|chartjs|highcharts)",
                        "year": "年份 (某些图表类型需要)"
                    },
                    "response": "图表数据"
                },
                "POST /api/visualization/create": {
                    "description": "创建可视化图表",
                    "body": {
                        "type": "图表类型",
                        "library": "图表库",
                        "data": "图表数据"
                    },
                    "response": "图表配置"
                }
            },
            "supported_timezones": self.Timezone.list_timezones() if hasattr(self, 'Timezone') else [],
            "supported_languages": ["zh_CN", "zh_TW", "ja_JP", "en_US"],
            "examples": {
                "create_date": "/api/date/create?date=2025-07-29",
                "format_chinese": "/api/date/format?date=2025-07-29&format=chinese",
                "solar_to_lunar": "/api/lunar/convert?date=2025-07-29&direction=solar_to_lunar",
                "parse_expression": "/api/expression/parse?expression=明天",
                "solar_terms": "/api/solar-terms?year=2025"
            }
        }
        
        response = APIResponse(success=True, data=docs)
        self._send_response(response)

class StaranAPIServer:
    """Staran API 服务器"""
    
    def __init__(self, host: str = 'localhost', port: int = 8000):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
    
    def start(self, background: bool = False):
        """启动服务器"""
        try:
            self.server = HTTPServer((self.host, self.port), StaranAPIHandler)
            logger.info(f"Staran API服务器启动在 http://{self.host}:{self.port}")
            
            if background:
                self.server_thread = threading.Thread(target=self.server.serve_forever)
                self.server_thread.daemon = True
                self.server_thread.start()
                logger.info("API服务器在后台运行")
            else:
                logger.info("按 Ctrl+C 停止服务器")
                self.server.serve_forever()
                
        except KeyboardInterrupt:
            logger.info("收到停止信号")
        except Exception as e:
            logger.error(f"启动服务器时出错: {e}")
        finally:
            if self.server:
                self.server.server_close()
    
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("API服务器已停止")
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)

# 便捷函数
def start_api_server(host: str = 'localhost', port: int = 8000, background: bool = False):
    """启动API服务器（便捷函数）"""
    server = StaranAPIServer(host, port)
    server.start(background)
    return server

def create_api_response(success: bool, data: Any = None, error: str = None, error_code: str = None) -> APIResponse:
    """创建API响应（便捷函数）"""
    return APIResponse(success=success, data=data, error=error, error_code=error_code)
