"""敏感数据检测器基础类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DetectionResult:
    """检测结果"""
    field_name: str
    data_type: str
    confidence: float
    pattern: Optional[str] = None
    sample_values: Optional[List[str]] = None


class BaseDetector(ABC):
    """检测器基础类"""
    
    def __init__(self, name: str, priority: int = 0):
        self.name = name
        self.priority = priority
    
    @abstractmethod
    def detect(self, field_name: str, values: List[Any]) -> Optional[DetectionResult]:
        """检测敏感数据"""
        pass
    
    def _sample_values(self, values: List[Any], max_samples: int = 5) -> List[str]:
        """获取样本值"""
        non_null_values = [str(v) for v in values if v is not None and str(v).strip()]
        return non_null_values[:max_samples]