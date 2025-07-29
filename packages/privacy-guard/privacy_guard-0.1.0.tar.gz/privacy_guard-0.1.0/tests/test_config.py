"""测试配置和规则引擎"""

import pytest
import tempfile
import json
from pathlib import Path
from src.config import ConfigLoader, RuleEngine, MaskingRules, FieldRule, GlobalConfig


class TestConfigLoader:
    """测试配置加载器"""
    
    def test_create_default_config(self):
        config = ConfigLoader.create_default_config()
        
        assert isinstance(config, MaskingRules)
        assert config.version == "1.0"
        assert len(config.field_rules) > 0
        assert config.global_config.auto_detect is True
    
    def test_save_and_load_json(self):
        config = ConfigLoader.create_default_config()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # 保存配置
            ConfigLoader.save_to_file(config, temp_path)
            
            # 加载配置
            loaded_config = ConfigLoader.load_from_file(temp_path)
            
            assert loaded_config.version == config.version
            assert len(loaded_config.field_rules) == len(config.field_rules)
        finally:
            Path(temp_path).unlink()
    
    def test_load_from_dict(self):
        config_dict = {
            "version": "1.0",
            "global_config": {
                "auto_detect": True,
                "default_strategy": "MaskStrategy"
            },
            "field_rules": [
                {
                    "field_name": "phone",
                    "data_type": "phone",
                    "strategy": "MaskStrategy",
                    "params": {},
                    "enabled": True
                }
            ]
        }
        
        config = ConfigLoader.load_from_dict(config_dict)
        assert isinstance(config, MaskingRules)
        assert len(config.field_rules) == 1
        assert config.field_rules[0].field_name == "phone"


class TestMaskingRules:
    """测试脱敏规则模型"""
    
    def test_get_rule_for_field(self):
        config = ConfigLoader.create_default_config()
        
        phone_rule = config.get_rule_for_field("phone")
        assert phone_rule is not None
        assert phone_rule.field_name == "phone"
        
        non_existent_rule = config.get_rule_for_field("non_existent")
        assert non_existent_rule is None
    
    def test_add_rule(self):
        config = MaskingRules()
        
        new_rule = FieldRule(
            field_name="test_field",
            strategy="MaskStrategy",
            params={"test": "value"}
        )
        
        config.add_rule(new_rule)
        
        assert len(config.field_rules) == 1
        assert config.get_rule_for_field("test_field") == new_rule
    
    def test_remove_rule(self):
        config = ConfigLoader.create_default_config()
        initial_count = len(config.field_rules)
        
        config.remove_rule("phone")
        
        assert len(config.field_rules) == initial_count - 1
        assert config.get_rule_for_field("phone") is None


class TestRuleEngine:
    """测试规则引擎"""
    
    def test_process_field_with_rule(self):
        config = ConfigLoader.create_default_config()
        engine = RuleEngine(config)
        
        phone_values = ["13812345678", "15987654321"]
        masked_values = engine.process_field("phone", phone_values)
        
        assert len(masked_values) == len(phone_values)
        for original, masked in zip(phone_values, masked_values):
            assert original != masked
    
    def test_process_field_auto_detect(self):
        config = MaskingRules(
            global_config=GlobalConfig(auto_detect=True),
            field_rules=[]
        )
        engine = RuleEngine(config)
        
        phone_values = ["13812345678", "15987654321"]
        masked_values = engine.process_field("mobile_number", phone_values)
        
        # 应该自动检测到手机号并进行脱敏
        assert len(masked_values) == len(phone_values)
    
    def test_analyze_dataset(self):
        config = ConfigLoader.create_default_config()
        engine = RuleEngine(config)
        
        data = {
            "name": ["张三", "李四"],
            "phone": ["13812345678", "15987654321"],
            "age": [25, 30]
        }
        
        analysis = engine.analyze_dataset(data)
        
        assert analysis["total_fields"] == 3
        assert analysis["sensitive_fields"] >= 1  # 至少检测到phone
        assert "field_analysis" in analysis
        assert "recommendations" in analysis
    
    def test_validate_rules(self):
        # 创建包含无效策略的配置
        invalid_rule = FieldRule(
            field_name="test",
            strategy="NonExistentStrategy",
            params={}
        )
        
        config = MaskingRules(field_rules=[invalid_rule])
        engine = RuleEngine(config)
        
        errors = engine.validate_rules()
        assert len(errors) > 0
        assert "NonExistentStrategy" in errors[0]