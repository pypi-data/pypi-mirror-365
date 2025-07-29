"""
AUM业务表结构定义模块

包含AUM (资产管理)业务相关的所有标准表结构：
- 客户行为特征表 (AUMBehaviorSchema)  
- 资产平均值表 (AUMAssetAvgSchema)
- 资产配置表 (AUMAssetConfigSchema)
- 月度统计表 (AUMMonthlyStatSchema)

这些表结构可以用于：
1. 特征工程流水线
2. 数据模型构建
3. 业务文档生成
4. 数据质量检查
"""

from typing import Dict
from ...features.schema import TableSchema
from ..document_generator import SchemaDocumentGenerator


class AUMBehaviorSchema:
    """AUM客户行为特征表 - A表结构定义（严格按照已提供给行方的字段）"""
    
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
        """创建客户行为特征表结构 - 严格按照已提供给行方的字段定义"""
        schema = TableSchema('bi_hlwj_dfcw_f1_f4_wy')
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
        
        # productamount and m1 ~ m4 的含义描述 - 严格按照原始定义
        m_fields = {
            "productamount": "购买金额",
            "m1": "去重订单数",
            "m2": "去重商品数",
            "m3": "去重渠道数",
            "m4": "去重产品品类数",
        }

        # 使用循环注册 productamount and m1~m4 各统计字段 - 严格按照原始逻辑
        for prefix, meaning in m_fields.items():
            for stat_key, stat_desc in AUMBehaviorSchema._STATS:
                field_name = f"{prefix}_{stat_key}"
                description = f"{meaning}的{stat_desc}"
                schema.add_field(field_name, "float", comment=description, aggregatable=True)

        # 其他字段 - 严格按照原始定义
        schema.add_field("life_day", "float", comment="客户生命周期天数", aggregatable=True)
        schema.add_field("gender", "float", comment="性别（编码）", aggregatable=True)
        schema.add_field("open_day", "float", comment="开户天数", aggregatable=True)
        
        schema.set_monthly_unique(False)  # A表每人每日记录
        return schema
        schema.add_field("FREQ_BRANCH_CODE", "string", comment="常用网点代码")
        schema.add_field("CROSS_REGION_TXN", "string", comment="跨地区交易情况")
        
        schema.set_monthly_unique(False)  # A表每人每天一条记录
        return schema


