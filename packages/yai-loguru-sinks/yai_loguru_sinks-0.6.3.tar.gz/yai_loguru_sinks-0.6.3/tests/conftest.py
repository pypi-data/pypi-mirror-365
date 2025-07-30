"""pytest 配置文件

提供测试的共享配置、fixture和工具函数。
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
import time
from pathlib import Path


@pytest.fixture
def mock_sls_config():
    """模拟SLS配置"""
    return {
        "project": "test-project",
        "logstore": "test-logstore",
        "region": "cn-hangzhou",
        "access_key_id": "test-access-key",
        "access_key_secret": "test-access-secret",
        "app_name": "test-app",
        "app_version": "1.0.0",
        "environment": "testing"
    }


@pytest.fixture
def mock_loguru_record():
    """模拟loguru日志记录"""
    return {
        'time': SimpleNamespace(timestamp=lambda: time.time()),
        'level': SimpleNamespace(name='INFO'),
        'message': '测试日志消息',
        'name': 'test_module',
        'function': 'test_function',
        'line': 42,
        'extra': {'extra': {'user_id': '12345', 'action': 'test'}}
    }


@pytest.fixture
def mock_loguru_message(mock_loguru_record):
    """模拟loguru消息对象"""
    return SimpleNamespace(record=mock_loguru_record)


@pytest.fixture
def temp_dir():
    """临时目录fixture"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_aliyun_sdk():
    """模拟阿里云SDK"""
    with patch('yai_loguru_sinks.internal.core.HAS_ALIYUN_SDK', True):
        mock_client = MagicMock()
        mock_log_item = MagicMock()
        mock_put_logs_request = MagicMock()
        
        with patch('yai_loguru_sinks.internal.core.LogClient', return_value=mock_client), \
             patch('yai_loguru_sinks.internal.async_handler.LogItem', return_value=mock_log_item), \
             patch('yai_loguru_sinks.internal.async_handler.PutLogsRequest', return_value=mock_put_logs_request):
            yield {
                'client': mock_client,
                'log_item': mock_log_item,
                'put_logs_request': mock_put_logs_request
            }


@pytest.fixture
def clean_env():
    """清理环境变量"""
    # 保存原始环境变量
    original_env = {}
    env_keys = [
        'SLS_ACCESS_KEY_ID', 'SLS_ACCESS_KEY_SECRET',
        'APP_NAME', 'APP_VERSION', 'ENVIRONMENT',
        'SLS_AUTO_DETECT_HOSTNAME', 'SLS_AUTO_DETECT_HOST_IP',
        'SLS_AUTO_DETECT_THREAD', 'SLS_DEFAULT_CATEGORY'
    ]
    
    for key in env_keys:
        if key in os.environ:
            original_env[key] = os.environ[key]
            del os.environ[key]
    
    yield
    
    # 恢复环境变量
    for key, value in original_env.items():
        os.environ[key] = value


@pytest.fixture
def sample_env_vars():
    """示例环境变量"""
    return {
        'SLS_ACCESS_KEY_ID': 'test-key-id',
        'SLS_ACCESS_KEY_SECRET': 'test-key-secret',
        'APP_NAME': 'test-app',
        'APP_VERSION': '2.0.0',
        'ENVIRONMENT': 'testing',
        'SLS_AUTO_DETECT_HOSTNAME': 'true',
        'SLS_AUTO_DETECT_HOST_IP': 'false',
        'SLS_AUTO_DETECT_THREAD': 'true',
        'SLS_DEFAULT_CATEGORY': 'test-category'
    }


@pytest.fixture
def mock_socket():
    """模拟socket操作"""
    with patch('socket.gethostname', return_value='test-hostname'), \
         patch('socket.socket') as mock_sock:
        
        # 模拟socket连接获取IP
        mock_sock_instance = MagicMock()
        mock_sock_instance.getsockname.return_value = ('192.168.1.100', 12345)
        mock_sock.return_value = mock_sock_instance
        
        yield mock_sock_instance


# 测试标记
pytest_plugins = []


def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "unit: 单元测试标记"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试标记"
    )
    config.addinivalue_line(
        "markers", "e2e: 端到端测试标记"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试标记"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    # 为没有标记的测试添加unit标记
    for item in items:
        if not any(mark.name in ['unit', 'integration', 'e2e'] for mark in item.iter_markers()):
            item.add_marker(pytest.mark.unit)