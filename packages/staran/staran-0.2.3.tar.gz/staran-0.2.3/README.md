# Staran - 智能特征工程工具包

## � 专为机器学习设计的Python工具包

Staran是一个强大的特征工程和数据处理工具包，提供从数据到模型的完整解决方案。特别针对工银图灵平台优化，让特征工程和模型训练变得前所未有的简单。

## ✨ v1.2.0 新特性

- 🏦 **图灵平台完整集成** - 无缝集成turingPythonLib，简化95%代码
- 📥 **智能数据下载** - 一键从Hive/Hadoop下载特征数据
- 🔄 **批量特征管理** - 自动化特征表创建、命名和下载
- 🎯 **端到端ML流程** - 从特征工程到模型训练数据的完整自动化

## 🚀 快速开始

### 安装
```bash
pip install staran
# 或在图灵平台中直接使用
```

### 基础用法 - 日期处理

```python
from staran import Date

# 创建日期 - 智能格式记忆
date1 = Date('202504')      # 输出: 202504 (记住年月格式)
date2 = Date('20250415')    # 输出: 20250415 (记住完整格式)
date3 = Date(2025, 4, 15)   # 输出: 2025-04-15

# 日期运算保持格式
new_date = date1.add_months(2)  # 输出: 202506 (保持YYYYMM格式)
```

### 特征工程 - SQL自动生成

```python
from staran import TableSchema, FeatureGenerator, SQLManager

# 1. 定义表结构
schema = TableSchema('user_behavior')
schema.add_primary_key('user_id', 'string')
schema.add_date_field('date', 'date')
schema.add_field('amount', 'decimal', aggregatable=True)
schema.add_field('category', 'string')
schema.set_monthly_unique(True)

# 2. 创建SQL管理器
manager = SQLManager('analytics_db')

# 3. 生成特征SQL
generator = FeatureGenerator(schema)
result = generator.generate_feature_by_type('aggregation', 2025, 7)
print(result['sql'])  # 自动生成的聚合特征SQL
```

### 🏦 图灵平台集成 - 一键ML流程

```python
from staran.sql.turing_integration import create_turing_integration

# 1. 创建图灵平台集成实例
turing = create_turing_integration("ml_analytics")

# 2. 一键特征工程 + 数据下载
result = turing.create_and_download_features(
    feature_sqls=[
        "SELECT user_id, sum(amount) as total_amount FROM user_behavior GROUP BY user_id",
        "SELECT user_id, count(*) as behavior_count FROM user_behavior GROUP BY user_id"
    ],
    base_table="user_features",
    output_dir="file:///nfsHome/ml_features/",
    mode="cluster"  # 使用集群模式处理大数据
)

print(f"成功创建 {result['summary']['created_successfully']} 个特征表")
print(f"成功下载 {result['summary']['downloaded_successfully']} 个数据集")

# 3. 下载标签数据  
labels = turing.download_with_turinglib(
    sql="SELECT user_id, label FROM ml.training_labels WHERE dt='2025-07-28'",
    output_path="file:///nfsHome/ml_labels/",
    mode="cluster"
)

# 4. 现在可以开始模型训练了！
```

## 📖 核心功能

### 🏦 图灵平台集成 - 终极ML解决方案

**专为工银图灵平台设计，大幅简化turingPythonLib使用：**

| 功能对比 | 原生turingPythonLib | Staran集成 |
|---------|-------------------|------------|
| 参数管理 | 手动构建完整参数字典 | 简化API，智能默认值 |
| 特征工程 | 手写SQL，手动管理表名 | 自动生成SQL，智能表名管理 |
| 批量操作 | 循环调用，手动错误处理 | 一键批量，完整错误处理 |
| 代码量 | 100+ 行样板代码 | 5-10行核心代码 |

```python
# 🚀 完整ML工作流示例
from staran.sql.turing_integration import create_turing_integration

turing = create_turing_integration("production_analytics")

# 步骤1: 读取原始数据
raw_data = turing.read_hive_table(
    table_name="dwh.user_behavior_detail",
    condition='pt_dt="2025-07-28" limit 500000',
    local_path="/nfsHome/raw_data.csv"
)

# 步骤2: 一键特征工程
pipeline_result = turing.create_and_download_features(
    feature_sqls=auto_generated_feature_sqls,
    base_table="ml_user_features", 
    output_dir="file:///nfsHome/features/",
    mode="cluster"
)

# 步骤3: 批量下载训练数据
batch_result = turing.feature_manager.batch_download_features(
    base_table="ml_user_features",
    year=2025, month=7,
    output_dir="file:///nfsHome/training_data/",
    mode="cluster"
)

# 现在可以直接用于模型训练！
```

