#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图灵平台引擎
继承Spark引擎，重写执行和下载方法以使用turingPythonLib
"""

from typing import Dict, Any, Optional, List, Callable
import sys
import os
from datetime import datetime
from .spark import SparkEngine

# 尝试导入turingPythonLib（在图灵平台环境中）
try:
    sys.path.append("/nfsHome/")
    import turingPythonLib as tp
    TURINGLIB_AVAILABLE = True
except ImportError:
    tp = None
    TURINGLIB_AVAILABLE = False


class TuringEngine(SparkEngine):
    """
    图灵平台引擎
    继承Spark引擎，使用turingPythonLib进行SQL执行和数据下载
    """
    
    def __init__(self, database_name: str, sql_executor: Optional[Callable] = None):
        # 不使用传入的sql_executor，因为我们使用turingPythonLib
        super().__init__(database_name, None)
        
        # 检查turingPythonLib是否可用
        if not TURINGLIB_AVAILABLE:
            print("⚠️  警告: turingPythonLib不可用，将使用模拟模式")
    
    def get_engine_name(self) -> str:
        return "Turing Platform (Spark)"
    
    # ==================== 重写SQL执行方法 ====================
    
    def execute_sql(self, sql: str, description: str = "") -> Any:
        """
        使用turingPythonLib执行SQL
        
        Args:
            sql: SQL语句
            description: 执行描述
            
        Returns:
            执行结果
        """
        if TURINGLIB_AVAILABLE:
            try:
                # 使用turingPythonLib执行SQL
                result = tp.execute_sql(sql)
                
                self.execution_history.append({
                    'sql': sql,
                    'description': description,
                    'timestamp': datetime.now(),
                    'result': result,
                    'platform': 'turingPythonLib'
                })
                
                return result
                
            except Exception as e:
                error_result = {
                    'status': 'error',
                    'message': f"执行SQL失败: {str(e)}",
                    'error': str(e)
                }
                
                self.execution_history.append({
                    'sql': sql,
                    'description': description,
                    'timestamp': datetime.now(),
                    'result': error_result,
                    'platform': 'turingPythonLib'
                })
                
                return error_result
        else:
            # 模拟模式
            print(f"模拟执行SQL: {description or 'SQL语句'}")
            print(f"  {sql[:100]}...")
            
            mock_result = {
                'status': 'simulated',
                'message': '模拟执行成功',
                'sql': sql[:100] + '...'
            }
            
            self.execution_history.append({
                'sql': sql,
                'description': description,
                'timestamp': datetime.now(),
                'result': mock_result,
                'platform': 'simulation'
            })
            
            return mock_result
    
    def create_table(self, table_name: str, select_sql: str, 
                    execute: bool = False, mode: str = "cluster",
                    spark_resource: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        使用turingPythonLib创建表
        
        Args:
            table_name: 表名
            select_sql: 选择SQL
            execute: 是否立即执行
            mode: 运行模式 ('local' 或 'cluster')
            spark_resource: Spark资源配置
            
        Returns:
            创建结果
        """
        full_table_name = self.get_full_table_name(table_name)
        
        result = {
            'table_name': table_name,
            'full_table_name': full_table_name,
            'select_sql': select_sql,
            'executed': execute,
            'mode': mode
        }
        
        if execute:
            if TURINGLIB_AVAILABLE:
                # 构建turingPythonLib参数
                params = {
                    'create_mode': 'by_select',
                    'table_name': full_table_name,
                    'sql': select_sql,
                    'run_mode': mode
                }
                
                # 如果是集群模式且提供了资源配置
                if mode == 'cluster' and spark_resource:
                    params['spark_resource'] = spark_resource
                elif mode == 'cluster':
                    # 使用默认资源配置
                    params['spark_resource'] = {
                        'num_executors': '4',
                        'driver_cores': '2',
                        'driver_memory': '4G',
                        'executor_cores': '2',
                        'executor_memory': '4G'
                    }
                
                try:
                    tp_result = tp.create_hive_table(params)
                    
                    result.update({
                        'status': 'success',
                        'message': f"成功创建表: {full_table_name}",
                        'turinglib_result': tp_result,
                        'params': params
                    })
                    
                except Exception as e:
                    result.update({
                        'status': 'error',
                        'message': f"创建表失败: {str(e)}",
                        'error': str(e),
                        'params': params
                    })
            else:
                # 模拟模式
                result.update({
                    'status': 'simulated',
                    'message': f"模拟创建表: {full_table_name}",
                    'simulated': True
                })
        else:
            result['status'] = 'prepared'
        
        return result
    
    # ==================== 重写数据下载方法 ====================
    
    def download_table_data(self, table_name: str, output_path: str,
                          source: str = "hadoop", mode: str = "cluster",
                          columns: str = "*", condition: str = "",
                          overwrite_path: str = "yes",
                          spark_resource: Optional[Dict[str, str]] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        使用turingPythonLib下载表数据
        
        Args:
            table_name: 要下载的表名
            output_path: 输出路径，必须以 'file:///nfsHome/' 开头
            source: 数据源类型 ('hadoop' 或 'mppdb')
            mode: 运行模式 ('local' 或 'cluster')
            columns: 要选择的列，默认为 "*"
            condition: WHERE条件
            overwrite_path: 是否覆盖路径 ('yes' 或 'no')
            spark_resource: 集群模式下的资源配置
            **kwargs: 其他参数
            
        Returns:
            下载结果
        """
        # 验证输出路径
        if not output_path.startswith('file:///nfsHome/'):
            raise ValueError("输出路径必须以 'file:///nfsHome/' 开头")
        
        full_table_name = self.get_full_table_name(table_name)
        
        # 构建下载SQL
        sql = f"SELECT {columns} FROM {full_table_name}"
        if condition.strip():
            if not condition.upper().strip().startswith('WHERE'):
                condition = f"WHERE {condition}"
            sql += f" {condition}"
        
        # 构建下载参数
        params = {
            'sql': sql,
            'source': source,
            'outputPath': output_path,
            'overwrite_path': overwrite_path,
            'mode': mode
        }
        
        # 如果是集群模式且提供了资源配置
        if mode == 'cluster' and spark_resource:
            params['spark_resource'] = spark_resource
        elif mode == 'cluster':
            # 使用默认资源配置
            params['spark_resource'] = {
                'num_executors': '4',
                'driver_cores': '2', 
                'driver_memory': '4G',
                'executor_cores': '2',
                'executor_memory': '4G'
            }
        
        try:
            if TURINGLIB_AVAILABLE:
                # 使用真实的turingPythonLib
                tp_result = tp.download(params)
                
                # 判断下载是否成功
                if isinstance(tp_result, dict) and tp_result.get('success') == '0':
                    return {
                        'status': 'success',
                        'message': f'数据已下载到: {output_path}',
                        'table_name': table_name,
                        'output_path': output_path,
                        'turinglib_result': tp_result,
                        'params': params
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f"下载失败: {tp_result.get('data', '未知错误')}",
                        'table_name': table_name,
                        'turinglib_result': tp_result,
                        'params': params
                    }
            else:
                # 模拟模式
                return {
                    'status': 'simulated',
                    'message': f'模拟下载到: {output_path}',
                    'table_name': table_name,
                    'output_path': output_path,
                    'turinglib_result': {'success': '0', 'message': '模拟下载成功'},
                    'params': params,
                    'simulated': True
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"下载异常: {str(e)}",
                'table_name': table_name,
                'error': str(e),
                'params': params
            }
    
    def download_query_result(self, sql: str, output_path: str,
                            source: str = "hadoop", mode: str = "cluster",
                            overwrite_path: str = "yes",
                            spark_resource: Optional[Dict[str, str]] = None,
                            **kwargs) -> Dict[str, Any]:
        """
        直接下载查询结果，使用turingPythonLib
        
        Args:
            sql: 查询SQL
            output_path: 输出路径
            source: 数据源类型
            mode: 运行模式
            overwrite_path: 是否覆盖路径
            spark_resource: 资源配置
            **kwargs: 其他参数
            
        Returns:
            下载结果
        """
        # 验证输出路径
        if not output_path.startswith('file:///nfsHome/'):
            raise ValueError("输出路径必须以 'file:///nfsHome/' 开头")
        
        # 构建下载参数
        params = {
            'sql': sql,
            'source': source,
            'outputPath': output_path,
            'overwrite_path': overwrite_path,
            'mode': mode
        }
        
        # 如果是集群模式且提供了资源配置
        if mode == 'cluster' and spark_resource:
            params['spark_resource'] = spark_resource
        elif mode == 'cluster':
            params['spark_resource'] = {
                'num_executors': '4',
                'driver_cores': '2', 
                'driver_memory': '4G',
                'executor_cores': '2',
                'executor_memory': '4G'
            }
        
        try:
            if TURINGLIB_AVAILABLE:
                tp_result = tp.download(params)
                
                if isinstance(tp_result, dict) and tp_result.get('success') == '0':
                    return {
                        'status': 'success',
                        'message': f'查询结果已下载到: {output_path}',
                        'output_path': output_path,
                        'turinglib_result': tp_result,
                        'params': params
                    }
                else:
                    return {
                        'status': 'error',
                        'message': f"下载失败: {tp_result.get('data', '未知错误')}",
                        'turinglib_result': tp_result,
                        'params': params
                    }
            else:
                return {
                    'status': 'simulated',
                    'message': f'模拟下载查询结果到: {output_path}',
                    'output_path': output_path,
                    'turinglib_result': {'success': '0', 'message': '模拟下载成功'},
                    'params': params,
                    'simulated': True
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f"下载查询结果失败: {str(e)}",
                'error': str(e),
                'params': params
            }
    
    # ==================== 图灵平台特有方法 ====================
    
    def install_python_packages(self, packages: List[str]) -> Dict[str, Any]:
        """
        安装Python包（使用turingPythonLib）
        
        Args:
            packages: 要安装的包列表
            
        Returns:
            安装结果
        """
        results = []
        
        for package in packages:
            try:
                if TURINGLIB_AVAILABLE:
                    tp.pip_install(package)
                    results.append({
                        'package': package,
                        'status': 'success',
                        'message': f'成功安装 {package}'
                    })
                else:
                    results.append({
                        'package': package,
                        'status': 'simulated',
                        'message': f'模拟安装 {package} (turingPythonLib不可用)'
                    })
            except Exception as e:
                results.append({
                    'package': package,
                    'status': 'error',
                    'error': str(e),
                    'message': f'安装 {package} 失败'
                })
        
        return {
            'total_packages': len(packages),
            'successful_installs': len([r for r in results if r['status'] == 'success']),
            'results': results
        }
    
    def get_platform_info(self) -> Dict[str, Any]:
        """获取图灵平台信息"""
        return {
            'engine_name': self.get_engine_name(),
            'engine_type': self.get_engine_type().value,
            'turinglib_available': TURINGLIB_AVAILABLE,
            'nfs_home_exists': os.path.exists('/nfsHome'),
            'database_name': self.database_name,
            'current_working_dir': os.getcwd(),
            'python_path': sys.path[:3]  # 只显示前3个路径
        }


# 便捷创建函数
def create_turing_engine(database_name: str, **kwargs) -> TuringEngine:
    """
    便捷函数：创建图灵引擎实例
    
    Args:
        database_name: 数据库名称
        **kwargs: 其他参数
        
    Returns:
        图灵引擎实例
    """
    return TuringEngine(database_name, **kwargs)
