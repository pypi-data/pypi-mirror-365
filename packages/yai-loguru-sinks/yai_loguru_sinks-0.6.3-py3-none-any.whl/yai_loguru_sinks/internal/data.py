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
    
    # PackId 功能默认启用，无需配置
    
    # 新增应用信息配置
    app_name: str = "unknown-app"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # 系统信息（可自动获取）
    auto_detect_hostname: bool = True
    auto_detect_host_ip: bool = True
    auto_detect_thread: bool = False
    
    # 日志分类配置
    default_category: str = "application"
    
    # 其他配置
    compress: bool = True