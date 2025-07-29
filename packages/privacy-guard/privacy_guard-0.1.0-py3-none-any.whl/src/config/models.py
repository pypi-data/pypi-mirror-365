"""配置模型"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class FieldRule(BaseModel):
    """字段规则配置"""
    field_name: str = Field(..., description="字段名称")
    data_type: Optional[str] = Field(None, description="数据类型")
    strategy: str = Field(..., description="脱敏策略")
    params: Dict[str, Any] = Field(default_factory=dict, description="策略参数")
    enabled: bool = Field(True, description="是否启用")


class GlobalConfig(BaseModel):
    """全局配置"""
    auto_detect: bool = Field(True, description="是否自动检测敏感数据")
    default_strategy: str = Field("MaskStrategy", description="默认脱敏策略") 
    preserve_null: bool = Field(True, description="是否保留空值")
    batch_size: int = Field(1000, description="批处理大小")


class MaskingRules(BaseModel):
    """脱敏规则配置"""
    version: str = Field("1.0", description="配置版本")
    global_config: GlobalConfig = Field(default_factory=GlobalConfig)
    field_rules: List[FieldRule] = Field(default_factory=list, description="字段规则列表")
    
    def get_rule_for_field(self, field_name: str) -> Optional[FieldRule]:
        """获取字段的规则"""
        for rule in self.field_rules:
            if rule.field_name == field_name and rule.enabled:
                return rule
        return None
    
    def add_rule(self, rule: FieldRule):
        """添加规则"""
        # 检查是否已存在同名规则
        existing_rule = self.get_rule_for_field(rule.field_name)
        if existing_rule:
            # 更新现有规则
            for i, r in enumerate(self.field_rules):
                if r.field_name == rule.field_name:
                    self.field_rules[i] = rule
                    break
        else:
            self.field_rules.append(rule)
    
    def remove_rule(self, field_name: str):
        """移除规则"""
        self.field_rules = [r for r in self.field_rules if r.field_name != field_name]