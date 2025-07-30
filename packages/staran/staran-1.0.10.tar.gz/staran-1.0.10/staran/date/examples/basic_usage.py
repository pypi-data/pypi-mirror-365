#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础使用示例
==========

演示Staran的基本功能和用法。
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from staran.date.core import Date


def basic_usage_demo():
    """基础使用演示"""
    print("🚀 基础使用演示")
    print("=" * 40)
    
    # 创建日期对象
    print("1. 创建日期对象:")
    date1 = Date('2025')        # 年份格式
    date2 = Date('202504')      # 年月格式
    date3 = Date('20250415')    # 完整格式
    date4 = Date(2025, 4, 15)   # 参数格式
    
    print(f"   年份格式: {date1}")
    print(f"   年月格式: {date2}")
    print(f"   完整格式: {date3}")
    print(f"   参数格式: {date4}")
    print()
    
    # 智能格式记忆
    print("2. 智能格式记忆:")
    print(f"   {date1} + 1年 = {date1.add_years(1)}")
    print(f"   {date2} + 2月 = {date2.add_months(2)}")
    print(f"   {date3} + 10天 = {date3.add_days(10)}")
    print()
    
    # 多种格式输出
    print("3. 多种格式输出:")
    date = Date('20250415')
    print(f"   默认格式: {date}")
    print(f"   ISO格式: {date.format_iso()}")
    print(f"   中文格式: {date.format_chinese()}")
    print(f"   斜杠格式: {date.format_slash()}")
    print(f"   点分格式: {date.format_dot()}")
    print()


def api_demo():
    """API命名规范演示"""
    print("🏗️ 统一API命名演示")
    print("=" * 40)
    
    date = Date('20250415')
    
    # from_* 系列
    print("1. from_* 系列 (创建方法):")
    print(f"   from_string: {Date.from_string('20250415')}")
    print(f"   today: {Date.today()}")
    print()
    
    # to_* 系列
    print("2. to_* 系列 (转换方法):")
    print(f"   to_tuple: {date.to_tuple()}")
    print(f"   to_dict: {date.to_dict()}")
    print()
    
    # get_* 系列
    print("3. get_* 系列 (获取方法):")
    print(f"   get_weekday: {date.get_weekday()} (星期二)")
    print(f"   get_month_start: {date.get_month_start()}")
    print(f"   get_month_end: {date.get_month_end()}")
    print(f"   get_days_in_month: {date.get_days_in_month()}")
    print()
    
    # is_* 系列
    print("4. is_* 系列 (判断方法):")
    print(f"   is_weekend: {date.is_weekend()}")
    print(f"   is_weekday: {date.is_weekday()}")
    print(f"   is_leap_year: {date.is_leap_year()}")
    print(f"   is_month_start: {date.is_month_start()}")
    print()
    
    # add_*/subtract_* 系列
    print("5. add_*/subtract_* 系列 (运算方法):")
    print(f"   add_days(7): {date.add_days(7)}")
    print(f"   add_months(2): {date.add_months(2)}")
    print(f"   subtract_years(1): {date.subtract_years(1)}")
    print()


def comparison_demo():
    """日期比较演示"""
    print("⚖️ 日期比较演示")
    print("=" * 40)
    
    date1 = Date('20250415')
    date2 = Date('20250416')
    date3 = Date('20250415')
    
    print(f"date1 = {date1}")
    print(f"date2 = {date2}")
    print(f"date3 = {date3}")
    print()
    
    print("比较结果:")
    print(f"   date1 == date3: {date1 == date3}")
    print(f"   date1 < date2: {date1 < date2}")
    print(f"   date2 > date1: {date2 > date1}")
    print(f"   date1 <= date3: {date1 <= date3}")
    print()


def calculation_demo():
    """日期计算演示"""
    print("🧮 日期计算演示")
    print("=" * 40)
    
    date1 = Date('20250415')
    date2 = Date('20250515')
    
    print(f"date1 = {date1}")
    print(f"date2 = {date2}")
    print()
    
    days_diff = date1.calculate_difference_days(date2)
    months_diff = date1.calculate_difference_months(date2)
    
    print("计算结果:")
    print(f"   天数差: {days_diff} 天")
    print(f"   月数差: {months_diff} 个月")
    print()


def backward_compatibility_demo():
    """向后兼容性演示"""
    print("🔙 向后兼容性演示")
    print("=" * 40)
    
    date = Date('20250415')
    
    print("旧API仍然可用:")
    print(f"   format('%Y年%m月'): {date.format('%Y年%m月')}")
    print(f"   to_date(): {date.to_date()}")
    print(f"   weekday(): {date.weekday()}")
    
    other_date = Date('20250425')
    print(f"   difference(other): {date.difference(other_date)} 天")
    print()


def main():
    """主函数"""
    print("✨ Staran v1.0.2 基础使用示例")
    print("=" * 50)
    print()
    
    # 运行各个演示
    basic_usage_demo()
    api_demo()
    comparison_demo()
    calculation_demo()
    backward_compatibility_demo()
    
    print("🎉 演示完成!")
    print("更多示例请查看 staran/examples/ 目录")


if __name__ == '__main__':
    main()
