#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Staran v1.0.8 新功能演示
=======================

演示农历支持和多语言功能的使用方法。
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date import Date, from_lunar, set_language, get_language
from staran.date.lunar import LunarDate
from staran.date.i18n import Language

def demo_lunar_features():
    """演示农历功能"""
    print("🌙 农历功能演示")
    print("=" * 50)
    
    # 1. 从农历日期创建公历日期
    print("1. 从农历日期创建公历日期")
    lunar_new_year = Date.from_lunar(2025, 1, 1)  # 农历2025年正月初一
    print(f"   农历2025年正月初一 → {lunar_new_year.format_iso()}")
    
    mid_autumn = Date.from_lunar(2025, 8, 15)  # 农历中秋节
    print(f"   农历2025年八月十五 → {mid_autumn.format_iso()}")
    
    # 2. 从农历字符串创建
    print("\n2. 从农历字符串创建")
    date_from_str = Date.from_lunar_string("20250315")  # 农历三月十五
    print(f"   '20250315' → {date_from_str.format_iso()}")
    
    # 闰月示例（假设2025年有闰月）
    try:
        leap_date = Date.from_lunar_string("2025闰0415")  # 农历闰四月十五
        print(f"   '2025闰0415' → {leap_date.format_iso()}")
    except:
        print(f"   闰月示例跳过（2025年可能无闰四月）")
    
    # 3. 公历转农历
    print("\n3. 公历转农历")
    solar_date = Date("20250415")
    lunar = solar_date.to_lunar()
    print(f"   {solar_date.format_iso()} → {lunar.format_chinese()}")
    print(f"   紧凑格式: {lunar.format_compact()}")
    print(f"   天干地支: {lunar.get_ganzhi_year()}")
    print(f"   生肖: {lunar.get_zodiac()}")
    
    # 4. 农历格式化
    print("\n4. 农历格式化")
    test_date = Date("20250129")  # 接近春节的日期
    print(f"   基本格式: {test_date.format_lunar()}")
    print(f"   包含生肖: {test_date.format_lunar(include_zodiac=True)}")
    print(f"   紧凑格式: {test_date.format_lunar_compact()}")
    
    # 5. 农历判断
    print("\n5. 农历判断")
    spring_festival = Date.from_lunar(2025, 1, 1)
    print(f"   农历正月初一:")
    print(f"     是否农历新年: {spring_festival.is_lunar_new_year()}")
    print(f"     是否农历月初: {spring_festival.is_lunar_month_start()}")
    print(f"     是否农历月中: {spring_festival.is_lunar_month_mid()}")
    
    lantern_festival = Date.from_lunar(2025, 1, 15)
    print(f"   农历正月十五:")
    print(f"     是否农历新年: {lantern_festival.is_lunar_new_year()}")
    print(f"     是否农历月中: {lantern_festival.is_lunar_month_mid()}")
    
    # 6. 农历比较
    print("\n6. 农历比较")
    date1 = Date.from_lunar(2025, 1, 1)
    date2 = Date.from_lunar(2025, 1, 15)
    print(f"   {date1.format_lunar()} vs {date2.format_lunar()}")
    print(f"     比较结果: {date1.compare_lunar(date2)}")  # -1: 前者小于后者
    print(f"     是否同月: {date1.is_same_lunar_month(date2)}")
    print(f"     是否同日: {date1.is_same_lunar_day(date2)}")


