"""脱敏策略基础类"""

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional
from dataclasses import dataclass


@dataclass
class MaskingConfig:
    """脱敏配置"""
    strategy_type: str
    params: Dict[str, Any]


class BaseStrategy(ABC):
    """脱敏策略基础类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def mask(self, value: Any, config: Optional[MaskingConfig] = None) -> Any:
        """脱敏单个值"""
        pass
    
    def mask_batch(self, values: List[Any], config: Optional[MaskingConfig] = None) -> List[Any]:
        """批量脱敏"""
        return [self.mask(value, config) for value in values]
    
    def _ensure_string(self, value: Any) -> str:
        """确保值为字符串"""
        return str(value) if value is not None else ""