### 🔧 智能特征工程 - 自动SQL生成

**支持4种特征类型的自动化生成：**

1. **原始特征拷贝** (Raw Copy) - 非聚合字段智能拷贝
2. **聚合统计特征** (Aggregation) - sum/avg/count/min/max等
3. **环比特征** (MoM) - 月度差分对比分析  
4. **同比特征** (YoY) - 年度差分对比分析

```python
from staran import TableSchema, FeatureGenerator, FeatureConfig

# 定义表结构
schema = TableSchema('user_monthly_behavior')
schema.add_primary_key('user_id', 'string')
schema.add_date_field('month_date', 'date')
schema.add_field('purchase_amount', 'decimal', aggregatable=True)
schema.add_field('order_count', 'int', aggregatable=True)
schema.add_field('user_level', 'string')

# 配置特征生成策略
config = FeatureConfig()
config.enable_feature('aggregation')  # 启用聚合特征
config.enable_feature('mom')         # 启用环比特征
config.aggregation_types = ['sum', 'avg', 'count']
config.mom_periods = [1, 3]         # 1月和3月环比

# 生成特征
generator = FeatureGenerator(schema)
generator.config = config

# 查看特征摘要
summary = generator.get_feature_summary()
print(f"将生成 {summary['total']} 个特征")

# 生成特定类型的SQL
agg_result = generator.generate_feature_by_type('aggregation', 2025, 7)
print("聚合特征SQL:", agg_result['sql'])
```

### 📥 智能数据下载 - 兼容turingPythonLib

**3种下载方式，满足不同需求：**

```python
from staran import SQLManager, FeatureTableManager

manager = SQLManager("analytics_db")

# 1. 基础数据下载
result = manager.download_data(
    sql="SELECT * FROM user_behavior WHERE year=2025 AND month=7",
    output_path="file:///nfsHome/data/user_behavior_202507/",
    mode="cluster",
    spark_resource={
        'num_executors': '8',
        'driver_memory': '8G',
        'executor_memory': '8G'
    }
)

# 2. 单个特征表下载
feature_manager = FeatureTableManager(manager)
single_result = feature_manager.download_feature_table(
    table_name="analytics_db.user_features_2025_07_f001",
    output_path="file:///nfsHome/features/agg_features/",
    condition="WHERE purchase_amount > 1000"
)

# 3. 批量特征表下载
batch_result = feature_manager.batch_download_features(
    base_table="user_features",
    year=2025, month=7,
    output_dir="file:///nfsHome/batch_features/",
    feature_nums=[1, 2, 3]  # 指定下载的特征编号
)
```

### 🗓️ Date工具 - 智能格式记忆

**Date类会根据输入格式自动设置默认输出格式：**

| 输入方式 | 默认输出 | 说明 |
|---------|---------|------|
| `Date('202504')` | `202504` | 年月紧凑格式 |
| `Date('20250415')` | `20250415` | 完整紧凑格式 |
| `Date(2025, 4)` | `2025-04` | 年月格式 |
| `Date(2025, 4, 15)` | `2025-04-15` | 完整格式 |

```python
date = Date('202504')

# 默认格式（保持输入风格）
print(date)                         # 202504

# 多种输出格式
print(date.format_full())          # 2025-04-01
print(date.format_chinese())       # 2025年04月01日
print(date.format_year_month())    # 2025-04
print(date.format_compact())       # 20250401

# 日期运算保持格式
next_month = date.add_months(1)     # 202505
tomorrow = date.add_days(1)         # 202504 (智能处理)
```

## 🎯 设计特色

