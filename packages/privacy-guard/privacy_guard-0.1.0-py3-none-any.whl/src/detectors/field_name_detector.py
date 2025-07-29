"""字段名称检测器"""

from typing import List, Dict, Any, Optional
from .base import BaseDetector, DetectionResult


class FieldNameDetector(BaseDetector):
    """基于字段名称的检测器"""
    
    # 常见敏感字段名称关键词
    FIELD_KEYWORDS = {
        'name': ['name', 'username', 'user_name', '姓名', '用户名', '真实姓名'],
        'phone': ['phone', 'mobile', 'tel', 'telephone', '电话', '手机', '联系方式'],
        'email': ['email', 'mail', '邮箱', '电子邮件'],
        'id_card': ['id_card', 'identity', 'idcard', '身份证', '证件号'],
        'address': ['address', 'addr', '地址', '住址', '联系地址'],
        'bank_card': ['bank_card', 'card_no', 'account', '银行卡', '卡号', '账号'],
        'password': ['password', 'pwd', 'pass', '密码'],
        'salary': ['salary', 'income', 'wage', '工资', '薪资', '收入'],
        'age': ['age', '年龄'],
        'birthday': ['birthday', 'birth', 'dob', '生日', '出生日期'],
    }
    
    def __init__(self):
        super().__init__("FieldNameDetector", priority=2)
    
    def detect(self, field_name: str, values: List[Any]) -> Optional[DetectionResult]:
        """基于字段名称检测敏感数据"""
        if not field_name:
            return None
        
        field_lower = field_name.lower()
        
        for data_type, keywords in self.FIELD_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in field_lower:
                    sample_values = self._sample_values(values)
                    
                    return DetectionResult(
                        field_name=field_name,
                        data_type=data_type,
                        confidence=0.7,  # 基于字段名的置信度相对较低
                        sample_values=sample_values[:3]
                    )
        
        return None