def demo_multilanguage_features():
    """演示多语言功能"""
    print("\n\n🌍 多语言功能演示")
    print("=" * 50)
    
    # 测试日期
    test_date = Date("20250415")  # 2025年4月15日，星期二
    
    print(f"测试日期: {test_date.format_iso()}")
    
    # 1. 全局语言设置
    print("\n1. 全局语言设置")
    print(f"   当前语言: {get_language()}")
    print(f"   支持的语言: {Date.get_supported_languages()}")
    
    # 2. 中文简体
    print("\n2. 中文简体 (zh_CN)")
    set_language('zh_CN')
    print(f"   本地化格式: {test_date.format_localized()}")
    print(f"   星期格式: {test_date.format_weekday_localized()}")
    print(f"   月份格式: {test_date.format_month_localized()}")
    print(f"   季度格式: {test_date.format_quarter_localized()}")
    print(f"   相对时间: {test_date.format_relative_localized()}")
    
    # 3. 中文繁体
    print("\n3. 中文繁体 (zh_TW)")
    set_language('zh_TW')
    print(f"   本地化格式: {test_date.format_localized()}")
    print(f"   星期格式: {test_date.format_weekday_localized()}")
    print(f"   相对时间: {test_date.format_relative_localized()}")
    
    # 4. 日语
    print("\n4. 日语 (ja_JP)")
    set_language('ja_JP')
    print(f"   本地化格式: {test_date.format_localized()}")
    print(f"   星期格式: {test_date.format_weekday_localized()}")
    print(f"   星期短格式: {test_date.format_weekday_localized(short=True)}")
    print(f"   月份格式: {test_date.format_month_localized()}")
    print(f"   相对时间: {test_date.format_relative_localized()}")
    
    # 5. 英语
    print("\n5. 英语 (en_US)")
    set_language('en_US')
    print(f"   本地化格式: {test_date.format_localized()}")
    print(f"   星期格式: {test_date.format_weekday_localized()}")
    print(f"   月份格式: {test_date.format_month_localized()}")
    print(f"   季度格式: {test_date.format_quarter_localized()}")
    print(f"   相对时间: {test_date.format_relative_localized()}")
    
    # 6. 单次覆盖演示
    print("\n6. 单次语言覆盖")
    set_language('zh_CN')  # 设置全局为中文
    print(f"   全局中文: {test_date.format_weekday_localized()}")
    print(f"   单次英语: {test_date.format_weekday_localized(language_code='en_US')}")
    print(f"   仍是中文: {test_date.format_weekday_localized()}")
    
    # 7. 相对时间多语言演示
    print("\n7. 相对时间多语言演示")
    today = Date.today()
    tomorrow = today.add_days(1)
    yesterday = today.add_days(-1)
    next_week = today.add_days(7)
    
    languages = ['zh_CN', 'zh_TW', 'ja_JP', 'en_US']
    
    for lang in languages:
        set_language(lang)
        lang_name = Date.get_supported_languages()[lang]
        print(f"   {lang_name}:")
        print(f"     今天: {today.format_relative_localized()}")
        print(f"     明天: {tomorrow.format_relative_localized()}")
        print(f"     昨天: {yesterday.format_relative_localized()}")
        print(f"     下周: {next_week.format_relative_localized()}")


def demo_combined_features():
    """演示农历和多语言组合功能"""
    print("\n\n🔄 农历 + 多语言组合演示")
    print("=" * 50)
    
    # 中国传统节日
    spring_festival = Date.from_lunar(2025, 1, 1)  # 春节
    mid_autumn = Date.from_lunar(2025, 8, 15)     # 中秋
    
    festivals = [
        (spring_festival, "春节（农历正月初一）"),
        (mid_autumn, "中秋节（农历八月十五）")
    ]
    
    languages = ['zh_CN', 'zh_TW', 'ja_JP', 'en_US']
    
    for date, festival_name in festivals:
        print(f"\n{festival_name}")
        print(f"公历日期: {date.format_iso()}")
        
        for lang in languages:
            set_language(lang)
            lang_name = Date.get_supported_languages()[lang]
            print(f"  {lang_name}:")
            print(f"    本地化: {date.format_localized()}")
            print(f"    星期: {date.format_weekday_localized()}")
            print(f"    农历: {date.format_lunar()}")


def demo_performance():
    """演示性能"""
    print("\n\n⚡ 性能演示")
    print("=" * 50)
    
    import time
    
    # 农历转换性能
    start_time = time.time()
    dates = []
    for i in range(100):
        date = Date.from_lunar(2025, 1, i % 29 + 1)
        dates.append(date)
    lunar_time = time.time() - start_time
    print(f"创建100个农历日期: {lunar_time:.4f}秒")
    
    # 格式化性能
    start_time = time.time()
    test_date = Date("20250415")
    for i in range(1000):
        formatted = test_date.format_localized()
    format_time = time.time() - start_time
    print(f"格式化1000次: {format_time:.4f}秒")
    
    # 语言切换性能
    start_time = time.time()
    languages = ['zh_CN', 'zh_TW', 'ja_JP', 'en_US']
    for i in range(100):
        set_language(languages[i % 4])
    switch_time = time.time() - start_time
    print(f"语言切换100次: {switch_time:.4f}秒")


if __name__ == "__main__":
    print("🚀 Staran v1.0.8 新功能完整演示")
    print("=" * 60)
    
    try:
        # 演示农历功能
        demo_lunar_features()
        
        # 演示多语言功能
        demo_multilanguage_features()
        
        # 演示组合功能
        demo_combined_features()
        
        # 演示性能
        demo_performance()
        
        print("\n\n✅ 演示完成！")
        print("=" * 60)
        print("🌟 主要新功能:")
        print("   • 农历与公历互转")
        print("   • 农历日期格式化")
        print("   • 农历日期比较和判断")
        print("   • 中简、中繁、日、英四种语言支持")
        print("   • 全局语言设置")
        print("   • 单次使用语言覆盖")
        print("   • 多语言本地化格式")
        print("   • 120+ API方法，保持向后兼容")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 恢复默认语言
    set_language('zh_CN')
