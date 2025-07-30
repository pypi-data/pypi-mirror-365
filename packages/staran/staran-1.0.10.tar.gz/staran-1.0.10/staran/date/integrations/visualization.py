#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran 数据可视化集成模块 v1.0.10
==============================

提供与主流图表库的集成支持，用于日期数据的可视化。

主要功能：
- 日期时间轴生成
- 日期分布图数据
- 时间序列图表数据
- 日历热力图数据
- 多种图表库适配器
"""

import datetime
import json
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

@dataclass
class ChartData:
    """图表数据类"""
    chart_type: str
    title: str
    data: List[Dict[str, Any]]
    config: Dict[str, Any]
    library: str  # 目标图表库

@dataclass
class TimeSeriesPoint:
    """时间序列数据点"""
    date: datetime.date
    value: Union[int, float]
    label: Optional[str] = None
    category: Optional[str] = None

class DateVisualization:
    """日期数据可视化类"""
    
    def __init__(self):
        self.supported_libraries = ['echarts', 'matplotlib', 'plotly', 'chartjs', 'highcharts']
    
    def create_timeline_data(self, 
                           dates: List[datetime.date], 
                           events: List[str], 
                           library: str = 'echarts') -> ChartData:
        """创建时间轴数据"""
        if library not in self.supported_libraries:
            raise ValueError(f"不支持的图表库: {library}")
        
        if library == 'echarts':
            return self._create_echarts_timeline(dates, events)
        elif library == 'matplotlib':
            return self._create_matplotlib_timeline(dates, events)
        elif library == 'plotly':
            return self._create_plotly_timeline(dates, events)
        elif library == 'chartjs':
            return self._create_chartjs_timeline(dates, events)
        elif library == 'highcharts':
            return self._create_highcharts_timeline(dates, events)
    
    def create_calendar_heatmap(self, 
                              date_values: Dict[datetime.date, float],
                              year: int,
                              library: str = 'echarts') -> ChartData:
        """创建日历热力图数据"""
        if library == 'echarts':
            return self._create_echarts_calendar_heatmap(date_values, year)
        elif library == 'matplotlib':
            return self._create_matplotlib_calendar_heatmap(date_values, year)
        elif library == 'plotly':
            return self._create_plotly_calendar_heatmap(date_values, year)
        else:
            raise ValueError(f"日历热力图暂不支持 {library}")
    
    def create_time_series_chart(self, 
                               time_series: List[TimeSeriesPoint],
                               library: str = 'echarts') -> ChartData:
        """创建时间序列图表数据"""
        if library == 'echarts':
            return self._create_echarts_time_series(time_series)
        elif library == 'matplotlib':
            return self._create_matplotlib_time_series(time_series)
        elif library == 'plotly':
            return self._create_plotly_time_series(time_series)
        elif library == 'chartjs':
            return self._create_chartjs_time_series(time_series)
        elif library == 'highcharts':
            return self._create_highcharts_time_series(time_series)
    
    def create_date_distribution_chart(self, 
                                     dates: List[datetime.date],
                                     group_by: str = 'month',
                                     library: str = 'echarts') -> ChartData:
        """创建日期分布图表数据"""
        distribution = self._calculate_date_distribution(dates, group_by)
        
        if library == 'echarts':
            return self._create_echarts_distribution(distribution, group_by)
        elif library == 'matplotlib':
            return self._create_matplotlib_distribution(distribution, group_by)
        elif library == 'plotly':
            return self._create_plotly_distribution(distribution, group_by)
        elif library == 'chartjs':
            return self._create_chartjs_distribution(distribution, group_by)
    
    def create_lunar_calendar_view(self, 
                                 year: int,
                                 library: str = 'echarts') -> ChartData:
        """创建农历日历视图数据"""
        from .lunar import LunarDate
        
        lunar_data = []
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        
        current_date = start_date
        while current_date <= end_date:
            try:
                # 这里需要实现公历转农历的逻辑
                lunar_info = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'solar_date': current_date.strftime('%m-%d'),
                    'lunar_date': f"农历{current_date.month}-{current_date.day}",  # 简化
                    'is_festival': False,  # 需要实现节日判断
                    'is_solar_term': False  # 需要实现节气判断
                }
                lunar_data.append(lunar_info)
            except:
                pass
            current_date += datetime.timedelta(days=1)
        
        return ChartData(
            chart_type='lunar_calendar',
            title=f'{year}年农历日历',
            data=lunar_data,
            config={'year': year},
            library=library
        )
    
    def create_solar_terms_chart(self, 
                               year: int,
                               library: str = 'echarts') -> ChartData:
        """创建二十四节气图表数据"""
        from .solar_terms import SolarTerms
        
        solar_terms = SolarTerms.get_all_solar_terms(year)
        
        if library == 'echarts':
            data = []
            for term in solar_terms:
                data.append({
                    'name': term.name,
                    'date': term.date.strftime('%Y-%m-%d'),
                    'season': term.season,
                    'description': term.description,
                    'month': term.date.month,
                    'day': term.date.day
                })
            
            return ChartData(
                chart_type='solar_terms',
                title=f'{year}年二十四节气',
                data=data,
                config={
                    'type': 'timeline',
                    'year': year,
                    'seasons': ['春季', '夏季', '秋季', '冬季']
                },
                library=library
            )
    
    # ECharts 适配器方法
    def _create_echarts_timeline(self, dates: List[datetime.date], events: List[str]) -> ChartData:
        """创建 ECharts 时间轴数据"""
        data = []
        for date, event in zip(dates, events):
            data.append({
                'name': event,
                'value': date.strftime('%Y-%m-%d'),
                'symbol': 'circle',
                'symbolSize': 10
            })
        
        config = {
            'type': 'timeline',
            'xAxis': {'type': 'time'},
            'yAxis': {'type': 'category', 'data': events},
            'series': [{'type': 'scatter', 'data': data}]
        }
        
        return ChartData(
            chart_type='timeline',
            title='时间轴图表',
            data=data,
            config=config,
            library='echarts'
        )
    
    def _create_echarts_calendar_heatmap(self, date_values: Dict[datetime.date, float], year: int) -> ChartData:
        """创建 ECharts 日历热力图数据"""
        data = []
        for date, value in date_values.items():
            if date.year == year:
                data.append([date.strftime('%Y-%m-%d'), value])
        
        config = {
            'type': 'heatmap',
            'calendar': {
                'range': str(year),
                'cellSize': ['auto', 20]
            },
            'series': [{
                'type': 'heatmap',
                'coordinateSystem': 'calendar',
                'data': data
            }]
        }
        
        return ChartData(
            chart_type='calendar_heatmap',
            title=f'{year}年日历热力图',
            data=data,
            config=config,
            library='echarts'
        )
    
    def _create_echarts_time_series(self, time_series: List[TimeSeriesPoint]) -> ChartData:
        """创建 ECharts 时间序列图表数据"""
        data = []
        categories = set()
        
        for point in time_series:
            data.append([
                point.date.strftime('%Y-%m-%d'),
                point.value,
                point.category or 'default'
            ])
            if point.category:
                categories.add(point.category)
        
        config = {
            'type': 'line',
            'xAxis': {'type': 'time'},
            'yAxis': {'type': 'value'},
            'series': [{'type': 'line', 'data': data}]
        }
        
        return ChartData(
            chart_type='time_series',
            title='时间序列图表',
            data=data,
            config=config,
            library='echarts'
        )
    
    def _create_echarts_distribution(self, distribution: Dict[str, int], group_by: str) -> ChartData:
        """创建 ECharts 分布图表数据"""
        categories = list(distribution.keys())
        values = list(distribution.values())
        
        data = [{'name': cat, 'value': val} for cat, val in distribution.items()]
        
        config = {
            'type': 'bar',
            'xAxis': {'type': 'category', 'data': categories},
            'yAxis': {'type': 'value'},
            'series': [{'type': 'bar', 'data': values}]
        }
        
        return ChartData(
            chart_type='distribution',
            title=f'日期{group_by}分布图',
            data=data,
            config=config,
            library='echarts'
        )
    
    # Matplotlib 适配器方法
    def _create_matplotlib_timeline(self, dates: List[datetime.date], events: List[str]) -> ChartData:
        """创建 Matplotlib 时间轴数据"""
        data = []
        for i, (date, event) in enumerate(zip(dates, events)):
            data.append({
                'x': date.strftime('%Y-%m-%d'),
                'y': i,
                'label': event
            })
        
        config = {
            'type': 'scatter',
            'figsize': (12, 8),
            'xlabel': 'Date',
            'ylabel': 'Events',
            'title': 'Timeline Chart'
        }
        
        return ChartData(
            chart_type='timeline',
            title='时间轴图表',
            data=data,
            config=config,
            library='matplotlib'
        )
    
    def _create_matplotlib_calendar_heatmap(self, date_values: Dict[datetime.date, float], year: int) -> ChartData:
        """创建 Matplotlib 日历热力图数据"""
        # 创建日历网格数据
        import calendar
        
        data = []
        for month in range(1, 13):
            month_cal = calendar.monthcalendar(year, month)
            for week_num, week in enumerate(month_cal):
                for day_num, day in enumerate(week):
                    if day != 0:
                        date = datetime.date(year, month, day)
                        value = date_values.get(date, 0)
                        data.append({
                            'month': month,
                            'week': week_num,
                            'day': day_num,
                            'value': value,
                            'date': date.strftime('%Y-%m-%d')
                        })
        
        config = {
            'type': 'imshow',
            'figsize': (15, 10),
            'cmap': 'YlOrRd',
            'title': f'{year}年日历热力图'
        }
        
        return ChartData(
            chart_type='calendar_heatmap',
            title=f'{year}年日历热力图',
            data=data,
            config=config,
            library='matplotlib'
        )
    
    def _create_matplotlib_time_series(self, time_series: List[TimeSeriesPoint]) -> ChartData:
        """创建 Matplotlib 时间序列图表数据"""
        data = []
        for point in time_series:
            data.append({
                'x': point.date.strftime('%Y-%m-%d'),
                'y': point.value,
                'label': point.label or '',
                'category': point.category or 'default'
            })
        
        config = {
            'type': 'plot',
            'figsize': (12, 6),
            'xlabel': 'Date',
            'ylabel': 'Value',
            'title': 'Time Series Chart'
        }
        
        return ChartData(
            chart_type='time_series',
            title='时间序列图表',
            data=data,
            config=config,
            library='matplotlib'
        )
    
    def _create_matplotlib_distribution(self, distribution: Dict[str, int], group_by: str) -> ChartData:
        """创建 Matplotlib 分布图表数据"""
        categories = list(distribution.keys())
        values = list(distribution.values())
        
        data = [{'category': cat, 'value': val} for cat, val in distribution.items()]
        
        config = {
            'type': 'bar',
            'figsize': (10, 6),
            'xlabel': group_by.title(),
            'ylabel': 'Count',
            'title': f'Date {group_by.title()} Distribution'
        }
        
        return ChartData(
            chart_type='distribution',
            title=f'日期{group_by}分布图',
            data=data,
            config=config,
            library='matplotlib'
        )
    
    # Plotly 适配器方法
    def _create_plotly_timeline(self, dates: List[datetime.date], events: List[str]) -> ChartData:
        """创建 Plotly 时间轴数据"""
        data = []
        for date, event in zip(dates, events):
            data.append({
                'x': date.strftime('%Y-%m-%d'),
                'y': event,
                'text': event,
                'mode': 'markers'
            })
        
        config = {
            'type': 'scatter',
            'title': 'Timeline Chart',
            'xaxis_title': 'Date',
            'yaxis_title': 'Events'
        }
        
        return ChartData(
            chart_type='timeline',
            title='时间轴图表',
            data=data,
            config=config,
            library='plotly'
        )
    
    def _create_plotly_calendar_heatmap(self, date_values: Dict[datetime.date, float], year: int) -> ChartData:
        """创建 Plotly 日历热力图数据"""
        data = []
        for date, value in date_values.items():
            if date.year == year:
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': value,
                    'month': date.month,
                    'day': date.day
                })
        
        config = {
            'type': 'heatmap',
            'title': f'{year}年日历热力图',
            'colorscale': 'Viridis'
        }
        
        return ChartData(
            chart_type='calendar_heatmap',
            title=f'{year}年日历热力图',
            data=data,
            config=config,
            library='plotly'
        )
    
    def _create_plotly_time_series(self, time_series: List[TimeSeriesPoint]) -> ChartData:
        """创建 Plotly 时间序列图表数据"""
        data = []
        for point in time_series:
            data.append({
                'x': point.date.strftime('%Y-%m-%d'),
                'y': point.value,
                'text': point.label or '',
                'category': point.category or 'default'
            })
        
        config = {
            'type': 'scatter',
            'mode': 'lines+markers',
            'title': 'Time Series Chart',
            'xaxis_title': 'Date',
            'yaxis_title': 'Value'
        }
        
        return ChartData(
            chart_type='time_series',
            title='时间序列图表',
            data=data,
            config=config,
            library='plotly'
        )
    
    def _create_plotly_distribution(self, distribution: Dict[str, int], group_by: str) -> ChartData:
        """创建 Plotly 分布图表数据"""
        categories = list(distribution.keys())
        values = list(distribution.values())
        
        data = [{'x': categories, 'y': values, 'type': 'bar'}]
        
        config = {
            'type': 'bar',
            'title': f'Date {group_by.title()} Distribution',
            'xaxis_title': group_by.title(),
            'yaxis_title': 'Count'
        }
        
        return ChartData(
            chart_type='distribution',
            title=f'日期{group_by}分布图',
            data=data,
            config=config,
            library='plotly'
        )
    
    # Chart.js 适配器方法
    def _create_chartjs_timeline(self, dates: List[datetime.date], events: List[str]) -> ChartData:
        """创建 Chart.js 时间轴数据"""
        data = []
        for date, event in zip(dates, events):
            data.append({
                'x': date.strftime('%Y-%m-%d'),
                'y': event,
                'label': event
            })
        
        config = {
            'type': 'scatter',
            'options': {
                'scales': {
                    'x': {'type': 'time'},
                    'y': {'type': 'category'}
                }
            }
        }
        
        return ChartData(
            chart_type='timeline',
            title='时间轴图表',
            data=data,
            config=config,
            library='chartjs'
        )
    
    def _create_chartjs_time_series(self, time_series: List[TimeSeriesPoint]) -> ChartData:
        """创建 Chart.js 时间序列图表数据"""
        data = []
        for point in time_series:
            data.append({
                'x': point.date.strftime('%Y-%m-%d'),
                'y': point.value
            })
        
        config = {
            'type': 'line',
            'options': {
                'scales': {
                    'x': {'type': 'time'},
                    'y': {'type': 'linear'}
                }
            }
        }
        
        return ChartData(
            chart_type='time_series',
            title='时间序列图表',
            data=data,
            config=config,
            library='chartjs'
        )
    
    def _create_chartjs_distribution(self, distribution: Dict[str, int], group_by: str) -> ChartData:
        """创建 Chart.js 分布图表数据"""
        labels = list(distribution.keys())
        values = list(distribution.values())
        
        data = {
            'labels': labels,
            'datasets': [{
                'label': f'{group_by.title()} Distribution',
                'data': values,
                'backgroundColor': 'rgba(75, 192, 192, 0.6)'
            }]
        }
        
        config = {
            'type': 'bar',
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'Date {group_by.title()} Distribution'
                    }
                }
            }
        }
        
        return ChartData(
            chart_type='distribution',
            title=f'日期{group_by}分布图',
            data=data,
            config=config,
            library='chartjs'
        )
    
    # Highcharts 适配器方法
    def _create_highcharts_timeline(self, dates: List[datetime.date], events: List[str]) -> ChartData:
        """创建 Highcharts 时间轴数据"""
        data = []
        for date, event in zip(dates, events):
            timestamp = int(date.strftime('%s')) * 1000  # Highcharts 使用毫秒时间戳
            data.append([timestamp, event])
        
        config = {
            'chart': {'type': 'timeline'},
            'title': {'text': 'Timeline Chart'},
            'series': [{'data': data}]
        }
        
        return ChartData(
            chart_type='timeline',
            title='时间轴图表',
            data=data,
            config=config,
            library='highcharts'
        )
    
    def _create_highcharts_time_series(self, time_series: List[TimeSeriesPoint]) -> ChartData:
        """创建 Highcharts 时间序列图表数据"""
        data = []
        for point in time_series:
            timestamp = int(point.date.strftime('%s')) * 1000
            data.append([timestamp, point.value])
        
        config = {
            'chart': {'type': 'line'},
            'title': {'text': 'Time Series Chart'},
            'xAxis': {'type': 'datetime'},
            'series': [{'data': data}]
        }
        
        return ChartData(
            chart_type='time_series',
            title='时间序列图表',
            data=data,
            config=config,
            library='highcharts'
        )
    
    # 辅助方法
    def _calculate_date_distribution(self, dates: List[datetime.date], group_by: str) -> Dict[str, int]:
        """计算日期分布"""
        distribution = Counter()
        
        for date in dates:
            if group_by == 'month':
                key = f"{date.month}月"
            elif group_by == 'weekday':
                weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                key = weekdays[date.weekday()]
            elif group_by == 'year':
                key = str(date.year)
            elif group_by == 'quarter':
                quarter = (date.month - 1) // 3 + 1
                key = f"Q{quarter}"
            else:
                key = date.strftime('%Y-%m')
            
            distribution[key] += 1
        
        return dict(distribution)
    
    def export_chart_data(self, chart_data: ChartData, format: str = 'json') -> str:
        """导出图表数据"""
        if format == 'json':
            return json.dumps(asdict(chart_data), ensure_ascii=False, indent=2)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            if chart_data.data and isinstance(chart_data.data[0], dict):
                fieldnames = chart_data.data[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(chart_data.data)
            
            return output.getvalue()
        else:
            raise ValueError("支持的格式: json, csv")

# 便捷函数
def create_timeline_chart(dates: List[datetime.date], events: List[str], library: str = 'echarts') -> ChartData:
    """创建时间轴图表（便捷函数）"""
    viz = DateVisualization()
    return viz.create_timeline_data(dates, events, library)

def create_calendar_heatmap(date_values: Dict[datetime.date, float], year: int, library: str = 'echarts') -> ChartData:
    """创建日历热力图（便捷函数）"""
    viz = DateVisualization()
    return viz.create_calendar_heatmap(date_values, year, library)

def create_time_series_chart(time_series: List[TimeSeriesPoint], library: str = 'echarts') -> ChartData:
    """创建时间序列图表（便捷函数）"""
    viz = DateVisualization()
    return viz.create_time_series_chart(time_series, library)
