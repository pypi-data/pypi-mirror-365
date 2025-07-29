# Star## Staran ✨ v0.6.1 新特性

- � **完善的包管理** - 优化setup.py配置，移除不必要的标准库依赖
- �📋 **独立Schema模块** - 专门的表结构定义和管理模块
- 📄 **文档自动生成** - 支持Markdown/PDF/HTML格式的技术文档生成
- 🏢 **业务域支持** - AUM等业务领域的标准表结构定义
- 🔗 **无缝集成** - Schema与特征工程模块完美集成
- 🛠️ **模块化引擎架构** - 独立的引擎模块，支持Spark、Hive、图灵平台
- 🔧 **统一接口设计** - 所有引擎提供一致的SQL生成、执行和下载接口
- 🎯 **继承复用架构** - TuringEngine继承SparkEngine，复用SQL生成逻辑
- 📦 **清晰代码分离** - SQL生成与平台特定执行逻辑完全分离
- 🚀 **易于扩展** - 新增数据库支持只需实现BaseEngine接口
- 📁 **独立引擎存储** - engines/文件夹专门存放所有数据库引擎
- 🔄 **向后兼容** - 保持对原有API的完全兼容

## 🎯 专为机器学习设计的Python工具包

Staran是一个强大的特征工程和数据处理工具包，提供从数据到模型的完整解决方案。特别针对工银图灵平台优化，让特征工程和模型训练变得前所未有的简单。

## ✨ v0.6.1 新特性

- 🔧 **完善的包管理** - 优化setup.py配置，移除不必要的标准库依赖
- 🛠️ **模块化引擎架构** - 独立的引擎模块，支持Spark、Hive、图灵平台
- 🔧 **统一接口设计** - 所有引擎提供一致的SQL生成、执行和下载接口
- 🎯 **继承复用架构** - TuringEngine继承SparkEngine，复用SQL生成逻辑
- 📦 **清晰代码分离** - SQL生成与平台特定执行逻辑完全分离
- 🚀 **易于扩展** - 新增数据库支持只需实现BaseEngine接口
- 📁 **独立引擎存储** - engines/文件夹专门存放所有数据库引擎
- 🔄 **向后兼容** - 保持对原有API的完全兼容

## � 专为机器学习设计的Python工具包

Staran是一个强大的特征工程和数据处理工具包，提供从数据到模型的完整解决方案。特别针对工银图灵平台优化，让特征工程和模型训练变得前所未有的简单。

## ✨ v0.6.0 新特性

- �️ **模块化引擎架构** - 独立的引擎模块，支持Spark、Hive、图灵平台
- 🔧 **统一接口设计** - 所有引擎提供一致的SQL生成、执行和下载接口
- 🎯 **继承复用架构** - TuringEngine继承SparkEngine，复用SQL生成逻辑
- 📦 **清晰代码分离** - SQL生成与平台特定执行逻辑完全分离
- � **易于扩展** - 新增数据库支持只需实现BaseEngine接口
- � **独立引擎存储** - engines/文件夹专门存放所有数据库引擎
- 🔄 **向后兼容** - 保持对原有API的完全兼容

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

### 引擎架构 - 多平台支持

```python
from staran.engines import create_engine, create_turing_engine

# 1. 使用Spark引擎
spark_engine = create_engine('spark', 'analytics_db')

# 2. 使用Hive引擎  
hive_engine = create_engine('hive', 'warehouse_db')

# 3. 使用图灵平台引擎 (继承Spark + turingPythonLib)
turing_engine = create_turing_engine('analytics_db')

# 统一接口 - 所有引擎都支持相同方法
sql = spark_engine.generate_aggregation_sql(schema, 2025, 7, ['sum', 'avg'])
result = turing_engine.create_table('my_table', sql, execute=True)
download = turing_engine.download_table_data('my_table', 'file:///nfsHome/data.parquet')
```

### Schema模块 - 表结构管理与文档生成

