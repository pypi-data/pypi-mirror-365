"""随机化策略"""

import random
import string
from faker import Faker
from typing import Any, Optional
from .base import BaseStrategy, MaskingConfig


class RandomizeStrategy(BaseStrategy):
    """随机化策略 - 生成随机数据替换"""
    
    def __init__(self):
        super().__init__("RandomizeStrategy")
        self.fake = Faker('zh_CN')  # 中文本地化
    
    def mask(self, value: Any, config: Optional[MaskingConfig] = None) -> Any:
        """随机化脱敏"""
        if value is None:
            return value
        
        text = self._ensure_string(value)
        if not text:
            return value
        
        # 默认配置
        data_type = "generic"
        preserve_format = True
        
        if config and config.params:
            data_type = config.params.get("data_type", "generic")
            preserve_format = config.params.get("preserve_format", True)
        
        return self._generate_fake_data(text, data_type, preserve_format)
    
    def _generate_fake_data(self, original: str, data_type: str, preserve_format: bool) -> str:
        """生成假数据"""
        if data_type == "name":
            return self.fake.name()
        
        elif data_type == "phone":
            return self.fake.phone_number()
        
        elif data_type == "email":
            if preserve_format and '@' in original:
                domain = original.split('@')[1]
                username = self.fake.user_name()
                return f"{username}@{domain}"
            return self.fake.email()
        
        elif data_type == "address":
            return self.fake.address()
        
        elif data_type == "id_card":
            return self.fake.ssn()
        
        elif data_type == "bank_card":
            return self.fake.credit_card_number()
        
        elif data_type == "date":
            return self.fake.date()
        
        elif data_type == "numeric":
            # 保持数字长度
            if preserve_format and original.isdigit():
                length = len(original)
                return ''.join([str(random.randint(0, 9)) for _ in range(length)])
            return str(self.fake.random_int())
        
        else:  # generic
            if preserve_format:
                return self._preserve_format_random(original)
            return self.fake.text(max_nb_chars=len(original))
    
    def _preserve_format_random(self, original: str) -> str:
        """保持格式的随机化"""
        result = []
        for char in original:
            if char.isalpha():
                if char.islower():
                    result.append(random.choice(string.ascii_lowercase))
                else:
                    result.append(random.choice(string.ascii_uppercase))
            elif char.isdigit():
                result.append(str(random.randint(0, 9)))
            else:
                result.append(char)  # 保持特殊字符不变
        return ''.join(result)