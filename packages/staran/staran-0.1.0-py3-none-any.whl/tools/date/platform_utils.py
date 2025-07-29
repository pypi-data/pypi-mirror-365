#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
跨平台C扩展加载器
支持 macOS、Linux、Windows 平台的自动检测和加载
"""

import os
import sys
import platform
import importlib.util
from datetime import datetime

class PlatformDateUtils:
    """跨平台日期工具类，优先使用C扩展，回退到Python实现"""
    
    def __init__(self):
        """初始化平台工具"""
        self.tools_dir = os.path.dirname(os.path.abspath(__file__))
        self.c_utils = self._load_c_extension()
        self.is_available = self.c_utils is not None
        self.has_c_extension = self.is_available
    
    def _get_extension_filename(self):
        """根据平台获取C扩展文件名"""
        system = platform.system().lower()
        
        # Python版本信息
        python_version = f"cpython-{sys.version_info.major}{sys.version_info.minor}"
        
        if system == 'darwin':  # macOS
            base_names = [
                f'date_utils_macos.{python_version}-darwin.so',
                'date_utils_macos.so'
            ]
        elif system == 'linux':
            base_names = [
                f'date_utils_linux.{python_version}-linux.so',
                'date_utils_linux.so'
            ]
        elif system == 'windows':
            base_names = [
                f'date_utils_windows.{python_version}.pyd',
                'date_utils_windows.pyd'
            ]
        else:
            base_names = ['date_utils.so']
        
        return base_names
    
    def _load_c_extension(self):
        """尝试加载C扩展"""
        try:
            # 获取可能的扩展文件名列表
            extension_files = self._get_extension_filename()
            
            # 尝试每个文件名
            for extension_file in extension_files:
                extension_path = os.path.join(self.tools_dir, extension_file)
                
                if os.path.exists(extension_path):
                    try:
                        # 加载扩展模块
                        spec = importlib.util.spec_from_file_location("date_utils", extension_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # 验证必要的函数是否存在
                        required_functions = ['get_today', 'date_to_timestamp', 'days_between_c', 'is_leap_year_c']
                        for func_name in required_functions:
                            if not hasattr(module, func_name):
                                print(f"Warning: C extension missing function: {func_name}")
                                continue  # 尝试下一个文件
                        
                        print(f"Successfully loaded C extension: {extension_file}")
                        return module
                    except Exception as e:
                        print(f"Failed to load {extension_file}: {e}")
                        continue  # 尝试下一个文件
            
            # 如果没有找到文件，尝试直接导入
            sys.path.insert(0, self.tools_dir)
            try:
                import date_utils as c_utils
                print("Successfully loaded C extension via direct import")
                return c_utils
            except ImportError:
                pass
            finally:
                if self.tools_dir in sys.path:
                    sys.path.remove(self.tools_dir)
                        
        except Exception as e:
            print(f"Error loading C extension: {e}")
        
        return None
    
    def get_today(self):
        """获取当前日期"""
        if self.has_c_extension and self.c_utils:
            try:
                return self.c_utils.get_today()
            except Exception as e:
                print(f"⚠️  C扩展get_today失败，回退到Python: {e}")
        
        # Python备用实现
        import datetime
        today = datetime.date.today()
        return (today.year, today.month, today.day)
    
    def date_to_timestamp(self, year, month, day):
        """日期转时间戳"""
        if self.has_c_extension and self.c_utils:
            try:
                return self.c_utils.date_to_timestamp(year, month, day)
            except Exception as e:
                print(f"⚠️  C扩展date_to_timestamp失败，回退到Python: {e}")
        
        # Python备用实现
        import datetime
        try:
            date = datetime.date(year, month, day)
            dt = datetime.datetime.combine(date, datetime.time())
            return dt.timestamp()
        except ValueError as e:
            raise ValueError(f"Invalid date: {e}")
    
    def days_between(self, year1, month1, day1, year2, month2, day2):
        """计算两个日期之间的天数差"""
        if self.has_c_extension and self.c_utils:
            try:
                return self.c_utils.days_between_c(year1, month1, day1, year2, month2, day2)
            except Exception as e:
                print(f"⚠️  C扩展days_between失败，回退到Python: {e}")
        
        # Python备用实现
        import datetime
        try:
            date1 = datetime.date(year1, month1, day1)
            date2 = datetime.date(year2, month2, day2)
            return (date2 - date1).days
        except ValueError as e:
            raise ValueError(f"Invalid date: {e}")
    
    def is_leap_year(self, year):
        """判断是否为闰年"""
        if self.has_c_extension and self.c_utils:
            try:
                return self.c_utils.is_leap_year_c(year)
            except Exception as e:
                print(f"⚠️  C扩展is_leap_year失败，回退到Python: {e}")
        
        # Python备用实现
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# 创建全局实例
_platform_utils = PlatformDateUtils()

# 导出函数接口
def get_today():
    """获取当前日期"""
    return _platform_utils.get_today()

def date_to_timestamp(year, month, day):
    """日期转时间戳"""
    return _platform_utils.date_to_timestamp(year, month, day)

def days_between(year1, month1, day1, year2, month2, day2):
    """计算日期间隔"""
    return _platform_utils.days_between(year1, month1, day1, year2, month2, day2)

def is_leap_year_c(year):
    """判断闰年"""
    return _platform_utils.is_leap_year(year)

def has_c_extension():
    """检查是否有C扩展可用"""
    return _platform_utils.has_c_extension

def get_platform_info():
    """获取平台信息"""
    return {
        'system': platform.system(),
        'machine': platform.machine(),
        'python_version': platform.python_version(),
        'has_c_extension': _platform_utils.has_c_extension,
        'expected_extension': _platform_utils._get_extension_filename()
    }
