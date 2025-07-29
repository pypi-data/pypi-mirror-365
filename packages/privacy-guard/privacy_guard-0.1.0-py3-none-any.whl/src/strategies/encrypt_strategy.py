"""加密策略"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Any, Optional
from .base import BaseStrategy, MaskingConfig


class EncryptStrategy(BaseStrategy):
    """加密策略 - 可逆加密脱敏"""
    
    def __init__(self):
        super().__init__("EncryptStrategy")
        self._fernet_cache = {}
    
    def mask(self, value: Any, config: Optional[MaskingConfig] = None) -> Any:
        """加密脱敏"""
        if value is None:
            return value
        
        text = self._ensure_string(value)
        if not text:
            return value
        
        # 默认配置
        password = "default_password"
        salt = b"privacy_guard_salt"
        
        if config and config.params:
            password = config.params.get("password", "default_password")
            salt_str = config.params.get("salt", "privacy_guard_salt")
            salt = salt_str.encode() if isinstance(salt_str, str) else salt_str
        
        fernet = self._get_fernet(password, salt)
        encrypted_data = fernet.encrypt(text.encode())
        
        # 返回Base64编码的字符串
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def unmask(self, encrypted_value: str, password: str, salt: bytes = b"privacy_guard_salt") -> str:
        """解密数据"""
        try:
            fernet = self._get_fernet(password, salt)
            encrypted_data = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted_data = fernet.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {e}")
    
    def _get_fernet(self, password: str, salt: bytes) -> Fernet:
        """获取Fernet加密对象（带缓存）"""
        cache_key = f"{password}_{salt.hex()}"
        
        if cache_key not in self._fernet_cache:
            # 生成密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            self._fernet_cache[cache_key] = Fernet(key)
        
        return self._fernet_cache[cache_key]