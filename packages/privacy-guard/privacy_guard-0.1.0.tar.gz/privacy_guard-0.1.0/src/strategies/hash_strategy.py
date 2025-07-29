"""哈希策略"""

import hashlib
from typing import Any, Optional
from .base import BaseStrategy, MaskingConfig


class HashStrategy(BaseStrategy):
    """哈希策略 - 使用哈希函数脱敏"""
    
    def __init__(self):
        super().__init__("HashStrategy")
    
    def mask(self, value: Any, config: Optional[MaskingConfig] = None) -> Any:
        """哈希脱敏"""
        if value is None:
            return value
        
        text = self._ensure_string(value)
        if not text:
            return value
        
        # 默认配置
        algorithm = "sha256"
        salt = ""
        truncate_length = None
        
        if config and config.params:
            algorithm = config.params.get("algorithm", "sha256")
            salt = config.params.get("salt", "")
            truncate_length = config.params.get("truncate_length")
        
        # 加盐
        salted_value = salt + text
        
        # 计算哈希
        if algorithm == "md5":
            hash_obj = hashlib.md5(salted_value.encode())
        elif algorithm == "sha1":
            hash_obj = hashlib.sha1(salted_value.encode())
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256(salted_value.encode())
        else:
            raise ValueError(f"不支持的哈希算法: {algorithm}")
        
        hash_value = hash_obj.hexdigest()
        
        # 截断
        if truncate_length and truncate_length > 0:
            hash_value = hash_value[:truncate_length]
        
        return hash_value