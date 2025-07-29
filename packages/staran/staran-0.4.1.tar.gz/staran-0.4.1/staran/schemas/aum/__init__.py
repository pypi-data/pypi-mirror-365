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
    """AUM客户行为特征表 - A表结构定义"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建客户行为特征表结构"""
        schema = TableSchema('bi_hlwj_dfcw_f1_f4_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 基础信息字段
        schema.add_field("AGE", "int", comment="客户年龄", aggregatable=True)
        schema.add_field("GENDER", "string", comment="客户性别")
        schema.add_field("EDU_LEVEL", "string", comment="教育水平")
        schema.add_field("MARITAL_STATUS", "string", comment="婚姻状况")
        schema.add_field("INCOME_LEVEL", "string", comment="收入水平")
        schema.add_field("OCCUPATION", "string", comment="职业类型")
        schema.add_field("CITY_LEVEL", "string", comment="城市等级")
        
        # 账户信息字段
        schema.add_field("ACCT_OPEN_MONTHS", "int", comment="开户月数", aggregatable=True)
        schema.add_field("MAIN_ACCT_BAL", "decimal", comment="主账户余额", aggregatable=True)
        schema.add_field("ACCT_COUNT", "int", comment="账户总数", aggregatable=True)
        schema.add_field("DEPOSIT_ACCT_COUNT", "int", comment="存款账户数", aggregatable=True)
        schema.add_field("LOAN_ACCT_COUNT", "int", comment="贷款账户数", aggregatable=True)
        schema.add_field("CREDIT_CARD_COUNT", "int", comment="信用卡数量", aggregatable=True)
        
        # 交易行为字段
        schema.add_field("MON3_TXN_COUNT", "int", comment="近3月交易次数", aggregatable=True)
        schema.add_field("MON3_TXN_AMT", "decimal", comment="近3月交易金额", aggregatable=True)
        schema.add_field("MON6_TXN_COUNT", "int", comment="近6月交易次数", aggregatable=True)
        schema.add_field("MON6_TXN_AMT", "decimal", comment="近6月交易金额", aggregatable=True)
        schema.add_field("YEAR1_TXN_COUNT", "int", comment="近1年交易次数", aggregatable=True)
        schema.add_field("YEAR1_TXN_AMT", "decimal", comment="近1年交易金额", aggregatable=True)
        
        # 渠道使用偏好
        schema.add_field("ONLINE_BANK_USAGE", "string", comment="网银使用频度")
        schema.add_field("MOBILE_BANK_USAGE", "string", comment="手机银行使用频度")
        schema.add_field("ATM_USAGE", "string", comment="ATM使用频度")
        schema.add_field("COUNTER_USAGE", "string", comment="柜台使用频度")
        
        # 产品持有情况
        schema.add_field("WEALTH_PROD_COUNT", "int", comment="理财产品数量", aggregatable=True)
        schema.add_field("FUND_PROD_COUNT", "int", comment="基金产品数量", aggregatable=True)
        schema.add_field("INSURANCE_PROD_COUNT", "int", comment="保险产品数量", aggregatable=True)
        schema.add_field("GOLD_PROD_COUNT", "int", comment="黄金产品数量", aggregatable=True)
        
        # 风险评级相关
        schema.add_field("RISK_LEVEL", "string", comment="风险等级")
        schema.add_field("RISK_APPETITE", "string", comment="风险偏好")
        schema.add_field("INVESTMENT_EXPERIENCE", "string", comment="投资经验")
        
        # 服务渠道偏好
        schema.add_field("PREFER_CHANNEL", "string", comment="偏好服务渠道")
        schema.add_field("CONTACT_TIME_PREFER", "string", comment="联系时间偏好")
        
        # 客户活跃度指标
        schema.add_field("LOGIN_DAYS_MON3", "int", comment="近3月登录天数", aggregatable=True)
        schema.add_field("LOGIN_DAYS_MON6", "int", comment="近6月登录天数", aggregatable=True)
        schema.add_field("LAST_LOGIN_DAYS", "int", comment="最后登录距今天数", aggregatable=True)
        schema.add_field("ACTIVE_LEVEL", "string", comment="活跃度等级")
        
        # 客户价值指标
        schema.add_field("CUSTOMER_VALUE_SCORE", "decimal", comment="客户价值评分", aggregatable=True)
        schema.add_field("POTENTIAL_VALUE_SCORE", "decimal", comment="潜在价值评分", aggregatable=True)
        schema.add_field("RETENTION_SCORE", "decimal", comment="留存倾向评分", aggregatable=True)
        
        # 营销响应历史
        schema.add_field("CAMPAIGN_RESPONSE_RATE", "decimal", comment="营销响应率", aggregatable=True)
        schema.add_field("LAST_CAMPAIGN_RESPONSE", "string", comment="最近营销响应")
        schema.add_field("PRODUCT_CROSS_SELL_COUNT", "int", comment="交叉销售产品数", aggregatable=True)
        
        # 投诉与满意度
        schema.add_field("COMPLAINT_COUNT_YEAR1", "int", comment="近1年投诉次数", aggregatable=True)
        schema.add_field("SATISFACTION_SCORE", "decimal", comment="满意度评分", aggregatable=True)
        schema.add_field("NPS_SCORE", "decimal", comment="净推荐值", aggregatable=True)
        
        # 地理位置相关
        schema.add_field("HOME_BRANCH_CODE", "string", comment="归属网点代码")
        schema.add_field("FREQ_BRANCH_CODE", "string", comment="常用网点代码")
        schema.add_field("CROSS_REGION_TXN", "string", comment="跨地区交易情况")
        
        schema.set_monthly_unique(False)  # A表每人每天一条记录
        return schema


class AUMAssetAvgSchema:
    """AUM资产平均值表 - B表结构定义"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建资产平均值表结构"""
        schema = TableSchema('bi_hlwj_zi_chan_avg_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 各类资产平均余额
        schema.add_field("TOTAL_ASSET_AVG", "decimal", comment="总资产平均值", aggregatable=True)
        schema.add_field("DEPOSIT_AVG", "decimal", comment="存款平均余额", aggregatable=True)
        schema.add_field("CURRENT_DEPOSIT_AVG", "decimal", comment="活期存款平均余额", aggregatable=True)
        schema.add_field("TIME_DEPOSIT_AVG", "decimal", comment="定期存款平均余额", aggregatable=True)
        schema.add_field("WEALTH_PRODUCT_AVG", "decimal", comment="理财产品平均余额", aggregatable=True)
        schema.add_field("FUND_ASSET_AVG", "decimal", comment="基金资产平均值", aggregatable=True)
        schema.add_field("INSURANCE_ASSET_AVG", "decimal", comment="保险资产平均值", aggregatable=True)
        schema.add_field("BOND_ASSET_AVG", "decimal", comment="债券资产平均值", aggregatable=True)
        schema.add_field("STOCK_ASSET_AVG", "decimal", comment="股票资产平均值", aggregatable=True)
        schema.add_field("GOLD_ASSET_AVG", "decimal", comment="黄金资产平均值", aggregatable=True)
        schema.add_field("FOREX_ASSET_AVG", "decimal", comment="外汇资产平均值", aggregatable=True)
        
        # 负债相关平均值
        schema.add_field("TOTAL_DEBT_AVG", "decimal", comment="总负债平均值", aggregatable=True)
        schema.add_field("MORTGAGE_DEBT_AVG", "decimal", comment="房贷平均余额", aggregatable=True)
        schema.add_field("CREDIT_CARD_DEBT_AVG", "decimal", comment="信用卡负债平均值", aggregatable=True)
        schema.add_field("OTHER_LOAN_AVG", "decimal", comment="其他贷款平均余额", aggregatable=True)
        
        schema.set_monthly_unique(True)  # B表每人每月唯一
        return schema


class AUMAssetConfigSchema:
    """AUM资产配置表 - C表结构定义"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建资产配置表结构"""
        schema = TableSchema('bi_hlwj_zi_chang_month_total_zb')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 资产配置比例
        schema.add_field("DEPOSIT_RATIO", "decimal", comment="存款资产占比", aggregatable=True)
        schema.add_field("WEALTH_RATIO", "decimal", comment="理财产品占比", aggregatable=True)
        schema.add_field("FUND_RATIO", "decimal", comment="基金资产占比", aggregatable=True)
        schema.add_field("INSURANCE_RATIO", "decimal", comment="保险资产占比", aggregatable=True)
        schema.add_field("BOND_RATIO", "decimal", comment="债券资产占比", aggregatable=True)
        schema.add_field("STOCK_RATIO", "decimal", comment="股票资产占比", aggregatable=True)
        schema.add_field("GOLD_RATIO", "decimal", comment="黄金资产占比", aggregatable=True)
        schema.add_field("FOREX_RATIO", "decimal", comment="外汇资产占比", aggregatable=True)
        
        # 风险资产vs安全资产配置
        schema.add_field("HIGH_RISK_RATIO", "decimal", comment="高风险资产占比", aggregatable=True)
        schema.add_field("MEDIUM_RISK_RATIO", "decimal", comment="中风险资产占比", aggregatable=True)
        schema.add_field("LOW_RISK_RATIO", "decimal", comment="低风险资产占比", aggregatable=True)
        schema.add_field("SAFE_ASSET_RATIO", "decimal", comment="安全资产占比", aggregatable=True)
        
        # 流动性配置
        schema.add_field("HIGH_LIQUIDITY_RATIO", "decimal", comment="高流动性资产占比", aggregatable=True)
        schema.add_field("MEDIUM_LIQUIDITY_RATIO", "decimal", comment="中流动性资产占比", aggregatable=True)
        schema.add_field("LOW_LIQUIDITY_RATIO", "decimal", comment="低流动性资产占比", aggregatable=True)
        
        # 期限结构配置
        schema.add_field("SHORT_TERM_RATIO", "decimal", comment="短期资产占比", aggregatable=True)
        schema.add_field("MEDIUM_TERM_RATIO", "decimal", comment="中期资产占比", aggregatable=True)
        schema.add_field("LONG_TERM_RATIO", "decimal", comment="长期资产占比", aggregatable=True)
        
        # 货币配置
        schema.add_field("RMB_ASSET_RATIO", "decimal", comment="人民币资产占比", aggregatable=True)
        schema.add_field("USD_ASSET_RATIO", "decimal", comment="美元资产占比", aggregatable=True)
        schema.add_field("EUR_ASSET_RATIO", "decimal", comment="欧元资产占比", aggregatable=True)
        schema.add_field("OTHER_CURRENCY_RATIO", "decimal", comment="其他货币资产占比", aggregatable=True)
        
        # 配置集中度指标
        schema.add_field("ASSET_CONCENTRATION_INDEX", "decimal", comment="资产集中度指数", aggregatable=True)
        schema.add_field("DIVERSIFICATION_SCORE", "decimal", comment="分散化程度评分", aggregatable=True)
        
        # 动态配置指标
        schema.add_field("CONFIG_CHANGE_FREQ", "int", comment="配置调整频率", aggregatable=True)
        schema.add_field("LAST_REBALANCE_DAYS", "int", comment="最后再平衡距今天数", aggregatable=True)
        
        # 配置绩效相关
        schema.add_field("CONFIG_RETURN_RATE", "decimal", comment="配置收益率", aggregatable=True)
        schema.add_field("RISK_ADJUSTED_RETURN", "decimal", comment="风险调整收益", aggregatable=True)
        schema.add_field("SHARPE_RATIO", "decimal", comment="夏普比率", aggregatable=True)
        
        # 配置建议相关
        schema.add_field("OPTIMAL_CONFIG_SCORE", "decimal", comment="最优配置评分", aggregatable=True)
        schema.add_field("CONFIG_IMPROVEMENT_POTENTIAL", "decimal", comment="配置优化潜力", aggregatable=True)
        
        schema.set_monthly_unique(True)  # C表每人每月唯一
        return schema


class AUMMonthlyStatSchema:
    """AUM月度统计表 - D表结构定义"""
    
    @staticmethod
    def create() -> TableSchema:
        """创建月度统计表结构"""
        schema = TableSchema('bi_hlwj_realy_month_stat_wy')
        schema.add_primary_key('party_dt', 'string')  # 注意这个表的主键是party_dt
        schema.add_date_field('data_dt', 'string')
        
        # 渠道存取款字段
        channels = {
            "CASH_DEPIST": "现金",
            "REMIT": "汇款", 
            "YY": "邮政储蓄",
            "UNIONPAY": "银联",
            "FIN_ASSET": "理财产品",
            "CORP_ACCT": "对公账户"
        }
        
        for prefix, desc in channels.items():
            schema.add_field(f"{prefix}_IN", "decimal", comment=f"{desc}存入金额", aggregatable=True)
            schema.add_field(f"{prefix}_OUT", "decimal", comment=f"{desc}取出金额", aggregatable=True)
        
        # 其他存取款字段
        schema.add_field("AGENT_SALARY_IN", "decimal", comment="代发工资存入金额", aggregatable=True)
        schema.add_field("CREDIT_CARD_OUT", "decimal", comment="信用卡取出金额", aggregatable=True)
        schema.add_field("DEBIT_CARD_OUT", "decimal", comment="借记卡取出金额", aggregatable=True)
        schema.add_field("BATCH_DEDUCT_OUT", "decimal", comment="批量扣款金额", aggregatable=True)
        
        # 交易渠道指标字段
        fields = [
            ("DEBIT_CARD", "借记卡", "MON3"),
            ("CREDIT_CARD", "信用卡", "MON3"),
            ("THIRD_PAYMENT", "第三方支付", "MON3"),
            ("MOBBANK", "手机银行", "MON12"),
            ("TELBANK", "电话银行", "MON12")
        ]
        
        metrics = [("TX_CNT", "交易次数"), ("TX_AMT", "交易金额")]
        
        for channel, desc, period in fields:
            for metric_code, metric_desc in metrics:
                field_name = f"{channel}_{metric_code}_{period}"
                description = f"{desc}{metric_desc}（近{period[-2:]}个月）"
                schema.add_field(field_name, "decimal", comment=description, aggregatable=True)
        
        # 其他交易字段
        schema.add_field("COUNTER_TX_CNT_MON12", "int", comment="柜台交易次数（近12个月）", aggregatable=True)
        schema.add_field("WEBBANK_TX_CNT_MON12", "int", comment="网银交易次数（近12个月）", aggregatable=True)
        
        # 境外交易字段
        for i in range(1, 6):
            schema.add_field(f"Y1_OVERS_CTY{i}_CNT", "int", comment=f"近一年境外国家{i}的交易次数", aggregatable=True)
            schema.add_field(f"Y1_OVERS_CNT_CTY{i}_CD", "string", comment=f"近一年境外国家{i}的交易次数（编码）")
            schema.add_field(f"Y1_OVERS_CTY{i}_AMT", "decimal", comment=f"近一年境外国家{i}的交易金额", aggregatable=True)
            schema.add_field(f"Y1_OVERS_AMT_CTY{i}_CD", "string", comment=f"近一年境外国家{i}的交易金额（编码）")
        
        schema.add_field("Y1_OVERS_OTHER_CTY_CNT", "int", comment="近一年其他境外国家的交易次数", aggregatable=True)
        schema.add_field("Y1_OVERS_OTHER_CTY_AMT", "decimal", comment="近一年其他境外国家的交易金额", aggregatable=True)
        
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
