"""
yai-loguru-sinks: 企业级 Loguru Sink 工厂

基于 loguru-config 的简洁架构，提供开箱即用的企业级日志 sink。
目前专注于阿里云 SLS 支持，未来将扩展更多云服务。
"""

from .config import register_protocol_parsers, create_config_from_dict, create_config_from_file

__version__ = "0.5.0"

__all__ = [
    "register_protocol_parsers", 
    "create_config_from_dict",
    "create_config_from_file",
    "__version__",
]