class AUMAssetAvgSchema:
    """AUM资产平均值表 - B表结构定义（严格按照已提供给行方的字段）"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建资产平均值表结构 - 严格按照原始定义"""
        schema = TableSchema('bi_hlwj_zi_chan_avg_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 基础余额字段 - 严格按照原始定义
        schema.add_field("asset_total_bal", "decimal", comment="总资产余额", aggregatable=True)
        schema.add_field("liab_total_bal", "decimal", comment="总负债余额", aggregatable=True)
        schema.add_field("dpsit_total_bal", "decimal", comment="存款总余额", aggregatable=True)
        schema.add_field("loan_total_bal", "decimal", comment="贷款总余额", aggregatable=True)
        schema.add_field("card_total_bal", "decimal", comment="信用卡总余额", aggregatable=True)
        schema.add_field("mid_busi_total_bal", "decimal", comment="中间业务总余额", aggregatable=True)

        # Register average balance fields - 严格按照原始逻辑
        for period in ["month", "year", "3", "6", "12"]:
            schema.add_field(
                f"avg_asset_bal_{period}", "decimal", comment=f"平均资产余额 ({period}期)", aggregatable=True
            )
        for period in ["3", "12"]:
            schema.add_field(
                f"avg_dpsit_bal_{period}", "decimal", comment=f"平均存款余额 ({period}期)", aggregatable=True
            )
        
        schema.set_monthly_unique(True)  # B表每人每月唯一
        return schema


class AUMAssetConfigSchema:
    """AUM资产配置表 - C表结构定义（严格按照已提供给行方的字段）"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建资产配置表结构 - 严格按照原始定义"""
        schema = TableSchema('bi_hlwj_zi_chang_month_total_zb')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # asset_fields - 严格按照原始定义
        asset_fields = [
            ("seg_asset_total", "总资产余额"),
            ("indv_consm_loan_amt", "个人消费贷款余额"),
            ("indv_house_loan_amt", "个人住房贷款余额"),
            ("indv_oper_loan_amt", "个人经营贷款余额"),
            ("dpsit_bal", "存款余额"),
            ("tbond_bal", "国债余额"),
            ("fund_bal", "基金余额"),
            ("bond_bal", "债券余额"),
            ("gold_bal", "黄金余额"),
            ("wcurr_chrem_bal", "外币现钞余额"),
            ("presv_mgmt_secu_bal", "保值管理证券余额"),
            ("insure_form_bal", "保险单余额"),
            ("crdt_card_od_bal", "信用卡透支余额"),
            ("crdt_card_con_amt", "信用卡消费金额"),
            ("semi_crdt_card_od_bal", "准贷记卡透支余额"),
            ("semi_crdt_card_con_amt", "准贷记卡消费金额"),
            ("inter_card_con_amt", "国际卡消费金额"),
            ("inter_card_od_bal", "国际卡透支余额"),
            ("crdt_card_dpsit_bal", "信用卡存款余额"),
            ("semi_crdt_card_dpsit_bal", "准贷记卡存款余额"),
            ("inter_card_dpsit_bal", "国际卡存款余额"),
            ("silver_bal", "白银余额"),
            ("agent_solid_silver_bal", "代发实物白银余额"),
            ("pt_bal", "个人养老金余额"),
            ("pd_bal", "个人养老金存款余额"),
            ("other_metal_bal", "其他金属余额"),
            ("curr_dpsit_bal", "活期存款余额"),
            ("time_dpsit_bal", "定期存款余额"),
            ("oil_bal", "石油余额"),
            ("fx_bal", "外汇余额"),
        ]

        # 严格按照原始循环逻辑注册字段
        for field_name, desc in asset_fields:
            schema.add_field(field_name, "decimal", comment=desc, aggregatable=True)
        
        schema.set_monthly_unique(True)  # C表每人每月唯一
        return schema


class AUMMonthlyStatSchema:
    """AUM月度统计表 - D表结构定义（严格按照已提供给行方的字段）"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建月度统计表结构 - 严格按照原始定义"""
        schema = TableSchema('bi_hlwj_realy_month_stat_wy')
        schema.add_primary_key('party_id', 'string')  # 修正主键名称
        schema.add_date_field('data_dt', 'string')
        
        # channels字典 - 严格按照原始定义
        channels = {
            "CASH_DEPIST": "现金",
            "REMIT": "汇款",
            "YY": "邮政储蓄",
            "UNIONPAY": "银联",
            "FIN_ASSET": "理财产品",
            "CORP_ACCT": "对公账户",
        }

        # 注册存入和取出字段 - 严格按照原始逻辑
        for prefix, desc in channels.items():
            schema.add_field(f"{prefix}_IN", "decimal", comment=f"{desc}存入金额", aggregatable=True)
            schema.add_field(f"{prefix}_OUT", "decimal", comment=f"{desc}取出金额", aggregatable=True)

        # 其他特定字段 - 严格按照原始定义
        schema.add_field("AGENT_SALARY_IN", "decimal", comment="代发工资存入金额", aggregatable=True)
        schema.add_field("CREDIT_CARD_OUT", "decimal", comment="信用卡取出金额", aggregatable=True)
        schema.add_field("DEBIT_CARD_OUT", "decimal", comment="借记卡取出金额", aggregatable=True)
        schema.add_field("BATCH_DEDUCT_OUT", "decimal", comment="批量扣款金额", aggregatable=True)

        # 定义字段结构：交易渠道、指标、时间范围、描述前缀 - 严格按照原始定义
        fields = [
            ("DEBIT_CARD", "借记卡", "MON3"),
            ("CREDIT_CARD", "信用卡", "MON3"),
            ("THIRD_PAYMENT", "第三方支付", "MON3"),
            ("MOBBANK", "手机银行", "MON12"),
            ("TELBANK", "电话银行", "MON12"),
        ]

        # 定义交易指标 - 严格按照原始定义
        metrics = [
            ("TX_CNT", "交易次数"),
            ("TX_AMT", "交易金额"),
        ]

        # 自动注册 - 严格按照原始逻辑
        for channel, desc, period in fields:
            for metric_code, metric_desc in metrics:
                field_name = f"{channel}_{metric_code}_{period}"
                description = f"{desc}{metric_desc}（近{period[-2:]}个月）"
                schema.add_field(field_name, "decimal", comment=description, aggregatable=True)

        # 其他固定字段 - 严格按照原始定义
        schema.add_field(
            "COUNTER_TX_CNT_MON12", "int", comment="柜台交易次数（近12个月）", aggregatable=True
        )
        schema.add_field(
            "WEBBANK_TX_CNT_MON12", "int", comment="网银交易次数（近12个月）", aggregatable=True
        )

        # 编号国家（1~5） - 严格按照原始循环逻辑
        for i in range(1, 6):
            schema.add_field(
                f"Y1_OVERS_CTY{i}_CNT", "int", comment=f"近一年境外国家{i}的交易次数", aggregatable=True
            )
            schema.add_field(
                f"Y1_OVERS_CNT_CTY{i}_CD",
                "string",
                comment=f"近一年境外国家{i}的交易次数（编码）",
            )
            schema.add_field(
                f"Y1_OVERS_CTY{i}_AMT", "decimal", comment=f"近一年境外国家{i}的交易金额", aggregatable=True
            )
            schema.add_field(
                f"Y1_OVERS_AMT_CTY{i}_CD",
                "string",
                comment=f"近一年境外国家{i}的交易金额（编码）",
            )

        # 其他国家 - 严格按照原始定义
        schema.add_field(
            "Y1_OVERS_OTHER_CTY_CNT", "int", comment="近一年其他境外国家的交易次数", aggregatable=True
        )
        schema.add_field(
            "Y1_OVERS_OTHER_CTY_AMT", "decimal", comment="近一年其他境外国家的交易金额", aggregatable=True
        )
        
        schema.set_monthly_unique(True)  # D表每人每月唯一
        return schema


def get_aum_schemas() -> Dict[str, TableSchema]:
    """获取所有AUM业务表结构"""
    return {
        'behavior': AUMBehaviorSchema.create(),
        'asset_avg': AUMAssetAvgSchema.create(), 
        'asset_config': AUMAssetConfigSchema.create(),
        'monthly_stat': AUMMonthlyStatSchema.create()
    }


def export_aum_docs(output_dir: str = "./docs", format_type: str = "markdown") -> Dict[str, str]:
    """
    导出AUM表结构文档
    
    Args:
        output_dir: 输出目录
        format_type: 文档格式 ('markdown' 或 'pdf')
        
    Returns:
        生成的文档文件路径字典
    """
    schemas = get_aum_schemas()
    generator = SchemaDocumentGenerator()
    
    results = {}
    for table_type, schema in schemas.items():
        file_path = generator.export_schema_doc(
            schema=schema,
            business_domain="AUM",
            table_type=table_type,
            output_dir=output_dir,
            format_type=format_type
        )
        results[table_type] = file_path
    
    return results


__all__ = [
    'AUMBehaviorSchema',
    'AUMAssetAvgSchema', 
    'AUMAssetConfigSchema',
    'AUMMonthlyStatSchema',
    'get_aum_schemas',
    'export_aum_docs'
]
