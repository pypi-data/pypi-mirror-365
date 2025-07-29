"""检测器管理器"""

from typing import List, Dict, Any, Optional
from .base import BaseDetector, DetectionResult
from .regex_detector import RegexDetector
from .field_name_detector import FieldNameDetector


class DetectorManager:
    """检测器管理器"""
    
    def __init__(self):
        self.detectors: List[BaseDetector] = []
        self._register_default_detectors()
    
    def _register_default_detectors(self):
        """注册默认检测器"""
        self.add_detector(RegexDetector())
        self.add_detector(FieldNameDetector())
    
    def add_detector(self, detector: BaseDetector):
        """添加检测器"""
        self.detectors.append(detector)
        # 按优先级排序
        self.detectors.sort(key=lambda x: x.priority)
    
    def detect_field(self, field_name: str, values: List[Any]) -> Optional[DetectionResult]:
        """检测单个字段"""
        best_result = None
        highest_confidence = 0.0
        
        for detector in self.detectors:
            result = detector.detect(field_name, values)
            if result and result.confidence > highest_confidence:
                best_result = result
                highest_confidence = result.confidence
        
        return best_result
    
    def detect_dataset(self, data: Dict[str, List[Any]]) -> Dict[str, DetectionResult]:
        """检测整个数据集"""
        results = {}
        
        for field_name, values in data.items():
            result = self.detect_field(field_name, values)
            if result:
                results[field_name] = result
        
        return results
    
    def get_sensitive_fields(self, data: Dict[str, List[Any]]) -> List[str]:
        """获取敏感字段列表"""
        detection_results = self.detect_dataset(data)
        return list(detection_results.keys())