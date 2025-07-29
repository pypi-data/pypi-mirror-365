"""策略管理器"""

from typing import Dict, Any, List, Optional
from .base import BaseStrategy, MaskingConfig
from .mask_strategy import MaskStrategy
from .hash_strategy import HashStrategy
from .randomize_strategy import RandomizeStrategy
from .encrypt_strategy import EncryptStrategy


class StrategyManager:
    """脱敏策略管理器"""
    
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """注册默认策略"""
        self.add_strategy(MaskStrategy())
        self.add_strategy(HashStrategy())
        self.add_strategy(RandomizeStrategy())
        self.add_strategy(EncryptStrategy())
    
    def add_strategy(self, strategy: BaseStrategy):
        """添加策略"""
        self.strategies[strategy.name] = strategy
    
    def get_strategy(self, name: str) -> Optional[BaseStrategy]:
        """获取策略"""
        return self.strategies.get(name)
    
    def apply_strategy(self, strategy_name: str, value: Any, config: Optional[MaskingConfig] = None) -> Any:
        """应用策略"""
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"未找到策略: {strategy_name}")
        
        return strategy.mask(value, config)
    
    def apply_strategy_batch(self, strategy_name: str, values: List[Any], config: Optional[MaskingConfig] = None) -> List[Any]:
        """批量应用策略"""
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"未找到策略: {strategy_name}")
        
        return strategy.mask_batch(values, config)
    
    def list_strategies(self) -> List[str]:
        """列出所有策略"""
        return list(self.strategies.keys())
    
    def get_default_strategy_for_type(self, data_type: str) -> str:
        """获取数据类型的默认策略"""
        defaults = {
            'phone': 'MaskStrategy',
            'email': 'MaskStrategy', 
            'id_card': 'HashStrategy',
            'name': 'RandomizeStrategy',
            'address': 'RandomizeStrategy',
            'bank_card': 'HashStrategy',
            'password': 'HashStrategy',
            'ip_address': 'HashStrategy',
            'mac_address': 'HashStrategy',
        }
        return defaults.get(data_type, 'MaskStrategy')