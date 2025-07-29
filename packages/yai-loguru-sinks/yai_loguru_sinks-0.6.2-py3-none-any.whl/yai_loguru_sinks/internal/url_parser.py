"""URL 解析器内部实现

处理各种协议的 URL 解析逻辑
"""

import os
from typing import Any, Dict
from urllib.parse import urlparse, parse_qs


def resolve_sls_credentials(
    access_key_id: str | None = None,
    access_key_secret: str | None = None
) -> tuple[str, str]:
    """解析 SLS 认证信息
    
    优先使用传入的参数，如果为空则从环境变量获取
    
    Args:
        access_key_id: 访问密钥ID，可选
        access_key_secret: 访问密钥，可选
        
    Returns:
        (access_key_id, access_key_secret) 元组
        
    Raises:
        ValueError: 如果无法获取完整的认证信息
    """
    # 从环境变量获取认证信息
    if not access_key_id:
        access_key_id = os.getenv("SLS_ACCESS_KEY_ID")
    if not access_key_secret:
        access_key_secret = os.getenv("SLS_ACCESS_KEY_SECRET")
    
    if not access_key_id or not access_key_secret:
        raise ValueError(
            "SLS 认证信息缺失，请提供 access_key_id 和 access_key_secret "
            "或设置环境变量 SLS_ACCESS_KEY_ID 和 SLS_ACCESS_KEY_SECRET"
        )
    
    return access_key_id, access_key_secret


def parse_sls_url(url: str) -> Dict[str, Any]:
    """解析 SLS URL 格式
    
    支持的 URL 格式：
        sls://project/logstore?region=xxx&access_key_id=xxx&access_key_secret=xxx
    
    完整示例：
        sls://yai-log-test/app-log?region=cn-beijing&topic=python-app&batch_size=100&flush_interval=5.0&compress=true
        sls://my-project/error-log?region=cn-hangzhou&access_key_id=LTAI5xxx&access_key_secret=xxx&source=web-server
    
    必需参数：
        - project: 阿里云 SLS 项目名
        - logstore: 日志库名
        - region: 地域，如 cn-beijing, cn-hangzhou, cn-shanghai
    
    可选参数：
        - access_key_id: 访问密钥 ID（可通过环境变量 SLS_ACCESS_KEY_ID 设置）
        - access_key_secret: 访问密钥（可通过环境变量 SLS_ACCESS_KEY_SECRET 设置）
        - topic: 日志主题，默认 "python-app"
        - source: 日志来源，默认 "yai-loguru"
        - batch_size: 批量发送大小，默认 100
        - flush_interval: 刷新间隔（秒），默认 5.0
        - compress: 是否压缩，默认 true
    
    Args:
        url: SLS URL 字符串
        
    Returns:
        解析后的配置字典
        
    Raises:
        ValueError: URL 格式无效或缺少必需参数
    """
    parsed = urlparse(url)
    
    if parsed.scheme != 'sls':
        raise ValueError(f"无效的 SLS URL scheme: {parsed.scheme}")
    
    # 解析路径，project 在 netloc 中，logstore 在 path 中
    project = parsed.netloc
    logstore = parsed.path.strip('/')
    
    if not project:
        raise ValueError(f"无效的 SLS URL: 缺少项目名")
    
    if not logstore:
        raise ValueError(f"无效的 SLS URL: 缺少日志库名")
    
    # 解析查询参数
    query_params = parse_qs(parsed.query)
    
    # 提取必需参数
    region = query_params.get('region', [None])[0]
    if not region:
        raise ValueError("SLS URL 缺少 region 参数")
    
    config: Dict[str, Any] = {
        'project': project,
        'logstore': logstore,
        'region': region,
    }
    
    # 提取可选参数
    optional_params = [
        'access_key_id', 'access_key_secret', 'topic', 'source',
        'batch_size', 'flush_interval', 'compress'
    ]
    
    for param in optional_params:
        if param in query_params:
            raw_value = query_params[param][0]
            # 类型转换
            if param in ['batch_size']:
                config[param] = int(raw_value)
            elif param in ['flush_interval']:
                config[param] = float(raw_value)
            elif param in ['compress']:
                config[param] = raw_value.lower() in ('true', '1', 'yes')
            else:
                config[param] = raw_value
    
    return config