"""CLI工具入口"""

import click
import json
import yaml
from pathlib import Path
from typing import Optional
from ..core import PrivacyGuard
from ..config import ConfigLoader


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Privacy Guard - 隐私保护数据脱敏工具"""
    pass


@main.command()
@click.option('--input', '-i', required=True, help='输入CSV文件路径')
@click.option('--output', '-o', required=True, help='输出CSV文件路径')
@click.option('--config', '-c', help='配置文件路径（可选）')
@click.option('--encoding', default='utf-8', help='文件编码，默认utf-8')
@click.option('--verbose', '-v', is_flag=True, help='显示详细信息')
def mask(input: str, output: str, config: Optional[str], encoding: str, verbose: bool):
    """脱敏CSV文件"""
    try:
        # 创建PrivacyGuard实例
        pg = PrivacyGuard(config)
        
        if verbose:
            click.echo(f"开始处理文件: {input}")
        
        # 执行脱敏
        result = pg.mask_csv(input, output, encoding)
        
        if verbose:
            click.echo(f"处理完成!")
            click.echo(f"输入文件: {result['input_file']}")
            click.echo(f"输出文件: {result['output_file']}")
            click.echo(f"总行数: {result['total_rows']}")
            click.echo(f"总列数: {result['total_columns']}")
            click.echo(f"处理字段: {', '.join(result['processed_fields'])}")
        else:
            click.echo(f"脱敏完成: {output}")
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option('--input', '-i', required=True, help='输入CSV文件路径')
@click.option('--config', '-c', help='配置文件路径（可选）')
@click.option('--encoding', default='utf-8', help='文件编码，默认utf-8')
@click.option('--output', '-o', help='保存分析结果到JSON文件')
def analyze(input: str, config: Optional[str], encoding: str, output: Optional[str]):
    """分析CSV文件中的敏感数据"""
    try:
        # 创建PrivacyGuard实例
        pg = PrivacyGuard(config)
        
        click.echo(f"分析文件: {input}")
        
        # 执行分析
        analysis = pg.analyze_csv(input, encoding)
        
        # 显示结果
        click.echo(f"\n=== 分析结果 ===")
        click.echo(f"总字段数: {analysis['total_fields']}")
        click.echo(f"敏感字段数: {analysis['sensitive_fields']}")
        
        if analysis['field_analysis']:
            click.echo(f"\n=== 敏感字段详情 ===")
            for field_name, info in analysis['field_analysis'].items():
                click.echo(f"字段: {field_name}")
                click.echo(f"  类型: {info['data_type']}")
                click.echo(f"  置信度: {info['confidence']:.2f}")
                click.echo(f"  已配置规则: {'是' if info['has_rule'] else '否'}")
                click.echo(f"  推荐策略: {info['recommended_strategy']}")
                if info['sample_values']:
                    click.echo(f"  样本值: {', '.join(info['sample_values'][:3])}")
                click.echo()
        
        if analysis['recommendations']:
            click.echo(f"=== 建议 ===")
            for rec in analysis['recommendations']:
                click.echo(f"- {rec}")
        
        # 保存到文件
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            click.echo(f"\n分析结果已保存到: {output}")
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option('--output', '-o', required=True, help='配置文件输出路径')
@click.option('--format', 'fmt', type=click.Choice(['yaml', 'json']), default='yaml', help='配置文件格式')
def init_config(output: str, fmt: str):
    """生成默认配置文件"""
    try:
        # 创建默认配置
        config = ConfigLoader.create_default_config()
        
        # 根据文件扩展名确定格式
        output_path = Path(output)
        if fmt == 'yaml' or output_path.suffix.lower() in ['.yml', '.yaml']:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config.model_dump(), f, default_flow_style=False, allow_unicode=True)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config.model_dump(), f, ensure_ascii=False, indent=2)
        
        click.echo(f"默认配置文件已生成: {output}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option('--config', '-c', required=True, help='配置文件路径')
def validate_config(config: str):
    """验证配置文件"""
    try:
        # 加载配置
        pg = PrivacyGuard(config)
        
        # 验证配置
        errors = pg.validate_config()
        
        if errors:
            click.echo("配置文件有以下错误:")
            for error in errors:
                click.echo(f"- {error}")
            raise click.Abort()
        else:
            click.echo("配置文件验证通过!")
            
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    main()