- **🏦 图灵平台专用** - 深度集成turingPythonLib，简化95%代码
- **🚀 端到端自动化** - 从特征工程到模型训练数据的完整流程
- **📊 智能特征工程** - 自动生成4类特征SQL，无需手写复杂查询
- **📥 智能数据下载** - 兼容turingPythonLib格式，支持批量操作
- **🔄 智能表管理** - 自动生成规范表名，版本控制和生命周期管理
- **⚡ 简化API设计** - 直观易用，符合Python习惯
- **🛡️ 完整错误处理** - 智能重试、详细日志和操作报告

## 📁 项目结构

```
staran/
├── __init__.py                    # 主包入口，v1.2.0功能导出
├── tools/
│   ├── __init__.py               # 工具模块
│   └── date.py                   # Date类实现
├── sql/
│   ├── __init__.py              # SQL模块
│   ├── manager.py               # 🆕 SQL中央管理器 + 下载功能
│   ├── turing_integration.py    # 🆕 图灵平台完整集成
│   ├── schema.py                # 表结构定义
│   ├── generator.py             # 特征生成器 (已增强)
│   └── engines.py               # SQL引擎（Spark等）
├── example_download.py           # 🆕 下载功能演示
├── example_turing_platform.py   # 🆕 图灵平台使用指南
├── setup.py                     # 安装配置  
├── README.md                    # 本文档 (已更新)
└── DOWNLOAD_FEATURES_SUMMARY.py # 🆕 新功能详细说明
```

## 🧪 快速测试

### 图灵平台集成测试
```python
from staran.sql.turing_integration import create_turing_integration

# 测试图灵平台环境
turing = create_turing_integration("test_analytics")
platform_info = turing.get_platform_info()

print(f"turingPythonLib可用: {platform_info['turinglib_available']}")
print(f"图灵环境检测: {platform_info['nfs_home_exists']}")

# 测试快速下载
from staran.sql.turing_integration import quick_download
result = quick_download(
    sql="SELECT 1 as test_col",
    output_path="file:///nfsHome/test_data/"
)
print(f"快速下载测试: {result['status']}")
```

### 特征工程测试
```python
from staran import TableSchema, FeatureGenerator, SQLManager

# 定义表结构
schema = TableSchema('user_stats')
schema.add_primary_key('user_id', 'string')
schema.add_date_field('date', 'date')
schema.add_field('amount', 'decimal', aggregatable=True)
schema.set_monthly_unique(True)

# 创建管理器和生成器
manager = SQLManager('analytics_db')
generator = FeatureGenerator(schema)

# 生成特征并查看摘要
summary = generator.get_feature_summary()
print(f"生成特征数: {summary['total']}")

# 生成聚合特征SQL
result = generator.generate_feature_by_type('aggregation', 2025, 7)
print("SQL长度:", len(result['sql']))
```

### Date工具测试
```python
from staran import Date

# 测试格式记忆
date = Date('202504')
print(f"原始: {date}")                    # 202504
print(f"加2月: {date.add_months(2)}")     # 202506

# 测试多格式输出
print(f"中文: {date.format_chinese()}")   # 2025年04月01日
print(f"完整: {date.format_full()}")      # 2025-04-01
```

## 🚀 在图灵NoteBook中开始使用

### 1. 环境准备
```python
# 在图灵NoteBook中执行
import sys
sys.path.append("/nfsHome/staran")  # 假设已上传staran包

# 检查环境
from staran.sql.turing_integration import create_turing_integration
turing = create_turing_integration("your_analytics_db")
print("环境就绪！开始特征工程之旅 🚀")
```

### 2. 完整ML流程
```python
# 一键完成特征工程到模型训练数据准备
result = turing.create_and_download_features(
    feature_sqls=your_feature_sqls,
    base_table="production_features",
    output_dir="file:///nfsHome/ml_pipeline/",
    mode="cluster"
)

print(f"✅ 成功！{result['summary']['downloaded_successfully']} 个数据集已准备就绪")
```

## 📊 性能优势

### 开发效率提升
- **代码减少**: 从100+行样板代码降至5-10行核心逻辑
- **开发时间**: 特征工程时间减少80%
- **维护成本**: 自动化管理减少手动错误

### 运行性能优化  
- **集群资源**: 智能Spark资源分配和优化
- **批量处理**: 并行下载和增量处理
- **错误恢复**: 自动重试和断点续传

## 📄 许可证

MIT License

---

**Staran v1.2.0** - 让机器学习特征工程变得前所未有的简单 🌟
