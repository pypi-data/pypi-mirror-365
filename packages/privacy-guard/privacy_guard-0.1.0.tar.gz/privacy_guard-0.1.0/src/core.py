"""Privacy Guard 核心类"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from .config import ConfigLoader, RuleEngine, MaskingRules
from .detectors import DetectorManager
from .strategies import StrategyManager


class PrivacyGuard:
    """Privacy Guard 主类"""
    
    def __init__(self, config: Optional[Union[str, Path, MaskingRules]] = None):
        """
        初始化 Privacy Guard
        
        Args:
            config: 配置文件路径、配置对象或None（使用默认配置）
        """
        if config is None:
            self.rules = ConfigLoader.create_default_config()
        elif isinstance(config, (str, Path)):
            self.rules = ConfigLoader.load_from_file(config)
        elif isinstance(config, MaskingRules):
            self.rules = config
        else:
            raise ValueError("config 参数必须是文件路径、MaskingRules对象或None")
        
        self.engine = RuleEngine(self.rules)
    
    def mask_csv(self, input_file: Union[str, Path], output_file: Union[str, Path], 
                 encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        脱敏CSV文件
        
        Args:
            input_file: 输入CSV文件路径
            output_file: 输出CSV文件路径
            encoding: 文件编码
            
        Returns:
            处理结果统计
        """
        # 读取CSV
        df = pd.read_csv(input_file, encoding=encoding)
        
        # 转换为字典格式
        data = {col: df[col].tolist() for col in df.columns}
        
        # 脱敏处理
        masked_data = self.engine.process_dataset(data)
        
        # 转换回DataFrame
        masked_df = pd.DataFrame(masked_data)
        
        # 保存结果
        masked_df.to_csv(output_file, index=False, encoding=encoding)
        
        return {
            "input_file": str(input_file),
            "output_file": str(output_file),
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "processed_fields": list(masked_data.keys())
        }
    
    def mask_dict(self, data: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        """
        脱敏字典数据
        
        Args:
            data: 字典格式的数据
            
        Returns:
            脱敏后的数据
        """
        return self.engine.process_dataset(data)
    
    def analyze_csv(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        分析CSV文件的敏感数据
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码
            
        Returns:
            分析结果
        """
        df = pd.read_csv(file_path, encoding=encoding)
        data = {col: df[col].tolist() for col in df.columns}
        
        return self.engine.analyze_dataset(data)
    
    def analyze_dict(self, data: Dict[str, List[Any]]) -> Dict[str, Any]:
        """
        分析字典数据的敏感数据
        
        Args:
            data: 字典格式的数据
            
        Returns:
            分析结果
        """
        return self.engine.analyze_dataset(data)
    
    def export_config(self, file_path: Union[str, Path]):
        """
        导出当前配置到文件
        
        Args:
            file_path: 配置文件保存路径
        """
        ConfigLoader.save_to_file(self.rules, file_path)
    
    def update_config(self, config: Union[str, Path, MaskingRules]):
        """
        更新配置
        
        Args:
            config: 新的配置
        """
        if isinstance(config, (str, Path)):
            self.rules = ConfigLoader.load_from_file(config)
        elif isinstance(config, MaskingRules):
            self.rules = config
        else:
            raise ValueError("config 参数必须是文件路径或MaskingRules对象")
        
        self.engine.update_rules(self.rules)
    
    def validate_config(self) -> List[str]:
        """
        验证当前配置
        
        Returns:
            错误列表，空列表表示配置有效
        """
        return self.engine.validate_rules()