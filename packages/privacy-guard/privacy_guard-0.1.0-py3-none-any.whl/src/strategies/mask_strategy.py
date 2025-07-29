"""掩码策略"""

import re
from typing import Any, Optional
from .base import BaseStrategy, MaskingConfig


class MaskStrategy(BaseStrategy):
    """掩码策略 - 用*号替换部分字符"""
    
    def __init__(self):
        super().__init__("MaskStrategy")
    
    def mask(self, value: Any, config: Optional[MaskingConfig] = None) -> Any:
        """掩码脱敏"""
        if value is None:
            return value
        
        text = self._ensure_string(value)
        if not text:
            return value
        
        # 默认配置
        mask_char = "*"
        keep_start = 3
        keep_end = 4
        
        if config and config.params:
            mask_char = config.params.get("mask_char", "*")
            keep_start = config.params.get("keep_start", 3)
            keep_end = config.params.get("keep_end", 4)
        
        # 根据数据类型智能掩码
        return self._smart_mask(text, mask_char, keep_start, keep_end)
    
    def _smart_mask(self, text: str, mask_char: str, keep_start: int, keep_end: int) -> str:
        """智能掩码"""
        length = len(text)
        
        # 短文本处理
        if length <= 2:
            return mask_char * length
        
        # 手机号特殊处理
        if re.match(r'^1[3-9]\d{9}$', text):
            return text[:3] + mask_char * 4 + text[-4:]
        
        # 身份证号特殊处理
        if re.match(r'^\d{15}|\d{17}[\dXx]$', text):
            return text[:6] + mask_char * (length - 10) + text[-4:]
        
        # 邮箱特殊处理
        if '@' in text:
            local, domain = text.split('@', 1)
            if len(local) > 2:
                masked_local = local[0] + mask_char * (len(local) - 2) + local[-1]
            else:
                masked_local = mask_char * len(local)
            return f"{masked_local}@{domain}"
        
        # 通用掩码
        if length <= keep_start + keep_end:
            # 文本太短，只保留首尾各一个字符
            return text[0] + mask_char * (length - 2) + text[-1] if length > 1 else mask_char
        
        return text[:keep_start] + mask_char * (length - keep_start - keep_end) + text[-keep_end:]