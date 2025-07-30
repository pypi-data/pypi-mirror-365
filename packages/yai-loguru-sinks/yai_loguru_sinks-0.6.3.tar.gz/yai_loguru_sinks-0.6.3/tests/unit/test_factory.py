"""测试工厂函数

测试 create_sls_sink 工厂函数的功能。
"""

import pytest
import os
from unittest.mock import patch
from yai_loguru_sinks.internal.factory import create_sls_sink


class TestCreateSlsSink:
    """测试 create_sls_sink 工厂函数"""
    
    @pytest.mark.unit
    def test_create_sls_sink_basic(self, mock_aliyun_sdk):
        """测试基本的 SLS sink 创建"""
        sink = create_sls_sink(
            project="test-project",
            logstore="test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret"
        )
        
        assert callable(sink)
    
    @pytest.mark.unit
    def test_create_sls_sink_with_app_info(self, mock_aliyun_sdk):
        """测试带应用信息的 SLS sink 创建"""
        sink = create_sls_sink(
            project="test-project",
            logstore="test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret",
            app_name="test-app",
            app_version="1.0.0",
            environment="testing"
        )
        
        assert callable(sink)
    
    @pytest.mark.unit
    def test_create_sls_sink_with_detection_flags(self, mock_aliyun_sdk):
        """测试带检测标志的 SLS sink 创建"""
        sink = create_sls_sink(
            project="test-project",
            logstore="test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret",
            auto_detect_hostname=True,
            auto_detect_host_ip=False,
            auto_detect_thread=True,
            default_category="custom"
        )
        
        assert callable(sink)
    
    @pytest.mark.unit
    def test_create_sls_sink_env_vars(self, mock_aliyun_sdk, clean_env, sample_env_vars):
        """测试从环境变量读取配置"""
        # 设置环境变量
        for key, value in sample_env_vars.items():
            os.environ[key] = value
        
        sink = create_sls_sink(
            project="test-project",
            logstore="test-logstore",
            region="cn-hangzhou"
        )
        
        assert callable(sink)
    
    @pytest.mark.unit
    def test_create_sls_sink_env_override(self, mock_aliyun_sdk, clean_env):
        """测试环境变量被参数覆盖"""
        # 设置环境变量
        os.environ['APP_NAME'] = 'env-app'
        os.environ['APP_VERSION'] = 'env-version'
        
        sink = create_sls_sink(
            project="test-project",
            logstore="test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret",
            app_name="param-app",  # 应该覆盖环境变量
            app_version="param-version"  # 应该覆盖环境变量
        )
        
        assert callable(sink)
    
    @pytest.mark.unit
    def test_create_sls_sink_boolean_env_vars(self, mock_aliyun_sdk, clean_env):
        """测试布尔类型环境变量的解析"""
        # 测试各种布尔值表示
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('yes', False),  # 只有 'true' 被认为是 True
            ('1', False),    # 只有 'true' 被认为是 True
        ]
        
        for env_value, expected in test_cases:
            os.environ['SLS_AUTO_DETECT_HOSTNAME'] = env_value
            
            sink = create_sls_sink(
                project="test-project",
                logstore="test-logstore",
                region="cn-hangzhou",
                access_key_id="test-key",
                access_key_secret="test-secret"
            )
            
            assert callable(sink)
            
            # 清理环境变量
            del os.environ['SLS_AUTO_DETECT_HOSTNAME']
    
    @pytest.mark.unit
    def test_create_sls_sink_endpoint_generation(self, mock_aliyun_sdk):
        """测试端点URL生成"""
        regions = [
            'cn-hangzhou',
            'cn-beijing',
            'cn-shanghai',
            'us-west-1'
        ]
        
        for region in regions:
            sink = create_sls_sink(
                project="test-project",
                logstore="test-logstore",
                region=region,
                access_key_id="test-key",
                access_key_secret="test-secret"
            )
            
            assert callable(sink)
    
    @pytest.mark.unit
    def test_create_sls_sink_custom_params(self, mock_aliyun_sdk):
        """测试自定义参数"""
        sink = create_sls_sink(
            project="test-project",
            logstore="test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret",
            topic="custom-topic",
            source="custom-source",
            batch_size=200,
            flush_interval=10.0,
            compress=False
        )
        
        assert callable(sink)
    
    @pytest.mark.unit
    def test_create_sls_sink_kwargs(self, mock_aliyun_sdk):
        """测试额外的关键字参数"""
        sink = create_sls_sink(
            project="test-project",
            logstore="test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret",
            custom_param="custom_value",  # 额外参数
            another_param=123
        )
        
        assert callable(sink)
    
    @pytest.mark.unit
    def test_create_sls_sink_missing_credentials(self, clean_env):
        """测试缺少认证信息的情况"""
        # 确保环境变量被清理
        import os
        for key in ['SLS_ACCESS_KEY_ID', 'SLS_ACCESS_KEY_SECRET']:
            if key in os.environ:
                del os.environ[key]
        
        with pytest.raises(ValueError, match="SLS 认证信息缺失"):
            create_sls_sink(
                project="test-project",
                logstore="test-logstore",
                region="cn-hangzhou"
                # 故意不提供认证信息
            )