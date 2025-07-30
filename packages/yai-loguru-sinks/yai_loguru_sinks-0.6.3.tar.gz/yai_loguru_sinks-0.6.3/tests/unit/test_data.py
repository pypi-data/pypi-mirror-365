"""测试数据配置类

测试 SlsConfig 数据类的功能和验证。
"""

import pytest
from yai_loguru_sinks.internal.data import SlsConfig


class TestSlsConfig:
    """测试 SlsConfig 数据类"""
    
    @pytest.mark.unit
    def test_sls_config_creation(self):
        """测试创建 SLS 配置"""
        config = SlsConfig(
            endpoint="https://test.log.aliyuncs.com",
            access_key_id="test_key",
            access_key_secret="test_secret",
            project="test_project",
            logstore="test_logstore"
        )
        
        assert config.endpoint == "https://test.log.aliyuncs.com"
        assert config.access_key_id == "test_key"
        assert config.access_key_secret == "test_secret"
        assert config.project == "test_project"
        assert config.logstore == "test_logstore"
    
    @pytest.mark.unit
    def test_sls_config_defaults(self):
        """测试 SLS 配置默认值"""
        config = SlsConfig(
            endpoint="https://test.log.aliyuncs.com",
            access_key_id="test_key",
            access_key_secret="test_secret",
            project="test_project",
            logstore="test_logstore"
        )
        
        # 测试默认值
        assert config.topic == "python-app"
        assert config.source == "yai-loguru"
        assert config.batch_size == 100
        assert config.flush_interval == 5.0
        assert config.max_retries == 3
        assert config.timeout == 30.0
        assert config.compress is True
        
        # 测试新增的默认值
        assert config.app_name == "unknown-app"
        assert config.app_version == "1.0.0"
        assert config.environment == "development"
        assert config.auto_detect_hostname is True
        assert config.auto_detect_host_ip is True
        assert config.auto_detect_thread is False
        assert config.default_category == "application"
    
    @pytest.mark.unit
    def test_sls_config_custom_values(self):
        """测试自定义配置值"""
        config = SlsConfig(
            endpoint="https://custom.log.aliyuncs.com",
            access_key_id="custom_key",
            access_key_secret="custom_secret",
            project="custom_project",
            logstore="custom_logstore",
            topic="custom-topic",
            source="custom-source",
            batch_size=200,
            flush_interval=10.0,
            max_retries=5,
            timeout=60.0,
            compress=False,
            app_name="custom-app",
            app_version="2.0.0",
            environment="production",
            auto_detect_hostname=False,
            auto_detect_host_ip=False,
            auto_detect_thread=True,
            default_category="custom"
        )
        
        assert config.topic == "custom-topic"
        assert config.source == "custom-source"
        assert config.batch_size == 200
        assert config.flush_interval == 10.0
        assert config.max_retries == 5
        assert config.timeout == 60.0
        assert config.compress is False
        assert config.app_name == "custom-app"
        assert config.app_version == "2.0.0"
        assert config.environment == "production"
        assert config.auto_detect_hostname is False
        assert config.auto_detect_host_ip is False
        assert config.auto_detect_thread is True
        assert config.default_category == "custom"
    
    @pytest.mark.unit
    def test_sls_config_immutable(self):
        """测试配置对象的不可变性（dataclass 特性）"""
        config = SlsConfig(
            endpoint="https://test.log.aliyuncs.com",
            access_key_id="test_key",
            access_key_secret="test_secret",
            project="test_project",
            logstore="test_logstore"
        )
        
        # 可以修改属性（dataclass 默认是可变的）
        config.app_name = "modified-app"
        assert config.app_name == "modified-app"
        
        # 测试类型提示（通过创建新实例验证）
        new_config = SlsConfig(
            endpoint="https://test2.log.aliyuncs.com",
            access_key_id="test_key2",
            access_key_secret="test_secret2",
            project="test_project2",
            logstore="test_logstore2",
            batch_size=150  # 应该是 int 类型
        )
        
        assert isinstance(new_config.batch_size, int)
        assert isinstance(new_config.flush_interval, float)
        assert isinstance(new_config.auto_detect_hostname, bool)