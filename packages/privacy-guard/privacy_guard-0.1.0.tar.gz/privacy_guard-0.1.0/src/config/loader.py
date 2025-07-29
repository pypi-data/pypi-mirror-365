"""配置加载器"""

import yaml
import json
from pathlib import Path
from typing import Union, Dict, Any
from .models import MaskingRules, FieldRule, GlobalConfig


class ConfigLoader:
    """配置文件加载器"""
    
    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> MaskingRules:
        """从文件加载配置"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yml', '.yaml']:
                data = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {path.suffix}")
        
        return MaskingRules(**data)
    
    @staticmethod
    def load_from_dict(config_dict: Dict[str, Any]) -> MaskingRules:
        """从字典加载配置"""
        return MaskingRules(**config_dict)
    
    @staticmethod
    def save_to_file(rules: MaskingRules, file_path: Union[str, Path]):
        """保存配置到文件"""
        path = Path(file_path)
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(rules.model_dump(), f, default_flow_style=False, allow_unicode=True)
            elif path.suffix.lower() == '.json':
                json.dump(rules.model_dump(), f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"不支持的配置文件格式: {path.suffix}")
    
    @staticmethod
    def create_default_config() -> MaskingRules:
        """创建默认配置"""
        return MaskingRules(
            global_config=GlobalConfig(),
            field_rules=[
                FieldRule(
                    field_name="phone",
                    data_type="phone",
                    strategy="MaskStrategy",
                    params={"keep_start": 3, "keep_end": 4}
                ),
                FieldRule(
                    field_name="email",
                    data_type="email", 
                    strategy="MaskStrategy",
                    params={}
                ),
                FieldRule(
                    field_name="id_card",
                    data_type="id_card",
                    strategy="HashStrategy",
                    params={"algorithm": "sha256", "truncate_length": 16}
                ),
                FieldRule(
                    field_name="name",
                    data_type="name",
                    strategy="RandomizeStrategy",
                    params={"data_type": "name"}
                )
            ]
        )