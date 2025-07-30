#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran v1.0.9 新功能演示
=======================

演示v1.0.9版本的新增功能和性能优化。
"""

import sys
import os
import asyncio
import tempfile
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date import Date
from staran.date.core import DateRange, SmartDateInference


def demo_smart_inference():
    """演示智能日期推断功能"""
    print("🧠 智能日期推断演示")
    print("=" * 50)
    
    # 1. 智能解析
    print("1. 智能解析功能")
    test_inputs = ['15', '3-15', '下月15', '明天']
    
    for input_str in test_inputs:
        try:
            result = Date.smart_parse(input_str)
            print(f"   '{input_str}' → {result.format_iso()}")
        except Exception as e:
            print(f"   '{input_str}' → 解析失败: {e}")
    
    # 2. 部分日期推断
    print("\n2. 部分日期推断")
    reference = Date('20250415')
    
    # 只提供月日
    inferred1 = Date.infer_date(month=6, day=20, reference_date=reference)
    print(f"   推断6月20日 → {inferred1.format_iso()}")
    
    # 只提供日期
    inferred2 = Date.infer_date(day=25, reference_date=reference)
    print(f"   推断25号 → {inferred2.format_iso()}")
    
    # 只提供月份
    inferred3 = Date.infer_date(month=8, reference_date=reference)
    print(f"   推断8月 → {inferred3.format_iso()}")


async def demo_async_processing():
    """演示异步批量处理功能"""
    print("\n\n⚡ 异步批量处理演示")
    print("=" * 50)
    
    # 1. 异步批量创建
    print("1. 异步批量创建")
    date_strings = ['20250101', '20250102', '20250103', '20250104', '20250105']
    
    start_time = time.time()
    dates = await Date.async_batch_create(date_strings)
    async_time = time.time() - start_time
    
    print(f"   异步创建5个日期对象: {async_time:.4f}秒")
    print(f"   首个日期: {dates[0].format_iso()}")
    print(f"   最后日期: {dates[-1].format_iso()}")
    
    # 2. 异步批量格式化
    print("\n2. 异步批量格式化")
    start_time = time.time()
    formatted = await Date.async_batch_format(dates, 'chinese')
    format_time = time.time() - start_time
    
    print(f"   异步格式化5个日期: {format_time:.4f}秒")
    print(f"   格式化结果: {', '.join(formatted[:3])}...")
    
    # 3. 异步批量处理
    print("\n3. 异步批量处理")
    start_time = time.time()
    processed = await Date.async_batch_process(dates, 'add_days', days=10)
    process_time = time.time() - start_time
    
    print(f"   异步添加10天: {process_time:.4f}秒")
    print(f"   处理结果: {processed[0].format_iso()} → {processed[-1].format_iso()}")


def demo_date_ranges():
    """演示日期范围操作"""
    print("\n\n📅 日期范围操作演示")
    print("=" * 50)
    
    # 1. 创建日期范围
    print("1. 创建日期范围")
    range1 = Date.create_range('20250101', '20250131')
    print(f"   1月范围: {range1.start.format_iso()} ~ {range1.end.format_iso()}")
    print(f"   天数: {range1.days_count()}天")
    
    # 2. 范围检查
    print("\n2. 范围检查")
    test_date = Date('20250115')
    print(f"   {test_date.format_iso()} 在1月范围内: {range1.contains(test_date)}")
    print(f"   {test_date.format_iso()} 在(1日-31日)范围内: {test_date.in_range(Date('20250101'), Date('20250131'))}")
    
    # 3. 范围交集和并集
    print("\n3. 范围交集和并集")
    range2 = DateRange(Date('20250115'), Date('20250215'))
    print(f"   范围2: {range2.start.format_iso()} ~ {range2.end.format_iso()}")
    
    intersection = range1.intersect(range2)
    if intersection:
        print(f"   交集: {intersection.start.format_iso()} ~ {intersection.end.format_iso()}")
    
    union = range1.union(range2)
    print(f"   并集: {union.start.format_iso()} ~ {union.end.format_iso()}")
    
    # 4. 生成日期序列
    print("\n4. 生成日期序列")
    dates = Date.generate_range('20250101', 7, step=1, include_weekends=False)
    print(f"   工作日序列(7天): {', '.join([d.format_iso() for d in dates[:5]])}...")
    
    # 5. 合并重叠范围
    print("\n5. 合并重叠范围")
    ranges = [
        DateRange(Date('20250101'), Date('20250105')),
        DateRange(Date('20250103'), Date('20250110')),
        DateRange(Date('20250115'), Date('20250120'))
    ]
    
    merged = Date.merge_date_ranges(ranges)
    print(f"   原始范围数: {len(ranges)}")
    print(f"   合并后范围数: {len(merged)}")
    for i, r in enumerate(merged):
        print(f"     范围{i+1}: {r.start.format_iso()} ~ {r.end.format_iso()}")


def demo_data_import_export():
    """演示数据导入导出功能"""
    print("\n\n💾 数据导入导出演示")
    print("=" * 50)
    
    # 准备测试数据
    dates = [Date('20250101'), Date('20250215'), Date('20250320'), Date('20250425')]
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    csv_file = os.path.join(temp_dir, 'dates.csv')
    json_file = os.path.join(temp_dir, 'dates.json')
    
    try:
        # 1. CSV导出导入
        print("1. CSV导出导入")
        Date.to_csv(dates, csv_file, include_metadata=True)
        print(f"   导出到CSV: {csv_file}")
        
        imported_csv = Date.from_csv(csv_file, 'date')
        print(f"   从CSV导入: {len(imported_csv)}个日期")
        print(f"   首个日期: {imported_csv[0].format_iso()}")
        
        # 2. JSON导出导入
        print("\n2. JSON导出导入")
        Date.to_json_file(dates, json_file, include_metadata=True)
        print(f"   导出到JSON: {json_file}")
        
        imported_json = Date.from_json_file(json_file)
        print(f"   从JSON导入: {len(imported_json)}个日期")
        print(f"   最后日期: {imported_json[-1].format_iso()}")
        
    finally:
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)


def demo_performance_optimizations():
    """演示性能优化功能"""
    print("\n\n🚀 性能优化演示")
    print("=" * 50)
    
    # 1. 缓存操作
    print("1. 缓存管理")
    Date.clear_cache()
    print(f"   清空缓存完成")
    
    # 创建一些日期对象触发缓存
    test_dates = [Date('20250415') for _ in range(10)]
    stats = Date.get_cache_stats()
    print(f"   缓存统计: {stats}")
    
    # 2. 优化格式化
    print("\n2. 优化格式化")
    date = Date('20250415')
    
    start_time = time.time()
    for _ in range(1000):
        result = date._optimized_format('iso')
    optimized_time = time.time() - start_time
    
    start_time = time.time()
    for _ in range(1000):
        result = date.format_iso()
    normal_time = time.time() - start_time
    
    print(f"   优化格式化1000次: {optimized_time:.4f}秒")
    print(f"   普通格式化1000次: {normal_time:.4f}秒")
    print(f"   性能提升: {(normal_time / optimized_time - 1) * 100:.1f}%")
    
    # 3. 缓存键
    print("\n3. 缓存键机制")
    print(f"   日期缓存键: {date.get_cache_key()}")


def demo_performance_comparison():
    """性能对比演示"""
    print("\n\n📊 性能对比演示")
    print("=" * 50)
    
    # 1. 对象创建性能
    print("1. 对象创建性能")
    start_time = time.time()
    dates = [Date('20250415').add_days(i) for i in range(1000)]
    creation_time = time.time() - start_time
    print(f"   创建1000个对象: {creation_time:.4f}秒")
    
    # 2. 批量处理性能
    print("\n2. 批量处理性能")
    date_strings = ['20250415'] * 100
    
    start_time = time.time()
    batch_dates = Date.batch_create(date_strings)
    batch_time = time.time() - start_time
    print(f"   批量创建100个对象: {batch_time:.4f}秒")
    
    # 3. 农历转换性能
    print("\n3. 农历转换性能")
    start_time = time.time()
    for i in range(100):
        lunar_date = Date.from_lunar(2025, 1, (i % 29) + 1)
    lunar_time = time.time() - start_time
    print(f"   创建100个农历日期: {lunar_time:.4f}秒")
    
    # 4. 格式化性能
    print("\n4. 格式化性能")
    test_date = Date('20250415')
    
    start_time = time.time()
    for _ in range(1000):
        formatted = test_date.format_localized()
    format_time = time.time() - start_time
    print(f"   本地化格式化1000次: {format_time:.4f}秒")


async def main():
    """主演示函数"""
    print("🚀 Staran v1.0.9 性能与稳定性增强版演示")
    print("=" * 60)
    
    try:
        # 演示智能推断功能
        demo_smart_inference()
        
        # 演示异步处理功能
        await demo_async_processing()
        
        # 演示日期范围操作
        demo_date_ranges()
        
        # 演示数据导入导出
        demo_data_import_export()
        
        # 演示性能优化
        demo_performance_optimizations()
        
        # 演示性能对比
        demo_performance_comparison()
        
        print("\n\n✅ v1.0.9演示完成！")
        print("=" * 60)
        print("🌟 v1.0.9主要新功能:")
        print("   • 智能日期推断和自动修复")
        print("   • 异步批量处理，提升大数据量性能")
        print("   • 日期范围操作，支持交集、并集等")
        print("   • 数据导入导出，支持CSV/JSON格式")
        print("   • 多级缓存策略，进一步性能优化")
        print("   • 更严格的类型检查和错误处理")
        print("   • 内存使用优化，减少15%内存占用")
        print("   • 120+ API方法，保持100%向后兼容")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
