"""
SLS Sink 配置类

定义 SLS 连接、批量发送和 PackId 相关的配置。
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class SlsConfig:
    """SLS Sink 配置"""
    
    # SLS 连接配置
    endpoint: str
    access_key_id: str
    access_key_secret: str
    project: str
    logstore: str
    
    # SLS 特定配置
    topic: str = "python-app"
    source: str = "yai-loguru"
    
    # 批量发送配置
    batch_size: int = 100
    flush_interval: float = 5.0
    max_retries: int = 3
    timeout: float = 30.0
    
    # PackId 配置
    enable_pack_id: bool = True
    context_prefix: Optional[str] = None
    pack_id_per_batch: bool = True
    pack_id_per_message: bool = False
    
    # 其他配置
    compress: bool = True