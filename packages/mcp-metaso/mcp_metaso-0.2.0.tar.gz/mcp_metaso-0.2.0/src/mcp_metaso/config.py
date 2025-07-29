"""MCP Metaso Server配置管理

提供配置类和全局配置实例，支持环境变量配置。
"""
import os
from typing import Optional


class Config:
    """配置类
    
    管理MCP Metaso服务器的所有配置项，包括API密钥、基础URL、超时设置等。
    支持通过环境变量进行配置。
    
    Attributes:
        api_key (str): Metaso API密钥
        base_url (str): Metaso API基础URL
        timeout (int): HTTP请求超时时间（秒）
    """
    
    def __init__(self) -> None:
        """初始化配置
        
        从环境变量中读取配置项，如果环境变量不存在则使用默认值。
        """
        self.api_key = self._get_optional_env("METASO_API_KEY", "")
        self.base_url = "https://metaso.cn/api/v1"
        self.timeout = 30
        
    def _get_required_env(self, key: str) -> str:
        """获取必需的环境变量
        
        Args:
            key: 环境变量名
            
        Returns:
            str: 环境变量值
            
        Raises:
            ValueError: 当环境变量不存在时抛出异常
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"环境变量 {key} 是必需的，请设置后重试")
        return value
    
    def _get_optional_env(self, key: str, default: str) -> str:
        """获取可选的环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            
        Returns:
            str: 环境变量值或默认值
        """
        return os.getenv(key, default)
    
    def validate(self) -> bool:
        """验证配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        return bool(self.api_key and self.base_url)
    
    def __repr__(self) -> str:
        """配置对象的字符串表示
        
        Returns:
            str: 配置信息（隐藏敏感信息）
        """
        masked_key = f"{self.api_key[:8]}..." if len(self.api_key) > 8 else "未设置"
        return f"Config(api_key='{masked_key}', base_url='{self.base_url}', timeout={self.timeout})"


# 全局配置实例
config = Config()