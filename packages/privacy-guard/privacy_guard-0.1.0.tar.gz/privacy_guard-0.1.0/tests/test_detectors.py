"""测试敏感数据检测器"""

import pytest
from src.detectors import RegexDetector, FieldNameDetector, DetectorManager


class TestRegexDetector:
    """测试正则表达式检测器"""
    
    def test_phone_detection(self):
        detector = RegexDetector()
        phones = ["13812345678", "15987654321", "18666888999"]
        result = detector.detect("mobile", phones)
        
        assert result is not None
        assert result.data_type == "phone"
        assert result.confidence >= 0.8
    
    def test_email_detection(self):
        detector = RegexDetector()
        emails = ["test@example.com", "user@gmail.com", "admin@company.org"]
        result = detector.detect("email", emails)
        
        assert result is not None
        assert result.data_type == "email"
        assert result.confidence >= 0.8
    
    def test_id_card_detection(self):
        detector = RegexDetector()
        ids = ["110101199001011234", "330103198512150987"]
        result = detector.detect("id_number", ids)
        
        assert result is not None
        assert result.data_type == "id_card"
        assert result.confidence >= 0.8
    
    def test_non_sensitive_data(self):
        detector = RegexDetector()
        data = ["apple", "banana", "orange"]
        result = detector.detect("fruit", data)
        
        assert result is None


class TestFieldNameDetector:
    """测试字段名称检测器"""
    
    def test_phone_field_detection(self):
        detector = FieldNameDetector()
        result = detector.detect("phone", ["some_value"])
        
        assert result is not None
        assert result.data_type == "phone"
    
    def test_email_field_detection(self):
        detector = FieldNameDetector()
        result = detector.detect("user_email", ["some_value"])
        
        assert result is not None
        assert result.data_type == "email"
    
    def test_chinese_field_detection(self):
        detector = FieldNameDetector()
        result = detector.detect("姓名", ["some_value"])
        
        assert result is not None
        assert result.data_type == "name"


class TestDetectorManager:
    """测试检测器管理器"""
    
    def test_detect_mixed_data(self):
        manager = DetectorManager()
        data = {
            "name": ["张三", "李四", "王五"],
            "phone": ["13812345678", "15987654321", "18666888999"],
            "email": ["test@example.com", "user@gmail.com", "admin@company.org"],
            "age": [25, 30, 35]
        }
        
        results = manager.detect_dataset(data)
        
        assert "phone" in results
        assert "email" in results
        assert results["phone"].data_type == "phone"
        assert results["email"].data_type == "email"
    
    def test_get_sensitive_fields(self):
        manager = DetectorManager()
        data = {
            "name": ["张三", "李四"],
            "phone": ["13812345678", "15987654321"],
            "product": ["苹果", "橙子"]
        }
        
        sensitive_fields = manager.get_sensitive_fields(data)
        
        assert "name" in sensitive_fields
        assert "phone" in sensitive_fields
        assert "product" not in sensitive_fields