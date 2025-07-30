#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran v1.0.10 新功能演示
========================

演示v1.0.10版本的所有新功能：
- 完整时区支持
- 日期表达式解析
- 二十四节气扩展
- 数据可视化集成
- REST API接口
"""

import sys
import os
import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date import (
    Date, get_version_info, get_feature_status, parse_expression,
    create_timeline_chart, start_api_server
)

def demo_version_info():
    """演示版本信息和功能状态"""
    print("🚀 Staran v1.0.10 版本信息")
    print("=" * 50)
    
    version_info = get_version_info()
    print(f"版本: {version_info['version']}")
    print(f"v1.0.10功能可用: {version_info['v1010_features_available']}")
    
    print("\n可用模块:")
    for module, available in version_info['modules'].items():
        status = "✅" if available else "❌"
        print(f"  {status} {module}")
    
    if version_info.get('new_features'):
        print(f"\n新功能: {', '.join(version_info['new_features'])}")
    
    # Date对象的功能状态
    date_obj = Date.today()
    feature_status = date_obj.get_feature_status()
    
    print(f"\nDate对象功能状态:")
    for feature, available in feature_status.items():
        status = "✅" if available else "❌"
        print(f"  {status} {feature}")

def demo_timezone_support():
    """演示时区支持功能"""
    print("\n\n🌍 时区支持功能演示")
    print("=" * 50)
    
    date = Date("2025-07-29")
    
    try:
        # 列出支持的时区
        timezones = Date.get_supported_timezones()
        print(f"支持的时区数量: {len(timezones)}")
        print(f"主要时区: {timezones[:10]}")
        
        # 时区信息查询
        print(f"\n时区信息查询:")
        for tz in ['UTC+8', 'EST', 'JST', 'GMT']:
            try:
                tz_info = date.get_timezone_info(tz)
                print(f"  {tz}: {tz_info['name']} ({tz_info['description']})")
                print(f"      当前偏移: {tz_info['offset_string']}")
                print(f"      夏令时: {'是' if tz_info['is_dst_active'] else '否'}")
            except Exception as e:
                print(f"  {tz}: 获取信息失败 - {e}")
        
        # 时区转换演示
        print(f"\n时区转换演示:")
        try:
            import datetime as dt
            base_time = dt.time(12, 0, 0)  # 中午12点
            
            beijing_dt = date.to_timezone('UTC+8', base_time)
            print(f"  北京时间: {beijing_dt}")
            
            # 创建其他时区的时间
            utc_dt = date.to_timezone('UTC', base_time)
            print(f"  UTC时间: {utc_dt}")
            
        except Exception as e:
            print(f"  时区转换演示失败: {e}")
    
    except Exception as e:
        print(f"时区功能不可用: {e}")

def demo_expression_parsing():
    """演示日期表达式解析功能"""
    print("\n\n📝 日期表达式解析演示")
    print("=" * 50)
    
    expressions = [
        "今天", "明天", "后天", "昨天", "前天",
        "下周一", "上周五", "这周三",
        "下个月", "上个月", "明年",
        "3天后", "5天前", "2周后", "1个月前",
        "2025年春节", "2025-12-25", "12月15日"
    ]
    
    print("表达式解析测试:")
    for expr in expressions:
        try:
            result = parse_expression(expr)
            if result:
                print(f"  '{expr}' → {result.format_iso()} ({result.format_chinese()})")
                
                # 获取详细解析信息
                detailed = Date.parse_expression_detailed(expr)
                if detailed['success']:
                    print(f"    置信度: {detailed['confidence']:.2f}")
                    print(f"    匹配模式: {detailed['matched_pattern']}")
            else:
                print(f"  '{expr}' → 解析失败")
        except Exception as e:
            print(f"  '{expr}' → 错误: {e}")

def demo_solar_terms():
    """演示二十四节气功能"""
    print("\n\n🌸 二十四节气功能演示")
    print("=" * 50)
    
    try:
        current_year = 2025
        
        # 获取全年节气
        solar_terms = Date.get_year_solar_terms(current_year)
        print(f"{current_year}年二十四节气:")
        
        for i, term in enumerate(solar_terms):
            print(f"  {i+1:2d}. {term.name:4s} - {term.date.strftime('%m月%d日')} ({term.season})")
            if i == 5:  # 只显示前6个，节省空间
                print(f"      ... (共{len(solar_terms)}个节气)")
                break
        
        # 当前日期的节气信息
        today = Date.today()
        print(f"\n当前日期节气信息:")
        print(f"  日期: {today.format_chinese()}")
        
        try:
            current_term = today.get_solar_term()
            if current_term:
                print(f"  最近节气: {current_term.name}")
                print(f"  节气日期: {current_term.date.strftime('%Y年%m月%d日')}")
                print(f"  节气描述: {current_term.description}")
                print(f"  气候特征: {current_term.climate_features}")
            
            # 下一个节气
            next_term = today.get_next_solar_term()
            print(f"  下一节气: {next_term.name}")
            print(f"  节气日期: {next_term.date.strftime('%Y年%m月%d日')}")
            print(f"  距离天数: {today.days_to_next_solar_term()}天")
            
            # 判断是否节气日
            is_term_day = today.is_solar_term()
            print(f"  今天是节气日: {'是' if is_term_day else '否'}")
            
        except Exception as e:
            print(f"  节气信息获取失败: {e}")
    
    except Exception as e:
        print(f"节气功能不可用: {e}")

def demo_visualization():
    """演示数据可视化功能"""
    print("\n\n📊 数据可视化功能演示")
    print("=" * 50)
    
    try:
        # 创建示例数据
        dates = [Date("2025-07-29"), Date("2025-08-01"), Date("2025-08-15")]
        events = ["项目开始", "里程碑1", "项目完成"]
        
        # 创建时间轴图表
        chart_data = create_timeline_chart(dates, events, 'echarts')
        
        print("时间轴图表数据:")
        print(f"  图表类型: {chart_data.chart_type}")
        print(f"  标题: {chart_data.title}")
        print(f"  图表库: {chart_data.library}")
        print(f"  数据点数量: {len(chart_data.data)}")
        
        # 显示部分数据
        print(f"  示例数据:")
        for i, data_point in enumerate(chart_data.data[:3]):
            print(f"    {i+1}. {data_point}")
        
        # 日历热力图示例
        print(f"\n日历热力图数据生成:")
        date_values = {
            Date("2025-07-29"): 85,
            Date("2025-07-30"): 92,
            Date("2025-07-31"): 78
        }
        
        try:
            heatmap_data = Date.create_calendar_heatmap(date_values, 2025, 'echarts')
            print(f"  热力图标题: {heatmap_data.title}")
            print(f"  数据点数量: {len(heatmap_data.data)}")
        except Exception as e:
            print(f"  热力图生成失败: {e}")
        
        # 时间序列图表
        print(f"\n时间序列图表:")
        time_series_data = [
            (Date("2025-07-29"), 100),
            (Date("2025-07-30"), 120),
            (Date("2025-07-31"), 95)
        ]
        
        try:
            series_chart = Date.create_time_series_chart(time_series_data, 'echarts')
            print(f"  系列图标题: {series_chart.title}")
            print(f"  配置类型: {series_chart.config.get('type')}")
        except Exception as e:
            print(f"  时间序列图生成失败: {e}")
    
    except Exception as e:
        print(f"可视化功能不可用: {e}")

def demo_enhanced_date_ranges():
    """演示增强的日期范围功能"""
    print("\n\n📅 增强日期范围功能演示")
    print("=" * 50)
    
    start_date = Date("2025-07-29")
    end_date = Date("2025-08-15")
    
    # 创建日期范围
    date_range = start_date.create_range_to(end_date)
    print(f"日期范围: {start_date.format_iso()} 到 {end_date.format_iso()}")
    print(f"范围天数: {date_range.days_count()}天")
    
    # 检查日期是否在范围内
    test_date = Date("2025-08-01")
    in_range = test_date.in_range(start_date, end_date)
    print(f"{test_date.format_iso()} 在范围内: {'是' if in_range else '否'}")
    
    # 创建日期序列
    sequence = Date.create_date_sequence(start_date, start_date.add_days(6), 2)
    print(f"日期序列 (步长2天): {[d.format_iso() for d in sequence]}")
    
    # 范围操作
    range1 = start_date.create_range_with_days(10)
    range2 = start_date.add_days(5).create_range_with_days(10)
    
    print(f"范围1: {range1.start.format_iso()} - {range1.end.format_iso()}")
    print(f"范围2: {range2.start.format_iso()} - {range2.end.format_iso()}")
    
    # 交集
    intersection = range1.intersect(range2)
    if intersection:
        print(f"交集: {intersection.start.format_iso()} - {intersection.end.format_iso()}")
    else:
        print("无交集")
    
    # 并集
    union = range1.union(range2)
    print(f"并集: {union.start.format_iso()} - {union.end.format_iso()}")

def demo_api_server():
    """演示REST API服务器功能"""
    print("\n\n🌐 REST API服务器演示")
    print("=" * 50)
    
    try:
        from staran.date import start_api_server
        
        print("API服务器功能演示:")
        print("  注意: 这里只演示服务器创建，不实际启动")
        print("  实际使用时可以启动完整的HTTP服务")
        
        # 实际使用时的示例
        print("\n启动API服务器的方法:")
        print("  server = start_api_server('localhost', 8000, background=True)")
        print("  # 服务器将在 http://localhost:8000 运行")
        print("")
        print("主要API端点:")
        endpoints = [
            "GET /api/health - 健康检查",
            "GET /api/date/create?date=2025-07-29 - 创建日期",
            "GET /api/date/format?date=2025-07-29&format=chinese - 格式化日期",
            "GET /api/lunar/convert?date=2025-07-29&direction=solar_to_lunar - 农历转换",
            "GET /api/solar-terms?year=2025 - 查询节气",
            "GET /api/timezone/convert?date=2025-07-29&from_tz=UTC+8&to_tz=EST - 时区转换",
            "GET /api/expression/parse?expression=明天 - 表达式解析",
            "GET /api/visualization/data?type=calendar_heatmap&year=2025 - 可视化数据"
        ]
        
        for endpoint in endpoints:
            print(f"  {endpoint}")
        
        print(f"\n文档地址: GET /api/docs")
        
    except Exception as e:
        print(f"API服务器功能不可用: {e}")

def demo_help_system():
    """演示帮助系统"""
    print("\n\n❓ 帮助系统演示")
    print("=" * 50)
    
    date = Date.today()
    
    # 获取创建方法帮助
    help_creation = date.help('creation')
    print("创建方法帮助:")
    print(help_creation)
    
    # 获取时区功能帮助
    try:
        help_timezone = date.help('timezone')
        print(f"\n时区功能帮助:")
        print(help_timezone)
    except:
        print(f"\n时区功能帮助不可用")
    
    # 获取节气功能帮助
    try:
        help_solar_terms = date.help('solar_terms')
        print(f"\n节气功能帮助:")
        print(help_solar_terms)
    except:
        print(f"\n节气功能帮助不可用")

def main():
    """主演示函数"""
    print("🚀 Staran v1.0.10 完整功能演示")
    print("=" * 60)
    
    try:
        # 基础信息
        demo_version_info()
        
        # 新功能演示
        demo_timezone_support()
        demo_expression_parsing()
        demo_solar_terms()
        demo_visualization()
        demo_enhanced_date_ranges()
        demo_api_server()
        demo_help_system()
        
        print("\n\n✅ v1.0.10 功能演示完成！")
        print("=" * 60)
        print("🌟 主要新增功能:")
        print("   • 完整时区支持 - 全球时区转换和处理")
        print("   • 日期表达式解析 - 自然语言日期解析")
        print("   • 二十四节气扩展 - 完整节气计算和查询")
        print("   • 数据可视化集成 - 多种图表库支持")
        print("   • REST API接口 - HTTP API服务")
        print("   • 增强日期范围操作 - 更丰富的范围功能")
        print("   • 智能帮助系统 - 分类帮助信息")
        print("")
        print("📚 更多信息:")
        print("   • API文档: 调用 Date().help() 查看")
        print("   • 版本信息: 调用 get_version_info() 查看")
        print("   • 功能状态: 调用 Date().get_feature_status() 查看")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