```python
from staran import get_aum_schemas, export_aum_docs, SchemaDocumentGenerator

# 1. 获取预定义业务表结构
schemas = get_aum_schemas()  # 获取AUM业务域的所有表结构

for table_type, schema in schemas.items():
    print(f"{table_type}: {schema.table_name} ({len(schema.fields)}个字段)")

# 2. 生成业务文档
docs = export_aum_docs('./docs', 'markdown')  # 生成Markdown格式文档

# 3. 自定义文档生成
generator = SchemaDocumentGenerator()
doc_path = generator.export_schema_doc(
    schema=schemas['behavior'],
    business_domain="AUM",
    table_type="behavior",
    format_type="markdown"
)

# 4. 与特征工程集成
from staran import create_aum_example, run_aum_example

# 基于预定义schema创建特征工程示例
example = create_aum_example()
summary = example.get_summary()  # 获取特征统计信息

# 一键运行完整流程
results = run_aum_example('202507')  # 生成916个特征
```

### 特征工程 - SQL自动生成

```python
from staran import TableSchema, FeatureGenerator, FeatureManager

# 1. 定义表结构
schema = TableSchema('user_behavior')
schema.add_primary_key('user_id', 'string')
schema.add_date_field('date', 'date')
schema.add_field('amount', 'decimal', aggregatable=True)
schema.add_field('category', 'string')
schema.set_monthly_unique(True)

# 2. 创建特征管理器 (基于引擎架构)
manager = FeatureManager('analytics_db', engine_type='spark')

# 3. 生成特征SQL
generator = FeatureGenerator(schema, manager)
result = generator.generate_feature_by_type('aggregation', 2025, 7)
print(result['sql'])  # 自动生成的聚合特征SQL
```

### 🏦 图灵平台集成 - 一键ML流程

```python
from staran.engines import create_turing_engine

# 1. 创建图灵引擎
turing = create_turing_engine("ml_analytics")

# 2. 创建特征表
create_result = turing.create_table(
    table_name="user_features_2025_07_raw",
    select_sql="SELECT user_id, sum(amount) as total_amount FROM user_behavior GROUP BY user_id",
    execute=True,
    mode="cluster"
)

# 3. 下载特征数据
download_result = turing.download_table_data(
    table_name="user_features_2025_07_raw",
    output_path="file:///nfsHome/ml_features/user_features.parquet",
    mode="cluster"
)

# 4. 批量下载查询结果
query_result = turing.download_query_result(
    sql="SELECT user_id, label FROM ml.training_labels WHERE dt='2025-07-28'",
    output_path="file:///nfsHome/ml_labels/labels.parquet"
)

print(f"特征表创建: {create_result['status']}")
print(f"数据下载: {download_result['status']}")
```

## 📖 核心功能

### �️ 引擎架构设计

**模块化引擎架构，清晰分离关注点：**

```
BaseEngine (抽象基类)
├── SparkEngine (Spark SQL实现)
│   └── TuringEngine (继承Spark + turingPythonLib)
└── HiveEngine (Hive SQL实现)
```

| 引擎类型 | SQL生成 | 执行方式 | 下载方式 | 适用场景 |
|---------|---------|---------|---------|---------|
| SparkEngine | Spark SQL | 本地执行器 | DataFrame保存 | 本地开发、测试 |
| HiveEngine | Hive SQL | 本地执行器 | 目录导出 | 传统Hive环境 |
| TuringEngine | Spark SQL | turingPythonLib | tp.download() | 工银图灵平台 |

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
├── __init__.py                    # 主包入口，v0.6.0功能导出
├── schemas/                       # 🆕 表结构定义与文档生成模块
│   ├── __init__.py               # Schema模块入口
│   ├── document_generator.py     # 文档生成器 (MD/PDF/HTML)
│   └── aum/                      # AUM业务域表结构
│       └── __init__.py           # AUM表结构定义
├── engines/                       # 🆕 模块化引擎架构
│   ├── __init__.py               # 引擎模块入口
│   ├── base.py                   # BaseEngine抽象基类
│   ├── spark.py                  # SparkEngine实现
│   ├── hive.py                   # HiveEngine实现
│   └── turing.py                 # TuringEngine (继承SparkEngine)
├── features/                      # 🆕 特征工程模块
│   ├── __init__.py               # 特征模块入口
│   ├── manager.py                # FeatureManager (使用引擎架构)
│   ├── schema.py                 # 表结构定义
│   └── generator.py              # 特征生成器
├── examples/                      # 🆕 完整示例模块
│   ├── __init__.py               # 示例模块入口
│   └── aum_longtail.py           # AUM代发长尾模型示例
├── tools/
│   ├── __init__.py               # 工具模块
│   └── date.py                   # Date类实现
├── setup.py                      # 安装配置  
├── README.md                     # 本文档 v0.6.0
└── quick-upload.sh               # 快速部署脚本
```

## 🧪 快速测试

### 引擎架构测试
```python
from staran import create_engine, create_turing_engine

