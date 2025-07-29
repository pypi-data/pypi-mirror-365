"""
SLS Sink 工厂函数

提供创建 SLS sink 的工厂函数，支持批量发送和异步处理。
"""

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
        **kwargs: 其他配置参数
    
    Returns:
        可调用的 sink 函数
    """
    from .url_parser import resolve_sls_credentials
    
    # 解析认证信息（统一在 url_parser.py 中处理）
    access_key_id, access_key_secret = resolve_sls_credentials(
        access_key_id, access_key_secret
    )
    
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
    )
    
    return SlsSink(config)