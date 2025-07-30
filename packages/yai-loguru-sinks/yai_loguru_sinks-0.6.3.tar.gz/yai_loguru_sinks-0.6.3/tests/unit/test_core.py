"""测试核心 SlsSink 类

测试 SlsSink 类的核心功能，包括日志处理、字段映射和系统信息检测。
"""

import pytest
import threading
from unittest.mock import patch, MagicMock
from yai_loguru_sinks.internal.core import SlsSink
from yai_loguru_sinks.internal.data import SlsConfig


class TestSlsSink:
    """测试 SlsSink 核心类"""
    
    @pytest.fixture
    def sls_config(self):
        """SLS 配置 fixture"""
        return SlsConfig(
            endpoint="https://test.log.aliyuncs.com",
            access_key_id="test_key",
            access_key_secret="test_secret",
            project="test_project",
            logstore="test_logstore",
            app_name="test-app",
            app_version="1.0.0",
            environment="testing",
            auto_detect_hostname=True,
            auto_detect_host_ip=True,
            auto_detect_thread=True,
            default_category="test"
        )
    
    @pytest.mark.unit
    def test_sls_sink_initialization(self, sls_config, mock_aliyun_sdk):
        """测试 SlsSink 初始化"""
        sink = SlsSink(sls_config)
        
        assert sink.config == sls_config
        assert sink.client is not None
        assert sink.pack_id_manager is not None
        assert sink.log_queue is not None
        assert sink.stop_event is not None
        assert sink.async_handler is not None
        assert sink.flush_thread is not None
        assert sink.flush_thread.daemon is True
    
    @pytest.mark.unit
    def test_sls_sink_without_aliyun_sdk(self, sls_config):
        """测试没有阿里云SDK时的错误处理"""
        with patch('yai_loguru_sinks.internal.core.HAS_ALIYUN_SDK', False):
            with pytest.raises(ImportError, match="阿里云 SDK 未安装"):
                SlsSink(sls_config)
    
    @pytest.mark.unit
    def test_get_hostname(self, sls_config, mock_aliyun_sdk, mock_socket):
        """测试获取主机名"""
        sink = SlsSink(sls_config)
        hostname = sink._get_hostname()
        
        assert hostname == "test-hostname"
    
    @pytest.mark.unit
    def test_get_hostname_error(self, sls_config, mock_aliyun_sdk):
        """测试获取主机名失败的情况"""
        with patch('socket.gethostname', side_effect=Exception("Network error")):
            sink = SlsSink(sls_config)
            hostname = sink._get_hostname()
            
            assert hostname == "unknown-host"
    
    @pytest.mark.unit
    def test_get_host_ip(self, sls_config, mock_aliyun_sdk, mock_socket):
        """测试获取主机IP"""
        sink = SlsSink(sls_config)
        host_ip = sink._get_host_ip()
        
        assert host_ip == "192.168.1.100"
    
    @pytest.mark.unit
    def test_get_host_ip_error(self, sls_config, mock_aliyun_sdk):
        """测试获取主机IP失败的情况"""
        with patch('socket.socket', side_effect=Exception("Network error")):
            sink = SlsSink(sls_config)
            host_ip = sink._get_host_ip()
            
            assert host_ip == "unknown-ip"
    
    @pytest.mark.unit
    def test_get_thread_info(self, sls_config, mock_aliyun_sdk, mock_loguru_record):
        """测试获取线程信息"""
        sink = SlsSink(sls_config)
        
        with patch('threading.current_thread') as mock_thread, \
             patch('threading.get_ident', return_value=12345):
            
            mock_thread.return_value.name = "TestThread"
            thread_info = sink._get_thread_info(mock_loguru_record)
            
            assert thread_info == "TestThread(12345)"
    
    @pytest.mark.unit
    def test_get_thread_info_error(self, sls_config, mock_aliyun_sdk, mock_loguru_record):
        """测试获取线程信息失败的情况"""
        with patch('threading.current_thread', side_effect=Exception("Thread error")):
            sink = SlsSink(sls_config)
            thread_info = sink._get_thread_info(mock_loguru_record)
            
            assert thread_info == "unknown-thread"
    
    @pytest.mark.unit
    def test_get_log_category_error(self, sls_config, mock_aliyun_sdk):
        """测试错误级别的日志分类"""
        sink = SlsSink(sls_config)
        
        # 测试错误级别
        mock_level = MagicMock()
        mock_level.name = 'ERROR'
        record = {
            'name': 'test_module',
            'level': mock_level,
            'message': 'Test error message'
        }
        
        category = sink._get_log_category(record)
        assert category == "error"
    
    @pytest.mark.unit
    def test_get_log_category_api(self, sls_config, mock_aliyun_sdk):
        """测试API模块的日志分类"""
        sink = SlsSink(sls_config)
        
        record = {
            'name': 'api.user',
            'level': MagicMock(name='INFO'),
            'message': 'API call'
        }
        
        category = sink._get_log_category(record)
        assert category == "api"
    
    @pytest.mark.unit
    def test_get_log_category_business(self, sls_config, mock_aliyun_sdk):
        """测试业务模块的日志分类"""
        sink = SlsSink(sls_config)
        
        record = {
            'name': 'business.order',
            'level': MagicMock(name='INFO'),
            'message': 'Business logic'
        }
        
        category = sink._get_log_category(record)
        assert category == "business"
    
    @pytest.mark.unit
    def test_get_log_category_default(self, sls_config, mock_aliyun_sdk):
        """测试默认日志分类"""
        sink = SlsSink(sls_config)
        
        record = {
            'name': 'unknown_module',
            'level': MagicMock(name='INFO'),
            'message': 'Unknown message'
        }
        
        category = sink._get_log_category(record)
        assert category == "test"  # 配置中的 default_category
    
    @pytest.mark.unit
    def test_get_log_category_exception_message(self, sls_config, mock_aliyun_sdk):
        """测试包含异常关键词的消息分类"""
        sink = SlsSink(sls_config)
        
        record = {
            'name': 'test_module',
            'level': MagicMock(name='INFO'),
            'message': 'An exception occurred during processing'
        }
        
        category = sink._get_log_category(record)
        assert category == "error"
    
    @pytest.mark.unit
    def test_call_method_basic(self, sls_config, mock_aliyun_sdk, mock_loguru_message):
        """测试基本的日志处理"""
        sink = SlsSink(sls_config)
        
        # 模拟队列的 put 方法
        with patch.object(sink.log_queue, 'put') as mock_put:
            sink(mock_loguru_message)
            
            # 验证 put 被调用
            mock_put.assert_called_once()
            
            # 获取传递给 put 的参数
            call_args = mock_put.call_args[0][0]
            
            # 验证基本字段
            assert 'timestamp' in call_args
            assert call_args['level'] == 'INFO'
            assert call_args['message'] == '测试日志消息'
            assert call_args['module'] == 'test_module'
            assert call_args['function'] == 'test_function'
            assert call_args['line'] == 42
            
            # 验证新增字段
            assert call_args['app_name'] == 'test-app'
            assert call_args['version'] == '1.0.0'
            assert call_args['environment'] == 'testing'
            assert 'category' in call_args
            
            # 验证自动检测字段
            assert 'hostname' in call_args
            assert 'host_ip' in call_args
            assert 'thread' in call_args
            
            # 验证 extra 字段
            assert 'extra' in call_args
    
    @pytest.mark.unit
    def test_call_method_no_extra(self, sls_config, mock_aliyun_sdk):
        """测试没有 extra 字段的日志处理"""
        sink = SlsSink(sls_config)
        
        # 创建没有 extra 的记录
        record = {
            'time': MagicMock(timestamp=lambda: 1234567890.0),
            'level': MagicMock(name='INFO'),
            'message': '测试消息',
            'name': 'test_module',
            'function': 'test_function',
            'line': 42,
            'extra': {}  # 空的 extra
        }
        
        message = MagicMock(record=record)
        
        with patch.object(sink.log_queue, 'put') as mock_put:
            sink(message)
            
            call_args = mock_put.call_args[0][0]
            
            # extra 字段不应该存在
            assert 'extra' not in call_args
    
    @pytest.mark.unit
    def test_call_method_error_handling(self, sls_config, mock_aliyun_sdk):
        """测试日志处理错误的情况"""
        sink = SlsSink(sls_config)
        
        # 创建会导致错误的消息
        bad_message = MagicMock()
        bad_message.record = None  # 这会导致错误
        
        with patch('builtins.print') as mock_print:
            sink(bad_message)
            
            # 验证错误被捕获并打印
            mock_print.assert_called_once()
            assert "SLS日志处理错误" in str(mock_print.call_args)
    
    @pytest.mark.unit
    def test_close_method(self, sls_config, mock_aliyun_sdk):
        """测试关闭方法"""
        sink = SlsSink(sls_config)
        
        with patch.object(sink.stop_event, 'set') as mock_set, \
             patch.object(sink.flush_thread, 'join') as mock_join, \
             patch.object(sink.async_handler, 'flush_remaining_logs') as mock_flush:
            
            sink.close()
            
            mock_set.assert_called_once()
            mock_join.assert_called_once_with(timeout=5.0)
            mock_flush.assert_called_once()
    
    @pytest.mark.unit
    def test_close_method_thread_timeout(self, sls_config, mock_aliyun_sdk):
        """测试关闭方法中线程超时的情况"""
        sink = SlsSink(sls_config)
        
        with patch.object(sink.flush_thread, 'is_alive', return_value=False), \
             patch.object(sink.async_handler, 'flush_remaining_logs') as mock_flush:
            
            sink.close()
            
            mock_flush.assert_called_once()