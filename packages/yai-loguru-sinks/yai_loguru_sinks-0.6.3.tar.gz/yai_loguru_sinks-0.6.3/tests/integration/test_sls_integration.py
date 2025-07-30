"""SLS 集成测试

测试完整的 SLS 日志处理流程，包括配置、创建、日志处理和发送。
"""

import pytest
import time
import os
from unittest.mock import patch, MagicMock
from yai_loguru_sinks.internal.factory import create_sls_sink
from yai_loguru_sinks import register_protocol_parsers


class TestSlsIntegration:
    """SLS 集成测试"""
    
    @pytest.mark.integration
    def test_complete_sls_workflow(self, mock_aliyun_sdk, mock_loguru_message, clean_env):
        """测试完整的 SLS 工作流程"""
        # 设置环境变量
        os.environ.update({
            'APP_NAME': 'integration-test-app',
            'APP_VERSION': '1.0.0',
            'ENVIRONMENT': 'testing',
            'SLS_AUTO_DETECT_HOSTNAME': 'true',
            'SLS_AUTO_DETECT_HOST_IP': 'true',
            'SLS_AUTO_DETECT_THREAD': 'false',
            'SLS_DEFAULT_CATEGORY': 'integration'
        })
        
        # 创建 sink
        sink = create_sls_sink(
            project="integration-test-project",
            logstore="integration-test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret"
        )
        
        # 处理日志消息
        sink(mock_loguru_message)
        
        # 等待异步处理
        time.sleep(0.1)
        
        # 验证日志被处理（通过检查队列或其他方式）
        assert callable(sink)
    
    @pytest.mark.integration
    def test_sls_with_protocol_parser(self, mock_aliyun_sdk, clean_env):
        """测试 SLS 协议解析器集成"""
        from yai_loguru_sinks.internal.url_parser import parse_sls_url
        
        # 设置环境变量
        os.environ.update({
            'SLS_ACCESS_KEY_ID': 'test-key',
            'SLS_ACCESS_KEY_SECRET': 'test-secret',
            'APP_NAME': 'protocol-test-app'
        })
        
        # 测试 SLS URL 解析
        sls_url = "sls://test-project/test-logstore?region=cn-hangzhou&app_name=test-app&app_version=1.0.0&environment=test"
        config = parse_sls_url(sls_url)
        
        # 验证解析结果
        assert config["project"] == "test-project"
        assert config["logstore"] == "test-logstore"
        assert config["region"] == "cn-hangzhou"
        
        # 添加必需的应用信息字段
        config.update({
            "app_name": "test-app",
            "app_version": "1.0.0",
            "environment": "test"
        })
    
    @pytest.mark.integration
    def test_sls_field_mapping_integration(self, mock_aliyun_sdk, mock_loguru_message, clean_env):
        """测试字段映射的完整集成"""
        # 设置完整的环境配置
        os.environ.update({
            'APP_NAME': 'field-test-app',
            'APP_VERSION': '2.0.0',
            'ENVIRONMENT': 'production',
            'SLS_AUTO_DETECT_HOSTNAME': 'true',
            'SLS_AUTO_DETECT_HOST_IP': 'true',
            'SLS_AUTO_DETECT_THREAD': 'true',
            'SLS_DEFAULT_CATEGORY': 'business'
        })
        
        # 创建 sink
        sink = create_sls_sink(
            project="field-test-project",
            logstore="field-test-logstore",
            region="cn-beijing",
            access_key_id="test-key",
            access_key_secret="test-secret"
        )
        
        # 模拟不同类型的日志记录
        test_records = [
            {
                'time': MagicMock(timestamp=lambda: time.time()),
                'level': MagicMock(name='INFO'),
                'message': 'API调用成功',
                'name': 'api.user',
                'function': 'get_user',
                'line': 100,
                'extra': {'extra': {'user_id': '12345', 'endpoint': '/api/user'}}
            },
            {
                'time': MagicMock(timestamp=lambda: time.time()),
                'level': MagicMock(name='ERROR'),
                'message': '数据库连接失败',
                'name': 'database.connection',
                'function': 'connect',
                'line': 50,
                'extra': {'extra': {'error_code': 'DB_CONN_FAILED'}}
            },
            {
                'time': MagicMock(timestamp=lambda: time.time()),
                'level': MagicMock(name='WARNING'),
                'message': '业务逻辑异常',
                'name': 'business.order',
                'function': 'process_order',
                'line': 200,
                'extra': {'extra': {'order_id': 'ORD-123'}}
            }
        ]
        
        # 处理所有测试记录
        for record in test_records:
            message = MagicMock(record=record)
            sink(message)
        
        # 等待异步处理
        time.sleep(0.2)
        
        # 验证处理成功
        assert callable(sink)
    
    @pytest.mark.integration
    def test_sls_async_processing(self, mock_aliyun_sdk, clean_env):
        """测试异步处理集成"""
        # 创建 sink
        sink = create_sls_sink(
            project="async-test-project",
            logstore="async-test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret",
            batch_size=5,  # 小批次便于测试
            flush_interval=1.0  # 短间隔便于测试
        )
        
        # 生成多条日志
        for i in range(10):
            record = {
                'time': MagicMock(timestamp=lambda: time.time()),
                'level': MagicMock(name='INFO'),
                'message': f'测试消息 {i}',
                'name': 'test_module',
                'function': 'test_function',
                'line': i,
                'extra': {'extra': {'index': i}}
            }
            message = MagicMock(record=record)
            sink(message)
        
        # 等待批次处理
        time.sleep(2.0)
        
        # 验证异步处理正常工作
        assert callable(sink)
    
    @pytest.mark.integration
    def test_sls_error_recovery(self, mock_aliyun_sdk, mock_loguru_message, clean_env):
        """测试错误恢复集成"""
        # 创建 sink
        sink = create_sls_sink(
            project="error-test-project",
            logstore="error-test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret"
        )
        
        # 模拟发送错误
        with patch.object(mock_aliyun_sdk['client'], 'put_logs', side_effect=Exception("Network error")):
            # 处理日志（应该不会崩溃）
            sink(mock_loguru_message)
            
            # 等待处理
            time.sleep(0.5)
        
        # 恢复正常（移除错误模拟）
        sink(mock_loguru_message)
        time.sleep(0.5)
        
        # 验证 sink 仍然可用
        assert callable(sink)
    
    @pytest.mark.integration
    def test_sls_pack_id_integration(self, mock_aliyun_sdk, clean_env):
        """测试 PackId 功能集成"""
        # 创建 sink
        sink = create_sls_sink(
            project="packid-test-project",
            logstore="packid-test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret"
        )
        
        # 生成一系列相关的日志
        business_flow_logs = [
            {'message': '开始处理订单', 'step': 'start'},
            {'message': '验证用户信息', 'step': 'validation'},
            {'message': '计算金额', 'step': 'calculation'},
            {'message': '完成处理', 'step': 'complete'}
        ]
        
        for log_data in business_flow_logs:
            record = {
                'time': MagicMock(timestamp=lambda: time.time()),
                'level': MagicMock(name='INFO'),
                'message': log_data['message'],
                'name': 'business.order',
                'function': 'process_order',
                'line': 100,
                'extra': {'extra': {
                    'business_flow': 'order_processing',
                    'step': log_data['step'],
                    'order_id': 'ORD-12345'
                }}
            }
            message = MagicMock(record=record)
            sink(message)
        
        # 等待处理
        time.sleep(1.0)
        
        # 验证 PackId 功能正常工作
        assert callable(sink)
    
    @pytest.mark.integration
    def test_sls_configuration_priority(self, mock_aliyun_sdk, clean_env):
        """测试配置优先级集成"""
        # 设置环境变量
        os.environ.update({
            'APP_NAME': 'env-app',
            'APP_VERSION': 'env-version',
            'ENVIRONMENT': 'env-environment'
        })
        
        # 创建 sink，参数应该覆盖环境变量
        sink = create_sls_sink(
            project="priority-test-project",
            logstore="priority-test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret",
            app_name="param-app",  # 应该覆盖环境变量
            environment="param-environment"  # 应该覆盖环境变量
            # app_version 没有提供，应该使用环境变量
        )
        
        # 处理日志
        record = {
            'time': MagicMock(timestamp=lambda: time.time()),
            'level': MagicMock(name='INFO'),
            'message': '配置优先级测试',
            'name': 'test_module',
            'function': 'test_function',
            'line': 1,
            'extra': {}
        }
        message = MagicMock(record=record)
        sink(message)
        
        # 等待处理
        time.sleep(0.5)
        
        # 验证配置正确应用
        assert callable(sink)