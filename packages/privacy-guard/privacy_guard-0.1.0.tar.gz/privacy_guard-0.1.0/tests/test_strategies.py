"""测试脱敏策略"""

import pytest
from src.strategies import MaskStrategy, HashStrategy, RandomizeStrategy, StrategyManager
from src.strategies.base import MaskingConfig


class TestMaskStrategy:
    """测试掩码策略"""
    
    def test_phone_masking(self):
        strategy = MaskStrategy()
        phone = "13812345678"
        masked = strategy.mask(phone)
        
        assert masked.startswith("138")
        assert masked.endswith("5678")
        assert "*" in masked
    
    def test_email_masking(self):
        strategy = MaskStrategy()
        email = "test@example.com"
        masked = strategy.mask(email)
        
        assert "@example.com" in masked
        assert masked.startswith("t")
        assert "*" in masked
    
    def test_custom_mask_config(self):
        strategy = MaskStrategy()
        config = MaskingConfig(
            strategy_type="MaskStrategy",
            params={"mask_char": "#", "keep_start": 2, "keep_end": 2}
        )
        
        text = "12345678"
        masked = strategy.mask(text, config)
        
        assert masked == "12####78"


class TestHashStrategy:
    """测试哈希策略"""
    
    def test_sha256_hashing(self):
        strategy = HashStrategy()
        text = "sensitive_data"
        hashed = strategy.mask(text)
        
        assert len(hashed) == 64  # SHA256输出长度
        assert hashed != text
    
    def test_different_inputs_different_hashes(self):
        strategy = HashStrategy()
        hash1 = strategy.mask("data1")
        hash2 = strategy.mask("data2")
        
        assert hash1 != hash2
    
    def test_consistent_hashing(self):
        strategy = HashStrategy()
        text = "test_data"
        hash1 = strategy.mask(text)
        hash2 = strategy.mask(text)
        
        assert hash1 == hash2


class TestRandomizeStrategy:
    """测试随机化策略"""
    
    def test_name_randomization(self):
        strategy = RandomizeStrategy()
        config = MaskingConfig(
            strategy_type="RandomizeStrategy",
            params={"data_type": "name"}
        )
        
        name = "张三"
        randomized = strategy.mask(name, config)
        
        assert randomized != name
        assert len(randomized) > 0
    
    def test_preserve_format(self):
        strategy = RandomizeStrategy()
        config = MaskingConfig(
            strategy_type="RandomizeStrategy",
            params={"data_type": "numeric", "preserve_format": True}
        )
        
        number = "12345"
        randomized = strategy.mask(number, config)
        
        assert len(randomized) == len(number)
        assert randomized.isdigit()


class TestStrategyManager:
    """测试策略管理器"""
    
    def test_get_strategy(self):
        manager = StrategyManager()
        
        mask_strategy = manager.get_strategy("MaskStrategy")
        assert mask_strategy is not None
        assert isinstance(mask_strategy, MaskStrategy)
    
    def test_apply_strategy(self):
        manager = StrategyManager()
        
        result = manager.apply_strategy("MaskStrategy", "13812345678")
        assert result != "13812345678"
        assert "*" in result
    
    def test_apply_strategy_batch(self):
        manager = StrategyManager()
        values = ["13812345678", "15987654321", "18666888999"]
        
        results = manager.apply_strategy_batch("MaskStrategy", values)
        
        assert len(results) == len(values)
        for original, masked in zip(values, results):
            assert original != masked
            assert "*" in masked
    
    def test_default_strategy_for_type(self):
        manager = StrategyManager()
        
        assert manager.get_default_strategy_for_type("phone") == "MaskStrategy"
        assert manager.get_default_strategy_for_type("id_card") == "HashStrategy"
        assert manager.get_default_strategy_for_type("name") == "RandomizeStrategy"