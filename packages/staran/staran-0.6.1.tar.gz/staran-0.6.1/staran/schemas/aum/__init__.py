"""
新疆工行代发长尾客户表结构定义模块

包含新疆工行代发长尾客户相关的所有表结构：
- 代发长尾客户行为特征表 (XinjiangICBCDaifaLongtailBehaviorSchema)  
- 代发长尾客户资产平均值表 (XinjiangICBCDaifaLongtailAssetAvgSchema)
- 代发长尾客户资产配置表 (XinjiangICBCDaifaLongtailAssetConfigSchema)
- 代发长尾客户月度统计表 (XinjiangICBCDaifaLongtailMonthlyStatSchema)

数据库: xinjiang_icbc_daifa_longtail
业务范围: 代发长尾客户（资产10k-100k）

这些表结构可以用于：
1. 代发长尾客户特征工程
2. 提升模型和防流失模型构建
3. 业务文档生成
4. 数据质量检查
"""

from typing import Dict
from ...features.schema import TableSchema
from ...tools.document_generator import SchemaDocumentGenerator


class XinjiangICBCDaifaLongtailBehaviorSchema:
    """新疆工行代发长尾客户行为特征表 - 严格按照已提供给行方的字段"""
    
    # 统计指标定义 - 与原始定义完全一致
    _STATS = [
        ("max", "最大值"),
        ("min", "最小值"),
        ("sum", "总和"),
        ("avg", "均值"),
        ("var", "方差"),
        ("std", "标准差"),
        ("rng", "极差"),
        ("med", "中位数"),
    ]
    
    @staticmethod
    def create() -> TableSchema:
        """创建新疆工行代发长尾客户行为特征表结构"""
        schema = TableSchema('xinjiang_icbc_daifa_hlwj_dfcw_f1_f4_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 基础字段 - 严格按照原始定义
        schema.add_field("buy_ct", "int", comment="购买次数", aggregatable=True)
        schema.add_field("recency", "int", comment="最近一次购买距今天数", aggregatable=True)
        schema.add_field("tenure", "int", comment="客户关系持续时间", aggregatable=True)
        schema.add_field("window1", "string", comment="时间窗口标记")
        schema.add_field("freq", "float", comment="总购买频率", aggregatable=True)
        schema.add_field("freq1", "float", comment="最近时间段购买频率", aggregatable=True)
        schema.add_field("productidcount", "int", comment="产品种类数", aggregatable=True)
        schema.add_field("orderidcount", "int", comment="订单数", aggregatable=True)
        schema.add_field("label", "float", comment="标签值（如是否购买）", aggregatable=True)
        
        # productamount and m1 ~ m4 的含义描述
        m_fields = {
            "productamount": "购买金额",
            "m1": "去重订单数",
            "m2": "去重商品数",
            "m3": "去重渠道数",
            "m4": "去重产品品类数",
        }

        # 使用循环注册 productamount and m1~m4 各统计字段
        for prefix, meaning in m_fields.items():
            for stat_key, stat_desc in XinjiangICBCDaifaLongtailBehaviorSchema._STATS:
                field_name = f"{prefix}_{stat_key}"
                description = f"{meaning}的{stat_desc}"
                schema.add_field(field_name, "float", comment=description, aggregatable=True)

        # 其他字段
        schema.add_field("life_day", "float", comment="客户生命周期天数", aggregatable=True)
        schema.add_field("gender", "float", comment="性别（编码）", aggregatable=True)
        schema.add_field("open_day", "float", comment="开户天数", aggregatable=True)
        
        schema.set_monthly_unique(False)  # 每人每日记录
        return schema


class XinjiangICBCDaifaLongtailAssetAvgSchema:
    """新疆工行代发长尾客户资产平均值表"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建新疆工行代发长尾客户资产平均值表结构"""
        schema = TableSchema('xinjiang_icbc_daifa_hlwj_zi_chan_avg_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 基础余额字段
        schema.add_field("asset_total_bal", "decimal", comment="总资产余额", aggregatable=True)
        schema.add_field("liab_total_bal", "decimal", comment="总负债余额", aggregatable=True)
        schema.add_field("net_asset_bal", "decimal", comment="净资产余额", aggregatable=True)
        
        # 存款相关字段
        schema.add_field("dep_bal", "decimal", comment="存款余额", aggregatable=True)
        schema.add_field("current_dep_bal", "decimal", comment="活期存款余额", aggregatable=True)
        schema.add_field("time_dep_bal", "decimal", comment="定期存款余额", aggregatable=True)
        
        # 理财投资字段
        schema.add_field("wealth_bal", "decimal", comment="理财余额", aggregatable=True)
        schema.add_field("fund_bal", "decimal", comment="基金余额", aggregatable=True)
        schema.add_field("insurance_bal", "decimal", comment="保险余额", aggregatable=True)
        
        schema.set_monthly_unique(True)  # 每人每月一条记录
        return schema


class XinjiangICBCDaifaLongtailAssetConfigSchema:
    """新疆工行代发长尾客户资产配置表"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建新疆工行代发长尾客户资产配置表结构"""
        schema = TableSchema('xinjiang_icbc_daifa_hlwj_zi_chan_config_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 资产配置比例字段
        schema.add_field("cash_ratio", "float", comment="现金类资产占比", aggregatable=True)
        schema.add_field("fixed_income_ratio", "float", comment="固收类资产占比", aggregatable=True)
        schema.add_field("equity_ratio", "float", comment="权益类资产占比", aggregatable=True)
        schema.add_field("alternative_ratio", "float", comment="另类资产占比", aggregatable=True)
        
        # 风险偏好相关
        schema.add_field("risk_level", "int", comment="风险偏好等级(1-5)", aggregatable=True)
        schema.add_field("investment_experience", "int", comment="投资经验年限", aggregatable=True)
        
        # 配置变化指标
        schema.add_field("config_change_freq", "int", comment="配置调整频率", aggregatable=True)
        schema.add_field("rebalance_count", "int", comment="再平衡次数", aggregatable=True)
        
        schema.set_monthly_unique(True)
        return schema


class XinjiangICBCDaifaLongtailMonthlyStatSchema:
    """新疆工行代发长尾客户月度统计表"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建新疆工行代发长尾客户月度统计表结构"""
        schema = TableSchema('xinjiang_icbc_daifa_hlwj_monthly_stat_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 月度交易统计
        schema.add_field("monthly_txn_count", "int", comment="月度交易笔数", aggregatable=True)
        schema.add_field("monthly_txn_amount", "decimal", comment="月度交易金额", aggregatable=True)
        schema.add_field("monthly_deposit_amount", "decimal", comment="月度存入金额", aggregatable=True)
        schema.add_field("monthly_withdraw_amount", "decimal", comment="月度取出金额", aggregatable=True)
        
        # 代发工资相关统计
        schema.add_field("salary_amount", "decimal", comment="月度代发工资金额", aggregatable=True)
        schema.add_field("salary_date", "string", comment="代发工资日期")
        schema.add_field("salary_stability", "float", comment="工资稳定性指数", aggregatable=True)
        
        # 长尾客户特征
        schema.add_field("longtail_score", "float", comment="长尾客户评分", aggregatable=True)
        schema.add_field("upgrade_potential", "float", comment="提升潜力评分", aggregatable=True)
        schema.add_field("churn_risk", "float", comment="流失风险评分", aggregatable=True)
        
        # 活跃度指标
        schema.add_field("login_days", "int", comment="月度登录天数", aggregatable=True)
        schema.add_field("channel_usage", "string", comment="渠道使用情况")
        
        schema.set_monthly_unique(True)
        return schema


def get_xinjiang_icbc_daifa_longtail_schemas() -> Dict[str, TableSchema]:
    """获取新疆工行代发长尾客户所有表结构"""
    return {
        'daifa_longtail_behavior': XinjiangICBCDaifaLongtailBehaviorSchema.create(),
        'daifa_longtail_asset_avg': XinjiangICBCDaifaLongtailAssetAvgSchema.create(),
        'daifa_longtail_asset_config': XinjiangICBCDaifaLongtailAssetConfigSchema.create(),
        'daifa_longtail_monthly_stat': XinjiangICBCDaifaLongtailMonthlyStatSchema.create(),
    }


def export_xinjiang_icbc_daifa_longtail_docs(output_dir: str = "./docs") -> Dict[str, str]:
    """导出新疆工行代发长尾客户表结构文档"""
    generator = SchemaDocumentGenerator()
    schemas = get_xinjiang_icbc_daifa_longtail_schemas()
    exported_files = {}
    
    for table_type, schema in schemas.items():
        file_path = generator.export_schema_doc(
            schema, 
            business_domain="新疆工行代发长尾客户", 
            table_type=table_type,
            output_dir=output_dir
        )
        exported_files[table_type] = file_path
    
    return exported_files


# 导出主要组件
__all__ = [
    'XinjiangICBCDaifaLongtailBehaviorSchema',
    'XinjiangICBCDaifaLongtailAssetAvgSchema', 
    'XinjiangICBCDaifaLongtailAssetConfigSchema',
    'XinjiangICBCDaifaLongtailMonthlyStatSchema',
    'get_xinjiang_icbc_daifa_longtail_schemas',
    'export_xinjiang_icbc_daifa_longtail_docs'
]
