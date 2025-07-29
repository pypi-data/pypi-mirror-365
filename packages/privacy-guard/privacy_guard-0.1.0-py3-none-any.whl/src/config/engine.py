"""规则引擎"""

from typing import Dict, List, Any, Optional
from ..detectors import DetectorManager, DetectionResult
from ..strategies import StrategyManager, MaskingConfig
from .models import MaskingRules, FieldRule


class RuleEngine:
    """规则引擎 - 协调检测器和策略管理器"""
    
    def __init__(self, rules: MaskingRules):
        self.rules = rules
        self.detector_manager = DetectorManager()
        self.strategy_manager = StrategyManager()
    
    def update_rules(self, rules: MaskingRules):
        """更新规则"""
        self.rules = rules
    
    def process_dataset(self, data: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        """处理整个数据集"""
        result = {}
        
        for field_name, values in data.items():
            result[field_name] = self.process_field(field_name, values)
        
        return result
    
    def process_field(self, field_name: str, values: List[Any]) -> List[Any]:
        """处理单个字段"""
        # 1. 检查是否有预定义规则
        field_rule = self.rules.get_rule_for_field(field_name)
        
        if field_rule:
            # 使用预定义规则
            strategy_name = field_rule.strategy
            config = MaskingConfig(
                strategy_type=strategy_name,
                params=field_rule.params
            )
        else:
            # 2. 自动检测（如果启用）
            if not self.rules.global_config.auto_detect:
                return values  # 不自动检测，返回原值
            
            detection_result = self.detector_manager.detect_field(field_name, values)
            if not detection_result:
                return values  # 未检测到敏感数据
            
            # 3. 使用默认策略
            strategy_name = self.strategy_manager.get_default_strategy_for_type(
                detection_result.data_type
            )
            config = MaskingConfig(
                strategy_type=strategy_name,
                params={}
            )
        
        # 4. 应用脱敏策略
        try:
            return self.strategy_manager.apply_strategy_batch(
                strategy_name, values, config
            )
        except Exception as e:
            print(f"警告: 字段 {field_name} 脱敏失败: {e}")
            return values
    
    def analyze_dataset(self, data: Dict[str, List[Any]]) -> Dict[str, Any]:
        """分析数据集，返回检测结果"""
        detection_results = self.detector_manager.detect_dataset(data)
        
        analysis = {
            "total_fields": len(data),
            "sensitive_fields": len(detection_results),
            "field_analysis": {},
            "recommendations": []
        }
        
        for field_name, result in detection_results.items():
            field_rule = self.rules.get_rule_for_field(field_name)
            
            analysis["field_analysis"][field_name] = {
                "data_type": result.data_type,
                "confidence": result.confidence,
                "has_rule": field_rule is not None,
                "recommended_strategy": self.strategy_manager.get_default_strategy_for_type(
                    result.data_type
                ),
                "sample_values": result.sample_values
            }
            
            if not field_rule:
                analysis["recommendations"].append(
                    f"建议为字段 '{field_name}' ({result.data_type}) 创建脱敏规则"
                )
        
        return analysis
    
    def validate_rules(self) -> List[str]:
        """验证规则配置"""
        errors = []
        
        for rule in self.rules.field_rules:
            # 检查策略是否存在
            if not self.strategy_manager.get_strategy(rule.strategy):
                errors.append(f"字段 '{rule.field_name}': 未知的策略 '{rule.strategy}'")
        
        return errors