# 测试SparkEngine
spark = create_engine('spark')
print(f"Spark引擎: {spark.__class__.__name__}")

# 测试TuringEngine继承
turing = create_turing_engine("test_analytics")
print(f"Turing引擎父类: {turing.__class__.__bases__[0].__name__}")
print(f"是否为SparkEngine子类: {isinstance(turing, spark.__class__)}")

# 测试引擎功能
sql = turing.generate_sql("SELECT user_id, amount FROM users", {"table": "test"})
print(f"SQL生成测试: {'success' if sql else 'failed'}")
```

### AUM示例测试  
```python
from staran import create_aum_example

# 创建示例并查看摘要
example = create_aum_example("dwegdata03000")
example.print_summary()

# 快速运行（测试模式，不执行实际SQL）
print("🎯 AUM长尾模型示例已准备就绪")
print("📊 包含4张业务表的完整特征工程流程")
```

### 一键运行示例
```python
from staran import run_aum_example

# 最简单的使用方式
results = run_aum_example("202507")  # 指定特征月份
print(f"✅ 处理完成: {len(results)} 个表")
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

# 检查新引擎架构
from staran import create_turing_engine
turing = create_turing_engine("your_analytics_db")
print(f"✅ 引擎类型: {turing.__class__.__name__}")
print(f"✅ 继承关系: 继承自{turing.__class__.__bases__[0].__name__}")
print("🚀 环境就绪！开始特征工程之旅")
```

### 2. 运行AUM示例
```python
# 最简单的方式 - 一行代码完成复杂特征工程
from staran import run_aum_example

results = run_aum_example(
    feature_date="202507",           # 特征月份
    database="dwegdata03000",        # 数据库名
    output_path="file:///nfsHome/aum_features"  # 输出路径
)

print(f"✅ 成功！处理了4张表，生成了完整的特征数据集")
print("📂 数据已保存到 /nfsHome/aum_features/ 目录")
```

### 3. 自定义特征工程
```python
# 如需更多控制，使用详细API
from staran import create_aum_example

example = create_aum_example("dwegdata03000")

# 查看会生成哪些特征
example.print_summary()

# 运行特征工程
results = example.run("202507")

# 查看结果
for table_type, result in results.items():
    if 'table_name' in result:
        print(f"{table_type}: {result['table_name']}")
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

## 🎯 完整示例

### AUM代发长尾模型 - 简化API
位置：`staran.examples` 模块

基于真实金融业务场景的完整特征工程示例，展示了新的引擎架构优势：

```python
# 最简单的使用方式
from staran import run_aum_example

# 一键运行完整特征工程流程
results = run_aum_example(
    feature_date="202507",  # 可选，默认当前月
    database="dwegdata03000",
    output_path="file:///nfsHome/aum_longtail"
)

print(f"✅ 特征工程完成！处理了 {len(results)} 个表")
```

**更多控制的方式：**
```python
from staran import create_aum_example

# 创建示例实例
example = create_aum_example("dwegdata03000")

# 查看特征摘要
example.print_summary()

# 运行特征工程
results = example.run("202507")
```

**示例特点：**
- 🏦 **真实业务场景** - 4张银行核心业务表的完整处理
- 🔧 **智能特征配置** - A表(源表+聚合)，其他表(全特征：环比5个月+同比1年)
- 📊 **多维度特征** - 客户行为、资产配置、交易统计、境外交易等
- 🚀 **简化API** - 一行代码完成复杂特征工程
- 📋 **完整文档** - 每个字段都有详细的业务含义说明

**数据表说明：**
- **A表** (`bi_hlwj_dfcw_f1_f4_wy`): 客户行为特征 → 仅生成原始拷贝+聚合特征
- **B表** (`bi_hlwj_zi_chan_avg_wy`): 资产平均余额 → 生成全部特征(聚合+环比5个月+同比1年)
- **C表** (`bi_hlwj_zi_chang_month_total_zb`): 月度资产配置 → 生成全部特征
- **D表** (`bi_hlwj_realy_month_stat_wy`): 月度实际统计 → 生成全部特征

## 📄 许可证

MIT License

---

**Staran v0.6.0** - 模块化引擎架构，让机器学习特征工程变得前所未有的简单 🌟
