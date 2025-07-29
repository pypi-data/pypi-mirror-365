"""协议解析器内部实现

处理各种协议的解析器逻辑
"""

import re
from typing import Any, Callable

from .url_parser import parse_sls_url, resolve_sls_credentials


def sls_protocol_parser(url: str) -> Any:
    """SLS 协议解析器
    
    解析 sls:// URL 并创建对应的 sink 函数
    
    Args:
        url: SLS URL，格式如 sls://project/logstore?region=cn-hangzhou&topic=app
        
    Returns:
        配置好的 SLS sink 函数
    """
    from .factory import create_sls_sink  # 延迟导入避免循环依赖
    config = parse_sls_url(url)
    
    # 解析认证信息
    access_key_id, access_key_secret = resolve_sls_credentials(
        config.get('access_key_id'),
        config.get('access_key_secret')
    )
    config['access_key_id'] = access_key_id
    config['access_key_secret'] = access_key_secret
    
    return create_sls_sink(**config)


def cloudwatch_protocol_parser(sink_config: str) -> Callable:
    """CloudWatch 协议解析器（占位符）
    
    Args:
        sink_config: CloudWatch URL 配置
    
    Returns:
        CloudWatch sink 函数（暂未实现）
    """
    raise NotImplementedError("CloudWatch sink 暂未实现")


def elasticsearch_protocol_parser(sink_config: str) -> Callable:
    """Elasticsearch 协议解析器（占位符）
    
    Args:
        sink_config: Elasticsearch URL 配置
    
    Returns:
        Elasticsearch sink 函数（暂未实现）
    """
    raise NotImplementedError("Elasticsearch sink 暂未实现")


def kafka_protocol_parser(sink_config: str) -> Callable:
    """Kafka 协议解析器（占位符）
    
    Args:
        sink_config: Kafka URL 配置
    
    Returns:
        Kafka sink 函数（暂未实现）
    """
    raise NotImplementedError("Kafka sink 暂未实现")


# 协议解析器映射 - 使用元组格式 (regex, parser_function)
PROTOCOL_PARSERS = [
    (re.compile(r'^sls://(.*)$'), lambda self, url: sls_protocol_parser(f"sls://{url}")),
    (re.compile(r'^cloudwatch://(.*)$'), lambda self, url: cloudwatch_protocol_parser(f"cloudwatch://{url}")),
    (re.compile(r'^elasticsearch://(.*)$'), lambda self, url: elasticsearch_protocol_parser(f"elasticsearch://{url}")),
    (re.compile(r'^kafka://(.*)$'), lambda self, url: kafka_protocol_parser(f"kafka://{url}")),
]