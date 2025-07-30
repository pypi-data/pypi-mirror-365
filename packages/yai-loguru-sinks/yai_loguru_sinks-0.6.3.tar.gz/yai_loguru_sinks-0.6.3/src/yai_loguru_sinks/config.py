"""loguru-config 扩展配置

注册企业级 sink 协议解析器，目前专注于阿里云 SLS 支持。
"""

from typing import Any, Dict

# 检查 loguru-config 是否可用
try:
    from loguru_config import LoguruConfig
    HAS_LOGURU_CONFIG = True
except ImportError:
    HAS_LOGURU_CONFIG = False


def register_protocol_parsers() -> None:
    """注册企业级协议解析器到 loguru-config
    
    此函数将 yai-loguru-sinks 提供的企业级 sink 协议解析器注册到 loguru-config 中，
    使得用户可以在 YAML/JSON 配置文件中使用企业级协议 URL 来配置日志输出。
    
    支持的协议:
        - sls://: 阿里云 SLS (Simple Log Service) 协议
            格式: sls://project/logstore?region=cn-hangzhou&access_key_id=xxx&access_key_secret=xxx
            参数: region (必需), access_key_id, access_key_secret, topic, batch_size 等
            
        - cloudwatch://: AWS CloudWatch Logs 协议 (占位符，未实现)
        - elasticsearch://: Elasticsearch 协议 (占位符，未实现)  
        - kafka://: Apache Kafka 协议 (占位符，未实现)
    
    使用示例:
        ```python
        from yai_loguru_sinks import register_protocol_parsers
        from loguru_config import LoguruConfig
        
        # 注册协议解析器
        register_protocol_parsers()
        
        # 现在可以在配置文件中使用企业级协议
        config = LoguruConfig()
        config.load('logging.yaml')
        ```
        
        配置文件示例 (logging.yaml):
        ```yaml
        handlers:
          - sink: sls://my-project/my-logstore?region=cn-hangzhou&access_key_id=${SLS_ACCESS_KEY}&access_key_secret=${SLS_SECRET}
            level: WARNING
            format: '{time} | {level} | {message}'
        ```
    
    注意事项:
        - 必须在加载配置文件之前调用此函数
        - 此函数是幂等的，多次调用不会产生副作用
        - SLS 协议支持环境变量替换，如 ${SLS_ACCESS_KEY}
        - 凭证可以通过 URL 参数或环境变量提供
    
    环境变量:
        - SLS_ACCESS_KEY_ID: 阿里云访问密钥 ID
        - SLS_ACCESS_KEY_SECRET: 阿里云访问密钥 Secret
        - SLS_REGION: 默认区域 (可选)
    
    Raises:
        ImportError: 如果 loguru-config 未安装
        UserWarning: 如果 loguru-config 版本过旧，不支持协议解析器功能
        
    Since:
        0.5.0
    """
    if not HAS_LOGURU_CONFIG:
        raise ImportError(
            "loguru-config 未安装，请运行: uv add loguru-config"
        )
    
    from .internal.protocol_parsers import PROTOCOL_PARSERS
    
    # 注册协议解析器 - 使用列表扩展方式
    if hasattr(LoguruConfig, 'supported_protocol_parsers'):
        # 将现有的解析器转换为列表并添加新的解析器
        current_parsers = list(LoguruConfig.supported_protocol_parsers)
        LoguruConfig.supported_protocol_parsers = current_parsers + PROTOCOL_PARSERS
    else:
        # 如果 loguru-config 版本不支持协议解析器，提供警告
        import warnings
        warnings.warn(
            "当前 loguru-config 版本不支持协议解析器，请升级到最新版本",
            UserWarning
        )


def create_config_from_dict(config_dict: Dict[str, Any]) -> LoguruConfig:
    """从字典创建 LoguruConfig
    
    Args:
        config_dict: 配置字典
        
    Returns:
        配置好的 LoguruConfig 实例
    """
    config = LoguruConfig()
    config.load(config_dict)
    return config


def create_config_from_file(config_file: str) -> LoguruConfig:
    """从文件创建 LoguruConfig
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置好的 LoguruConfig 实例
    """
    config = LoguruConfig()
    config.load(config_file)
    return config