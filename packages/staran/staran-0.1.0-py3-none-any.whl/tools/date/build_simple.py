#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化的C扩展编译脚本
使用Python的setuptools来处理复杂的链接问题
"""

from setuptools import setup, Extension
import platform
import os
import sys

def get_extension_name():
    """获取平台特定的扩展名"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'date_utils_macos'
    elif system == 'linux':
        return 'date_utils_linux'
    elif system == 'windows':
        return 'date_utils_windows'
    else:
        return 'date_utils'

def main():
    print(f"🔨 Python setuptools 编译器")
    print(f"平台: {platform.system()} {platform.machine()}")
    print(f"Python: {platform.python_version()}")
    
    extension_name = get_extension_name()
    print(f"目标模块: {extension_name}")
    
    # 定义扩展
    extension = Extension(
        extension_name,
        sources=['date_utils.c'],
        extra_compile_args=['-O3', '-std=c99'] if platform.system() != 'Windows' else ['/O2'],
    )
    
    # 编译
    setup(
        name=extension_name,
        version='1.0.0',
        ext_modules=[extension],
        zip_safe=False,
        script_args=['build_ext', '--inplace']
    )
    
    # 检查编译结果
    expected_files = []
    if platform.system() == 'Windows':
        expected_files.append(f'{extension_name}.pyd')
    else:
        expected_files.extend([
            f'{extension_name}.so',
            f'{extension_name}.cpython-*.so'
        ])
    
    print(f"\n🔍 检查编译结果...")
    found_file = None
    for pattern in expected_files:
        if '*' in pattern:
            import glob
            matches = glob.glob(pattern)
            if matches:
                found_file = matches[0]
                break
        elif os.path.exists(pattern):
            found_file = pattern
            break
    
    if found_file:
        print(f"✅ 编译成功: {found_file}")
        
        # 快速测试
        print(f"🧪 快速测试...")
        try:
            # 临时添加当前目录到路径
            if '.' not in sys.path:
                sys.path.insert(0, '.')
            
            module = __import__(extension_name)
            print(f"✅ 模块导入成功")
            
            # 测试基本功能
            today = module.get_today()
            print(f"当前日期: {today}")
            
            timestamp = module.date_to_timestamp(2024, 6, 15)
            print(f"时间戳测试: {timestamp}")
            
            platform_info = module.get_platform_info()
            print(f"平台信息: {platform_info}")
            
            print(f"🎉 所有测试通过！")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    else:
        print(f"❌ 编译失败：找不到输出文件")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
