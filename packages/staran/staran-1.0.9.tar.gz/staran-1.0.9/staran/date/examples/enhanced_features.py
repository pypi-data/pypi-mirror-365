#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran Date 模块增强功能演示
==========================

展示v1.0.7版本的所有新增和优化功能。
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date import Date


def enhanced_holidays_demo():
    """增强的节假日功能演示"""
    print("🎊 增强的节假日功能")
    print("=" * 40)
    
    # 中国节假日
    print("中国节假日:")
    cn_dates = ['20250101', '20250501', '20251001', '20250405']
    for date_str in cn_dates:
        date = Date(date_str)
        is_holiday = date.is_holiday('CN')
        status = "✅ 节假日" if is_holiday else "❌ 工作日"
        print(f"   {date.format_chinese()}: {status}")
    
    # 美国节假日
    print("\n美国节假日:")
    us_dates = ['20250101', '20250704', '20251225', '20251127']
    for date_str in us_dates:
        date = Date(date_str)
        is_holiday = date.is_holiday('US')
        status = "✅ 节假日" if is_holiday else "❌ 工作日"
        print(f"   {date.format_iso()}: {status}")
    
    print()


def batch_processing_demo():
    """批量处理功能演示"""
    print("⚡ 批量处理功能")
    print("=" * 40)
    
    # 批量创建
    date_strings = ['20250101', '20250201', '20250301', '20250401']
    dates = Date.batch_create(date_strings)
    print("批量创建结果:")
    for i, date in enumerate(dates):
        print(f"   {date_strings[i]} -> {date}")
    
    # 批量格式化
    print("\n批量格式化:")
    iso_formats = Date.batch_format(dates, 'iso')
    chinese_formats = Date.batch_format(dates, 'chinese')
    
    for i, date in enumerate(dates):
        print(f"   原始: {date}")
        print(f"   ISO: {iso_formats[i]}")
        print(f"   中文: {chinese_formats[i]}")
        print()


def timezone_demo():
    """时区支持演示"""
    print("🌍 时区支持功能")
    print("=" * 40)
    
    date = Date('20250101')
    
    # 不同时区的时间戳
    utc_timestamp = date.to_timestamp(0)      # UTC
    beijing_timestamp = date.to_timestamp(8) # 北京时间 (UTC+8)
    ny_timestamp = date.to_timestamp(-5)     # 纽约时间 (UTC-5)
    
    print("同一日期在不同时区的时间戳:")
    print(f"   UTC: {utc_timestamp}")
    print(f"   北京时间: {beijing_timestamp}")
    print(f"   纽约时间: {ny_timestamp}")
    
    # 从时间戳创建日期
    print("\n从时间戳创建日期:")
    base_timestamp = 1735689600  # 2025-01-01 00:00:00 UTC
    utc_date = Date.from_timestamp(base_timestamp, 0)
    beijing_date = Date.from_timestamp(base_timestamp, 8)
    
    print(f"   UTC时间戳 -> {utc_date.format_iso()}")
    print(f"   +8小时偏移 -> {beijing_date.format_iso()}")
    print()


def business_rules_demo():
    """业务规则演示"""
    print("📊 业务规则功能")
    print("=" * 40)
    
    date = Date('20250415')  # 2025年4月15日
    
    print(f"基准日期: {date.format_chinese()}")
    
    # 各种业务规则
    rules = [
        ('month_end', '月末'),
        ('quarter_end', '季度末'),
        ('next_business_day', '下一个工作日'),
        ('prev_business_day', '上一个工作日')
    ]
    
    for rule, description in rules:
        try:
            result = date.apply_business_rule(rule)
            print(f"   {description}: {result.format_chinese()}")
        except ValueError as e:
            print(f"   {description}: {e}")
    
    print()


def enhanced_json_demo():
    """增强JSON功能演示"""
    print("📄 增强JSON序列化")
    print("=" * 40)
    
    date = Date('20250415')
    
    # 包含元数据的JSON
    json_with_meta = date.to_json(include_metadata=True)
    json_simple = date.to_json(include_metadata=False)
    
    print("包含元数据的JSON:")
    print(json.dumps(json.loads(json_with_meta), indent=2, ensure_ascii=False))
    
    print("\n简单JSON:")
    print(json.dumps(json.loads(json_simple), indent=2, ensure_ascii=False))
    
    # 字典转换
    dict_with_meta = date.to_dict(include_metadata=True)
    print("\n包含元数据的字典:")
    for key, value in dict_with_meta.items():
        print(f"   {key}: {value}")
    
    print()


def date_ranges_demo():
    """日期范围功能演示"""
    print("📅 新增日期范围功能")
    print("=" * 40)
    
    # 工作日和周末
    print("一周的工作日和周末:")
    business_days = Date.business_days('20250407', '20250413')  # 一周
    weekends = Date.weekends('20250407', '20250413')
    
    print("   工作日:", [str(d) for d in business_days])
    print("   周末:", [str(d) for d in weekends])
    
    # 月份范围
    print("\n月份范围 (前3个月):")
    months = Date.month_range('202501', 3)
    for month in months:
        print(f"   {month} ({month.format_chinese()})")
    
    # 季度日期
    print("\n2025年季度划分:")
    quarters = Date.quarter_dates(2025)
    for q, (start, end) in quarters.items():
        print(f"   Q{q}: {start.format_compact()} - {end.format_compact()}")
    
    print()


def validation_demo():
    """验证功能演示"""
    print("✅ 日期验证功能")
    print("=" * 40)
    
    test_strings = [
        '20250415',  # 有效
        '20250230',  # 无效 - 2月30日
        '202504',    # 有效
        'invalid',   # 无效
        '20251301',  # 无效 - 13月
    ]
    
    print("日期字符串验证:")
    for test_str in test_strings:
        is_valid = Date.is_valid_date_string(test_str)
        status = "✅ 有效" if is_valid else "❌ 无效"
        print(f"   '{test_str}': {status}")
    
    print()


def main():
    """主演示函数"""
    print("✨ Staran Date 模块 v1.0.7 增强功能演示")
    print("=" * 50)
    print()
    
    # 运行各个演示
    enhanced_holidays_demo()
    batch_processing_demo()
    timezone_demo()
    business_rules_demo()
    enhanced_json_demo()
    date_ranges_demo()
    validation_demo()
    
    print("🎉 演示完成!")
    print("\n📝 总结:")
    print("   • 增强的节假日支持 (多国节假日)")
    print("   • 高效的批量处理功能")
    print("   • 基础时区转换支持")
    print("   • 灵活的业务规则引擎")
    print("   • 增强的JSON序列化")
    print("   • 丰富的日期范围生成")
    print("   • 严格的数据验证")
    print("\n更多功能请查阅API文档! 📚")


if __name__ == '__main__':
    main()
