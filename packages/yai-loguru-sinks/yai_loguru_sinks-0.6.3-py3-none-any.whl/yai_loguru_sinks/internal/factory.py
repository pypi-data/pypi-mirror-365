"""
SLS Sink 工厂函数

提供创建 SLS sink 的工厂函数，支持批量发送和异步处理。
"""

import os
from typing import Optional, Callable, Dict, Any

from .data import SlsConfig
from .core import SlsSink


def create_sls_sink(
    project: str,
    logstore: str,
    region: str,
    access_key_id: Optional[str] = None,
    access_key_secret: Optional[str] = None,
    topic: str = "python-app",
    source: str = "yai-loguru",
    batch_size: int = 100,
    flush_interval: float = 5.0,
    compress: bool = True,
    # 新增应用信息参数
    app_name: Optional[str] = None,
    app_version: Optional[str] = None,
    environment: Optional[str] = None,
    # 系统信息检测参数
    auto_detect_hostname: Optional[bool] = None,
    auto_detect_host_ip: Optional[bool] = None,
    auto_detect_thread: Optional[bool] = None,
    # 日志分类参数
    default_category: Optional[str] = None,
    **kwargs: Any
) -> Callable[[Dict[str, Any]], None]:
    """创建 SLS sink 函数
    
    Args:
        project: SLS 项目名
        logstore: SLS 日志库名
        region: 阿里云区域，如 'cn-hangzhou'
        access_key_id: 访问密钥ID，默认从环境变量 SLS_ACCESS_KEY_ID 获取
        access_key_secret: 访问密钥，默认从环境变量 SLS_ACCESS_KEY_SECRET 获取
        topic: 日志主题
        source: 日志来源
        batch_size: 批量发送大小
        flush_interval: 刷新间隔（秒）
        compress: 是否压缩
        app_name: 应用名称，默认从环境变量 APP_NAME 获取
        app_version: 应用版本，默认从环境变量 APP_VERSION 获取
        environment: 运行环境，默认从环境变量 ENVIRONMENT 获取
        auto_detect_hostname: 是否自动检测主机名
        auto_detect_host_ip: 是否自动检测主机IP
        auto_detect_thread: 是否自动检测线程信息
        default_category: 默认日志分类
        **kwargs: 其他配置参数
    
    Returns:
        可调用的 sink 函数
    """
    from .url_parser import resolve_sls_credentials
    
    # 解析认证信息（统一在 url_parser.py 中处理）
    access_key_id, access_key_secret = resolve_sls_credentials(
        access_key_id, access_key_secret
    )
    
    # 从环境变量获取应用信息配置
    app_name = app_name or os.getenv('APP_NAME', 'unknown-app')
    app_version = app_version or os.getenv('APP_VERSION', '1.0.0')
    environment = environment or os.getenv('ENVIRONMENT', 'development')
    
    # 从环境变量获取系统检测配置
    if auto_detect_hostname is None:
        auto_detect_hostname = os.getenv('SLS_AUTO_DETECT_HOSTNAME', 'true').lower() == 'true'
    if auto_detect_host_ip is None:
        auto_detect_host_ip = os.getenv('SLS_AUTO_DETECT_HOST_IP', 'true').lower() == 'true'
    if auto_detect_thread is None:
        auto_detect_thread = os.getenv('SLS_AUTO_DETECT_THREAD', 'false').lower() == 'true'
    
    # 从环境变量获取分类配置
    default_category = default_category or os.getenv('SLS_DEFAULT_CATEGORY', 'application')
    
    # 构造 endpoint
    endpoint = f"https://{region}.log.aliyuncs.com"
    
    config = SlsConfig(
        endpoint=endpoint,
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        project=project,
        logstore=logstore,
        topic=topic,
        source=source,
        batch_size=batch_size,
        flush_interval=flush_interval,
        compress=compress,
        # 新增配置
        app_name=app_name,
        app_version=app_version,
        environment=environment,
        auto_detect_hostname=auto_detect_hostname,
        auto_detect_host_ip=auto_detect_host_ip,
        auto_detect_thread=auto_detect_thread,
        default_category=default_category,
    )
    
    return SlsSink(config)