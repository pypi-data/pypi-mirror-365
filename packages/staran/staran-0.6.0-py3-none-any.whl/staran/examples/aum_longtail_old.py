"""
AUM代发长尾模型示例
基于Staran v0.3.0架构，使用schemas模块的预定义表结构
"""

from typing import Dict, List, Optional
from ..engines import create_turing_engine
from ..features import FeatureManager, FeatureConfig, FeatureType
from ..tools import Date
from ..schemas.aum import get_aum_schemas


class AUMLongtailExample:
    """AUM代发长尾模型示例类"""
    
    def __init__(self, database: str = "dwegdata03000"):
        """
        初始化AUM长尾模型示例
        
        Args:
            database: 数据库名称，默认为dwegdata03000
        """
        self.database = database
        self.engine = create_turing_engine(database)
        self.schemas = get_aum_schemas()  # 从schemas模块获取预定义的表结构
        
    def run(self, feature_date: Optional[str] = None, output_path: str = "file:///nfsHome/aum_longtail") -> Dict:
        """创建表结构定义"""
        schemas = {}
        
        # A表：bi_hlwj_dfcw_f1_f4_wy - 客户行为特征表（只生成原始拷贝和聚合特征）
        schemas['behavior'] = self._create_behavior_schema()
        
        # B表：bi_hlwj_zi_chan_avg_wy - 资产平均余额表（生成全部特征）
        schemas['asset_avg'] = self._create_asset_avg_schema()
        
        # C表：bi_hlwj_zi_chang_month_total_zb - 月度资产配置表（生成全部特征）
        schemas['asset_config'] = self._create_asset_config_schema()
        
        # D表：bi_hlwj_realy_month_stat_wy - 月度实际统计表（生成全部特征）
        schemas['monthly_stat'] = self._create_monthly_stat_schema()
        
        return schemas
    
    def _create_behavior_schema(self) -> TableSchema:
        """创建A表结构 - 客户行为特征表"""
        schema = TableSchema('bi_hlwj_dfcw_f1_f4_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 基础行为字段
        schema.add_field("buy_ct", "string", comment="购买次数", aggregatable=True)
        schema.add_field("recency", "string", comment="最近一次购买距今天数", aggregatable=True)
        schema.add_field("tenure", "string", comment="客户关系持续时间", aggregatable=True)
        schema.add_field("window1", "string", comment="时间窗口标记")
        schema.add_field("freq", "string", comment="总购买频率", aggregatable=True)
        schema.add_field("freq1", "string", comment="最近时间段购买频率", aggregatable=True)
        schema.add_field("productidcount", "string", comment="产品种类数", aggregatable=True)
        schema.add_field("orderidcount", "string", comment="订单数", aggregatable=True)
        schema.add_field("productcategorycount", "string", comment="产品品类数", aggregatable=True)
        
        # productamount和m1~m4统计字段
        stats_fields = [
            ("max", "最大值"), ("min", "最小值"), ("sum", "总和"), 
            ("avg", "平均值"), ("var", "方差"), ("std", "标准差"), 
            ("rng", "范围"), ("med", "中位数")
        ]
        
        m_fields = {
            "productamount": "购买金额",
            "m1": "去重订单数",
            "m2": "去重商品数", 
            "m3": "去重渠道数",
            "m4": "去重产品品类数"
        }
        
        for prefix, meaning in m_fields.items():
            for stat_key, stat_desc in stats_fields:
                field_name = f"{prefix}_{stat_key}"
                description = f"{meaning}的{stat_desc}"
                schema.add_field(field_name, "string", comment=description, aggregatable=True)
        
        # 客户属性字段
        schema.add_field("life_day", "string", comment="客户生命周期天数", aggregatable=True)
        schema.add_field("gender", "string", comment="性别（编码）")
        schema.add_field("open_day", "string", comment="开户天数", aggregatable=True)
        schema.add_field("label", "string", comment="标签值（如是否购买）")
        
        schema.set_monthly_unique(False)  # A表不是每人每月唯一
        return schema
    
    def _create_asset_avg_schema(self) -> TableSchema:
        """创建B表结构 - 资产平均余额表"""
        schema = TableSchema('bi_hlwj_zi_chan_avg_wy')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 总余额字段
        schema.add_field("asset_total_bal", "string", comment="总资产余额", aggregatable=True)
        schema.add_field("liab_total_bal", "string", comment="总负债余额", aggregatable=True)
        schema.add_field("dpsit_total_bal", "string", comment="存款总余额", aggregatable=True)
        schema.add_field("loan_total_bal", "string", comment="贷款总余额", aggregatable=True)
        schema.add_field("card_total_bal", "string", comment="信用卡总余额", aggregatable=True)
        schema.add_field("mid_busi_total_bal", "string", comment="中间业务总余额", aggregatable=True)
        
        # 平均资产余额字段
        for period in ["month", "year", "3", "6", "12"]:
            schema.add_field(
                f"avg_asset_bal_{period}", 
                "string",
                comment=f"平均资产余额 ({period}期)", 
                aggregatable=True
            )
        
        # 平均存款余额字段
        for period in ["3", "12"]:
            schema.add_field(
                f"avg_dpsit_bal_{period}", 
                "string",
                comment=f"平均存款余额 ({period}期)", 
                aggregatable=True
            )
        
        schema.set_monthly_unique(True)  # B表每人每月唯一
        return schema
    
    def _create_asset_config_schema(self) -> TableSchema:
        """创建C表结构 - 月度资产配置表"""
        schema = TableSchema('bi_hlwj_zi_chang_month_total_zb')
        schema.add_primary_key('party_id', 'string')
        schema.add_date_field('data_dt', 'string')
        
        # 资产配置字段
        asset_fields = [
            ("SEG_ASSET_TOTAL", "总资产余额"),
            ("INDV_CONSM_LOAN_AMT", "个人消费贷款余额"),
            ("INDV_HOUSE_LOAN_AMT", "个人住房贷款余额"),
            ("INDV_OPER_LOAN_AMT", "个人经营贷款余额"),
            ("DPSIT_BAL", "存款余额"),
            ("TBOND_BAL", "国债余额"),
            ("FUND_BAL", "基金余额"),
            ("BOND_BAL", "债券余额"),
            ("GOLD_BAL", "黄金余额"),
            ("WCURR_CHREM_BAL", "外币现钞余额"),
            ("PRESV_MGMT_SECU_BAL", "保值管理证券余额"),
            ("INSURE_FORM_BAL", "保险单余额"),
            ("CRDT_CARD_OD_BAL", "信用卡透支余额"),
            ("CRDT_CARD_CON_AMT", "信用卡消费金额"),
            ("SEMI_CRDT_CARD_OD_BAL", "准贷记卡透支余额"),
            ("SEMI_CRDT_CARD_CON_AMT", "准贷记卡消费金额"),
            ("INTER_CARD_CON_AMT", "国际卡消费金额"),
            ("INTER_CARD_OD_BAL", "国际卡透支余额"),
            ("CRDT_CARD_DPSIT_BAL", "信用卡存款余额"),
            ("SEMI_CRDT_CARD_DPSIT_BAL", "准贷记卡存款余额"),
            ("INTER_CARD_DPSIT_BAL", "国际卡存款余额"),
            ("SILVER_BAL", "白银余额"),
            ("AGENT_SOLID_SILVER_BAL", "代发实物白银余额"),
            ("PT_BAL", "个人养老金余额"),
            ("PD_BAL", "个人养老金存款余额"),
            ("OTHER_METAL_BAL", "其他金属余额"),
            ("CURR_DPSIT_BAL", "活期存款余额"),
            ("TIME_DPSIT_BAL", "定期存款余额"),
            ("OIL_BAL", "石油余额"),
            ("FX_BAL", "外汇余额")
        ]
        
        for field_name, description in asset_fields:
            schema.add_field(field_name, "string", comment=description, aggregatable=True)
        
        schema.set_monthly_unique(True)  # C表每人每月唯一
        return schema
    
    def _create_monthly_stat_schema(self) -> TableSchema:
        """创建D表结构 - 月度实际统计表"""
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
            schema.add_field(f"{prefix}_IN", "string", comment=f"{desc}存入金额", aggregatable=True)
            schema.add_field(f"{prefix}_OUT", "string", comment=f"{desc}取出金额", aggregatable=True)
        
        # 其他存取款字段
        schema.add_field("AGENT_SALARY_IN", "string", comment="代发工资存入金额", aggregatable=True)
        schema.add_field("CREDIT_CARD_OUT", "string", comment="信用卡取出金额", aggregatable=True)
        schema.add_field("DEBIT_CARD_OUT", "string", comment="借记卡取出金额", aggregatable=True)
        schema.add_field("BATCH_DEDUCT_OUT", "string", comment="批量扣款金额", aggregatable=True)
        
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
                schema.add_field(field_name, "string", comment=description, aggregatable=True)
        
        # 其他交易字段
        schema.add_field("COUNTER_TX_CNT_MON12", "string", comment="柜台交易次数（近12个月）", aggregatable=True)
        schema.add_field("WEBBANK_TX_CNT_MON12", "string", comment="网银交易次数（近12个月）", aggregatable=True)
        
        # 境外交易字段
        for i in range(1, 6):
            schema.add_field(f"Y1_OVERS_CTY{i}_CNT", "string", comment=f"近一年境外国家{i}的交易次数", aggregatable=True)
            schema.add_field(f"Y1_OVERS_CNT_CTY{i}_CD", "string", comment=f"近一年境外国家{i}的交易次数（编码）")
            schema.add_field(f"Y1_OVERS_CTY{i}_AMT", "string", comment=f"近一年境外国家{i}的交易金额", aggregatable=True)
            schema.add_field(f"Y1_OVERS_AMT_CTY{i}_CD", "string", comment=f"近一年境外国家{i}的交易金额（编码）")
        
        schema.add_field("Y1_OVERS_OTHER_CTY_CNT", "string", comment="近一年其他境外国家的交易次数", aggregatable=True)
        schema.add_field("Y1_OVERS_OTHER_CTY_AMT", "string", comment="近一年其他境外国家的交易金额", aggregatable=True)
        
        schema.set_monthly_unique(True)  # D表每人每月唯一
        return schema
    
    def run(self, feature_date: Optional[str] = None, output_path: str = "file:///nfsHome/aum_longtail") -> Dict:
        """
        运行完整的AUM长尾模型特征工程
        
        Args:
            feature_date: 特征日期，格式为YYYYMM，默认为当前月
            output_path: 输出路径，默认为file:///nfsHome/aum_longtail
            
        Returns:
            包含所有结果的字典
        """
        if feature_date is None:
            feature_date = Date.today().format_compact()[:6]
        
        print(f"🚀 开始AUM长尾模型特征工程 - {feature_date}")
        print("="*60)
        
        results = {}
        
        # 1. A表特征（只生成原始拷贝和聚合特征）
        print("📊 A表：客户行为特征（原始拷贝 + 聚合特征）")
        results['behavior'] = self._generate_behavior_features(feature_date)
        
        # 2. B表特征（生成全部特征：聚合 + 环比5个月 + 同比1年）
        print("💰 B表：资产平均余额特征（聚合 + 环比5个月 + 同比1年）")
        results['asset_avg'] = self._generate_full_features('asset_avg', feature_date)
        
        # 3. C表特征（生成全部特征）
        print("📈 C表：月度资产配置特征（聚合 + 环比5个月 + 同比1年）")
        results['asset_config'] = self._generate_full_features('asset_config', feature_date)
        
        # 4. D表特征（生成全部特征）
        print("📋 D表：月度实际统计特征（聚合 + 环比5个月 + 同比1年）")
        results['monthly_stat'] = self._generate_full_features('monthly_stat', feature_date)
        
        # 5. 导出训练数据
        print("💾 导出训练数据...")
        results['export'] = self._export_datasets(feature_date, output_path)
        
        print("\n" + "="*60)
        print("✅ AUM长尾模型特征工程完成！")
        print(f"📂 输出路径: {output_path}")
        
        return results
    
    def _generate_behavior_features(self, feature_date: str) -> Dict:
        """生成A表特征（仅原始拷贝和聚合特征）"""
        schema = self.schemas['behavior']
        manager = FeatureManager(self.engine, self.database)
        
        # 配置特征生成（只启用原始拷贝和聚合）
        config = FeatureConfig()
        config.enable_feature(FeatureType.RAW_COPY)
        config.enable_feature(FeatureType.AGGREGATION)
        config.disable_feature(FeatureType.MOM)
        config.disable_feature(FeatureType.YOY)
        
        # 使用完整的聚合类型
        config.set_aggregation_types(['sum', 'avg', 'max', 'min', 'count', 'stddev'])
        
        from ..features.generator import FeatureGenerator
        generator = FeatureGenerator(schema, manager, config)
        
        # 生成特征表
        result = generator.create_feature_table(
            feature_type=FeatureType.AGGREGATION,
            year=int(feature_date[:4]),
            month=int(feature_date[4:6]),
            feature_num=1,
            execute=True
        )
        
        print(f"   ✅ 生成表: {result}")
        return {'table_name': result, 'feature_types': ['raw_copy', 'aggregation']}
    
    def _generate_full_features(self, table_type: str, feature_date: str) -> Dict:
        """生成完整特征（聚合 + 环比5个月 + 同比1年）"""
        schema = self.schemas[table_type]
        manager = FeatureManager(self.engine, self.database)
        
        # 配置特征生成（启用所有特征）
        config = FeatureConfig()
        config.enable_feature(FeatureType.RAW_COPY)
        config.enable_feature(FeatureType.AGGREGATION)
        config.enable_feature(FeatureType.MOM)
        config.enable_feature(FeatureType.YOY)
        
        # 设置环比过去5个月
        config.set_mom_periods([1, 2, 3, 4, 5])
        # 设置同比过去1年
        config.set_yoy_periods([1])
        
        from ..features.generator import FeatureGenerator
        generator = FeatureGenerator(schema, manager, config)
        
        # 生成完整特征表
        result = generator.create_feature_table(
            feature_type=FeatureType.AGGREGATION,  # 主要特征类型
            year=int(feature_date[:4]),
            month=int(feature_date[4:6]),
            feature_num=1,
            execute=True
        )
        
        print(f"   ✅ 生成表: {result}")
        return {
            'table_name': result, 
            'feature_types': ['raw_copy', 'aggregation', 'mom_5m', 'yoy_1y']
        }
    
    def _export_datasets(self, feature_date: str, output_path: str) -> Dict:
        """导出训练数据集"""
        results = {}
        
        # 导出各个特征表的数据
        table_mappings = {
            'behavior': 'behavior_features',
            'asset_avg': 'asset_avg_features', 
            'asset_config': 'asset_config_features',
            'monthly_stat': 'monthly_stat_features'
        }
        
        for table_type, file_prefix in table_mappings.items():
            table_name = f"{self.schemas[table_type].table_name}_{feature_date}_f001"
            
            result = self.engine.download_table_data(
                table_name=f"{self.database}.{table_name}",
                output_path=f"{output_path}/{file_prefix}_{feature_date}.parquet",
                mode="cluster"
            )
            
            results[table_type] = result
            print(f"   ✅ 导出 {table_type}: {result.get('status', 'unknown')}")
        
        return results
    
    def get_summary(self) -> Dict:
        """获取示例摘要信息"""
        summary = {
            'database': self.database,
            'tables': {},
            'total_features': 0
        }
        
        for table_type, schema in self.schemas.items():
            try:
                manager = FeatureManager(self.engine, self.database)
                
                if table_type == 'behavior':
                    # A表只有原始拷贝和聚合特征
                    config = FeatureConfig()
                    config.enable_feature(FeatureType.RAW_COPY)
                    config.enable_feature(FeatureType.AGGREGATION)
                    config.disable_feature(FeatureType.MOM)
                    config.disable_feature(FeatureType.YOY)
                else:
                    # B、C、D表包含完整特征：聚合+5个月MoM+1年YoY
                    config = FeatureConfig()
                    config.enable_feature(FeatureType.AGGREGATION, mom_windows=[5], yoy_windows=[12])
                
                feature_count = manager.count_features(schema, config)
                summary['tables'][table_type] = {
                    'table_name': schema.table_name,
                    'field_count': len(schema.fields),
                    'feature_count': feature_count,
                    'features': {
                        'total': feature_count,
                        'aggregation': len(schema.fields),  # 估算
                        'mom': len(schema.fields) * 5 if table_type != 'behavior' else 0,
                        'yoy': len(schema.fields) * 1 if table_type != 'behavior' else 0
                    }
                }
                summary['total_features'] += feature_count
            except Exception as e:
                # 在模拟模式下返回预估数量
                base_fields = len(schema.fields)
                if table_type == 'behavior':
                    estimated_features = base_fields * 2  # 原始拷贝 + 聚合
                    agg_count = base_fields
                    mom_count = 0
                    yoy_count = 0
                else:
                    estimated_features = base_fields * 8  # 聚合 + MoM + YoY 组合
                    agg_count = base_fields
                    mom_count = base_fields * 5
                    yoy_count = base_fields * 1
                
                summary['tables'][table_type] = {
                    'table_name': schema.table_name,
                    'field_count': base_fields,
                    'feature_count': estimated_features,
                    'mode': 'estimated',
                    'features': {
                        'total': estimated_features,
                        'aggregation': agg_count,
                        'mom': mom_count,
                        'yoy': yoy_count
                    }
                }
                summary['total_features'] += estimated_features
        
        return summary
    
    def print_summary(self):
        """打印示例摘要"""
        summary = self.get_summary()
        
        print("🎯 AUM代发长尾模型示例摘要")
        print("="*50)
        print(f"数据库: {summary['database']}")
        print(f"总特征数: {summary['total_features']}")
        print()
        
        for table_type, info in summary['tables'].items():
            features = info['features']
            print(f"📊 {table_type.upper()}表 ({info['table_name']})")
            print(f"   - 字段数: {info['fields_count']}")
            print(f"   - 总特征: {features['total']}")
            print(f"   - 原始拷贝: {features['raw_copy']}")
            print(f"   - 聚合特征: {features['aggregation']}")
            print(f"   - 环比特征: {features['mom']}")
            print(f"   - 同比特征: {features['yoy']}")
            print()


# 简化的使用接口
def create_aum_example(database: str = "dwegdata03000") -> AUMLongtailExample:
    """
    创建AUM长尾模型示例
    
    Args:
        database: 数据库名称
        
    Returns:
        AUMLongtailExample实例
    """
    return AUMLongtailExample(database)


def run_aum_example(feature_date: Optional[str] = None, 
                   database: str = "dwegdata03000",
                   output_path: str = "file:///nfsHome/aum_longtail") -> Dict:
    """
    一键运行AUM长尾模型示例
    
    Args:
        feature_date: 特征日期，格式YYYYMM
        database: 数据库名称
        output_path: 输出路径
        
    Returns:
        执行结果
    """
    example = create_aum_example(database)
    return example.run(feature_date, output_path)
