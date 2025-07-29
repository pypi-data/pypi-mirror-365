"""测试核心功能"""

import pytest
import tempfile
import pandas as pd
from pathlib import Path
from src import PrivacyGuard
from src.config import ConfigLoader


class TestPrivacyGuard:
    """测试PrivacyGuard核心类"""
    
    def test_initialization_with_default_config(self):
        pg = PrivacyGuard()
        assert pg.rules is not None
        assert len(pg.rules.field_rules) > 0
    
    def test_initialization_with_config_object(self):
        config = ConfigLoader.create_default_config()
        pg = PrivacyGuard(config)
        assert pg.rules == config
    
    def test_mask_dict(self):
        pg = PrivacyGuard()
        
        data = {
            "name": ["张三", "李四", "王五"],
            "phone": ["13812345678", "15987654321", "18666888999"],
            "age": [25, 30, 35]
        }
        
        masked_data = pg.mask_dict(data)
        
        assert len(masked_data) == len(data)
        assert "name" in masked_data
        assert "phone" in masked_data
        assert "age" in masked_data
        
        # 检查手机号是否被脱敏
        original_phones = data["phone"]
        masked_phones = masked_data["phone"]
        
        for original, masked in zip(original_phones, masked_phones):
            assert original != masked
    
    def test_analyze_dict(self):
        pg = PrivacyGuard()
        
        data = {
            "name": ["张三", "李四"],
            "phone": ["13812345678", "15987654321"],
            "email": ["test@example.com", "user@gmail.com"],
            "product": ["苹果", "橙子"]
        }
        
        analysis = pg.analyze_dict(data)
        
        assert analysis["total_fields"] == 4
        assert analysis["sensitive_fields"] >= 2  # 至少检测到phone和email
        assert "field_analysis" in analysis
    
    def test_mask_csv(self):
        pg = PrivacyGuard()
        
        # 创建测试CSV文件
        test_data = pd.DataFrame({
            "name": ["张三", "李四", "王五"],
            "phone": ["13812345678", "15987654321", "18666888999"],
            "age": [25, 30, 35]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
            test_data.to_csv(input_file.name, index=False)
            input_path = input_file.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as output_file:
            output_path = output_file.name
        
        try:
            # 执行脱敏
            result = pg.mask_csv(input_path, output_path)
            
            assert result["total_rows"] == 3
            assert result["total_columns"] == 3
            assert "processed_fields" in result
            
            # 检查输出文件
            masked_data = pd.read_csv(output_path)
            assert len(masked_data) == 3
            assert "name" in masked_data.columns
            assert "phone" in masked_data.columns
            
        finally:
            Path(input_path).unlink()
            Path(output_path).unlink()
    
    def test_analyze_csv(self):
        pg = PrivacyGuard()
        
        # 创建测试CSV文件
        test_data = pd.DataFrame({
            "user_name": ["张三", "李四"],
            "mobile": ["13812345678", "15987654321"],
            "email": ["test@example.com", "user@gmail.com"]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            analysis = pg.analyze_csv(temp_path)
            
            assert analysis["total_fields"] == 3
            assert analysis["sensitive_fields"] >= 2
            assert "field_analysis" in analysis
            
        finally:
            Path(temp_path).unlink()
    
    def test_export_and_update_config(self):
        pg = PrivacyGuard()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # 导出配置
            pg.export_config(temp_path)
            
            # 验证文件存在
            assert Path(temp_path).exists()
            
            # 更新配置
            pg.update_config(temp_path)
            
        finally:
            Path(temp_path).unlink()
    
    def test_validate_config(self):
        pg = PrivacyGuard()
        
        errors = pg.validate_config()
        assert isinstance(errors, list)