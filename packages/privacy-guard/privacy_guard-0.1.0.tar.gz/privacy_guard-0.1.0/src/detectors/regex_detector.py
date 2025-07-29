"""基于正则表达式的检测器"""

import re
from typing import List, Dict, Any, Optional
from .base import BaseDetector, DetectionResult


class RegexDetector(BaseDetector):
    """正则表达式检测器"""
    
    # 中国常用敏感数据正则模式
    PATTERNS = {
        'phone': {
            'pattern': r'^1[3-9]\d{9}$',
            'description': '手机号码'
        },
        'id_card': {
            'pattern': r'^\d{15}|\d{17}[\dXx]$',
            'description': '身份证号码'
        },
        'email': {
            'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'description': '电子邮箱'
        },
        'bank_card': {
            'pattern': r'^\d{16,19}$',
            'description': '银行卡号'
        },
        'credit_card': {
            'pattern': r'^[4-6]\d{15}$',
            'description': '信用卡号'
        },
        'ip_address': {
            'pattern': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
            'description': 'IP地址'
        },
        'mac_address': {
            'pattern': r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
            'description': 'MAC地址'
        }
    }
    
    def __init__(self):
        super().__init__("RegexDetector", priority=1)
        self.compiled_patterns = {
            name: re.compile(pattern_info['pattern'])
            for name, pattern_info in self.PATTERNS.items()
        }
    
    def detect(self, field_name: str, values: List[Any]) -> Optional[DetectionResult]:
        """检测敏感数据"""
        if not values:
            return None
        
        sample_values = self._sample_values(values)
        if not sample_values:
            return None
        
        # 检测每种模式
        for data_type, compiled_pattern in self.compiled_patterns.items():
            matches = 0
            total_checked = 0
            
            for value in sample_values:
                total_checked += 1
                if compiled_pattern.match(str(value).strip()):
                    matches += 1
            
            if total_checked > 0:
                confidence = matches / total_checked
                
                # 如果匹配率超过80%，认为是该类型的敏感数据
                if confidence >= 0.8:
                    return DetectionResult(
                        field_name=field_name,
                        data_type=data_type,
                        confidence=confidence,
                        pattern=self.PATTERNS[data_type]['pattern'],
                        sample_values=sample_values[:3]
                    )
        
        return None