"""
Schema文档生成器

支持根据表结构定义生成多种格式的技术文档：
- Markdown格式：适合开发团队和版本控制
- PDF格式：适合正式交付和业务方审阅
- HTML格式：适合在线查看和分享

主要功能：
1. 表结构自动解析
2. 字段信息格式化
3. 业务含义说明
4. 技术规范文档
5. 多格式导出支持
"""

import os
from typing import Dict, List, Optional
from datetime import datetime


class SchemaDocumentGenerator:
    """表结构文档生成器"""
    
    def __init__(self):
        self.template_configs = {
            'markdown': {
                'extension': '.md',
                'header_template': self._get_markdown_header_template(),
                'field_template': self._get_markdown_field_template(),
                'footer_template': self._get_markdown_footer_template()
            },
            'pdf': {
                'extension': '.pdf', 
                'requires_conversion': True,
                'base_format': 'markdown'  # 先生成MD再转PDF
            },
            'html': {
                'extension': '.html',
                'header_template': self._get_html_header_template(),
                'field_template': self._get_html_field_template(),
                'footer_template': self._get_html_footer_template()
            }
        }
    
    def export_schema_doc(self, schema, business_domain: str, table_type: str, 
                         output_dir: str = "./docs", format_type: str = "markdown") -> str:
        """
        导出表结构文档
        
        Args:
            schema: TableSchema对象
            business_domain: 业务域名称 (如: AUM, CRM, RISK)
            table_type: 表类型 (如: behavior, asset_avg)
            output_dir: 输出目录
            format_type: 文档格式 ('markdown', 'pdf', 'html')
            
        Returns:
            生成的文档文件路径
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{business_domain}_{table_type}_schema_{timestamp}"
        
        if format_type.lower() == 'pdf':
            # PDF格式先生成Markdown再转换
            md_content = self._generate_markdown_content(schema, business_domain, table_type)
            md_path = os.path.join(output_dir, f"{filename}.md")
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            # 转换为PDF (这里可以集成pandoc或其他转换工具)
            pdf_path = os.path.join(output_dir, f"{filename}.pdf")
            self._convert_md_to_pdf(md_path, pdf_path)
            return pdf_path
            
        elif format_type.lower() == 'html':
            # HTML格式
            html_content = self._generate_html_content(schema, business_domain, table_type)
            html_path = os.path.join(output_dir, f"{filename}.html")
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return html_path
            
        else:
            # 默认Markdown格式
            md_content = self._generate_markdown_content(schema, business_domain, table_type)
            md_path = os.path.join(output_dir, f"{filename}.md")
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            return md_path
    
    def _generate_markdown_content(self, schema, business_domain: str, table_type: str) -> str:
        """生成Markdown格式内容"""
        content = []
        
        # 文档头部
        content.append(f"# {business_domain} - {table_type.upper()}表结构文档")
        content.append("")
        content.append(f"## 基本信息")
        content.append("")
        content.append(f"- **表名**: `{schema.table_name}`")
        content.append(f"- **业务域**: {business_domain}")
        content.append(f"- **表类型**: {table_type}")
        content.append(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"- **月度唯一性**: {'是' if getattr(schema, 'is_monthly_unique', False) else '否'}")
        content.append("")
        
        # 表结构说明
        content.append("## 表结构说明")
        content.append("")
        if hasattr(schema, 'description'):
            content.append(f"{schema.description}")
            content.append("")
        
        # 主键信息
        if hasattr(schema, 'primary_key') and schema.primary_key:
            content.append("### 主键字段")
            content.append("")
            content.append(f"- `{schema.primary_key}` (主键)")
            content.append("")
        
        # 日期字段
        if hasattr(schema, 'date_field') and schema.date_field:
            content.append("### 日期字段")
            content.append("")
            content.append(f"- `{schema.date_field}` (日期字段)")
            content.append("")
        
        # 字段详情表格
        content.append("## 字段详情")
        content.append("")
        content.append("| 字段名 | 数据类型 | 业务含义 | 可聚合 | 备注 |")
        content.append("|--------|----------|----------|--------|------|")
        
        if hasattr(schema, 'fields'):
            for field_name, field in schema.fields.items():
                # 简化数据类型显示
                field_type_str = str(field.field_type) if hasattr(field, 'field_type') else 'string'
                field_type = field_type_str.replace('FieldType.', '').lower()
                comment = field.comment if hasattr(field, 'comment') else ''
                aggregatable = '是' if getattr(field, 'aggregatable', False) else '否'
                remarks = ''  # 可以从其他地方获取备注
                
                content.append(f"| `{field_name}` | {field_type} | {comment} | {aggregatable} | {remarks} |")
        
        content.append("")
        
        # 业务规则说明
        content.append("## 业务规则")
        content.append("")
        content.append("### 数据更新规则")
        if getattr(schema, 'is_monthly_unique', False):
            content.append("- 每人每月一条记录")
            content.append("- 月末批量更新")
        else:
            content.append("- 每人每日一条记录")
            content.append("- 日终批量更新")
        content.append("")
        
        content.append("### 数据质量要求")
        content.append("- 主键字段不允许为空")
        content.append("- 日期字段格式统一为YYYYMMDD")
        content.append("- 金额字段精度保持2位小数")
        content.append("- 比例字段取值范围[0,1]")
        content.append("")
        
        # 使用说明
        content.append("## 使用说明")
        content.append("")
        content.append("### 特征工程配置")
        if table_type == 'behavior':
            content.append("- 生成原始拷贝特征")
            content.append("- 生成聚合特征")
            content.append("- 不生成环比、同比特征")
        else:
            content.append("- 生成聚合特征")
            content.append("- 生成5个月环比特征")
            content.append("- 生成1年同比特征")
        content.append("")
        
        content.append("### 示例SQL查询")
        content.append("```sql")
        content.append(f"-- 查询最新数据")
        content.append(f"SELECT * FROM {schema.table_name}")
        content.append(f"WHERE data_dt = (SELECT MAX(data_dt) FROM {schema.table_name})")
        content.append(f"LIMIT 10;")
        content.append("```")
        content.append("")
        
        # 文档尾部
        content.append("---")
        content.append("*本文档由Staran Schema自动生成*")
        
        return "\n".join(content)
    
    def _generate_html_content(self, schema, business_domain: str, table_type: str) -> str:
        """生成HTML格式内容"""
        # 基础HTML模板，可以根据需要扩展
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{business_domain} - {table_type.upper()}表结构文档</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        .info-table {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>{business_domain} - {table_type.upper()}表结构文档</h1>
    
    <h2>基本信息</h2>
    <table class="info-table">
        <tr><th>表名</th><td><code>{schema.table_name}</code></td></tr>
        <tr><th>业务域</th><td>{business_domain}</td></tr>
        <tr><th>表类型</th><td>{table_type}</td></tr>
        <tr><th>生成时间</th><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
        <tr><th>月度唯一性</th><td>{'是' if getattr(schema, 'is_monthly_unique', False) else '否'}</td></tr>
    </table>
    
    <h2>字段详情</h2>
    <table>
        <thead>
            <tr>
                <th>字段名</th>
                <th>数据类型</th>
                <th>业务含义</th>
                <th>可聚合</th>
                <th>备注</th>
            </tr>
        </thead>
        <tbody>
"""
        
        # 添加字段行
        if hasattr(schema, 'fields'):
            for field_name, field in schema.fields.items():
                # 简化数据类型显示
                field_type_str = str(field.field_type) if hasattr(field, 'field_type') else 'string'
                field_type = field_type_str.replace('FieldType.', '').lower()
                comment = field.comment if hasattr(field, 'comment') else ''
                aggregatable = '是' if getattr(field, 'aggregatable', False) else '否'
                remarks = ''  # 可以从其他地方获取备注
                
                html_content += f"""
            <tr>
                <td><code>{field_name}</code></td>
                <td>{field_type}</td>
                <td>{comment}</td>
                <td>{aggregatable}</td>
                <td>{remarks}</td>
            </tr>"""
        
        html_content += """
        </tbody>
    </table>
    
    <hr>
    <p><em>本文档由Staran Schema自动生成</em></p>
</body>
</html>"""
        
        return html_content
    
    def _convert_md_to_pdf(self, md_path: str, pdf_path: str):
        """将Markdown转换为PDF (需要安装pandoc或其他转换工具)"""
        try:
            import subprocess
            # 尝试使用pandoc转换
            subprocess.run([
                'pandoc', md_path, '-o', pdf_path,
                '--pdf-engine=xelatex',
                '--variable=CJKmainfont:Microsoft YaHei'
            ], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 如果pandoc不可用，创建一个说明文件
            with open(pdf_path.replace('.pdf', '_conversion_note.txt'), 'w', encoding='utf-8') as f:
                f.write(f"PDF转换说明：\\n")
                f.write(f"原始Markdown文件：{md_path}\\n")
                f.write(f"如需PDF格式，请安装pandoc工具：\\n")
                f.write(f"pip install pandoc\\n")
                f.write(f"或访问：https://pandoc.org/installing.html\\n")
    
    def _get_markdown_header_template(self) -> str:
        return "# {title}\\n\\n## 基本信息\\n\\n"
    
    def _get_markdown_field_template(self) -> str:
        return "| {name} | {type} | {comment} | {aggregatable} |\\n"
    
    def _get_markdown_footer_template(self) -> str:
        return "\\n---\\n*文档生成时间: {timestamp}*\\n"
    
    def _get_html_header_template(self) -> str:
        return "<h1>{title}</h1>\\n<h2>基本信息</h2>\\n"
    
    def _get_html_field_template(self) -> str:
        return "<tr><td>{name}</td><td>{type}</td><td>{comment}</td><td>{aggregatable}</td></tr>\\n"
    
    def _get_html_footer_template(self) -> str:
        return "<hr><p><em>文档生成时间: {timestamp}</em></p>\\n"


def export_business_docs(business_domain: str, schemas_dict: Dict, output_dir: str = "./docs", 
                        format_type: str = "markdown") -> Dict[str, str]:
    """
    批量导出业务域表结构文档
    
    Args:
        business_domain: 业务域名称
        schemas_dict: 表结构字典 {table_type: schema}
        output_dir: 输出目录
        format_type: 文档格式
        
    Returns:
        生成的文档文件路径字典
    """
    generator = SchemaDocumentGenerator()
    results = {}
    
    for table_type, schema in schemas_dict.items():
        file_path = generator.export_schema_doc(
            schema=schema,
            business_domain=business_domain,
            table_type=table_type,
            output_dir=output_dir,
            format_type=format_type
        )
        results[table_type] = file_path
    
    return results


__all__ = [
    'SchemaDocumentGenerator',
    'export_business_docs'
]
