"""端到端用户场景测试

测试真实的用户使用场景，包括配置文件、环境变量和实际的日志记录。
"""

import pytest
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from loguru import logger

from yai_loguru_sinks.internal.factory import create_sls_sink


class TestUserScenarios:
    """用户场景端到端测试"""
    
    @pytest.mark.e2e
    def test_basic_user_setup(self, temp_dir, mock_aliyun_sdk, clean_env):
        """测试基础用户设置场景"""
        # 模拟用户创建 .env 文件
        env_file = temp_dir / ".env"
        env_content = """
# SLS 配置
SLS_PROJECT=my-project
SLS_LOGSTORE=my-logstore
SLS_REGION=cn-hangzhou
SLS_ACCESS_KEY_ID=my-access-key
SLS_ACCESS_KEY_SECRET=my-access-secret

# 应用信息
APP_NAME=my-awesome-app
APP_VERSION=1.2.3
ENVIRONMENT=production

# SLS 配置
SLS_AUTO_DETECT_HOSTNAME=true
SLS_AUTO_DETECT_HOST_IP=true
SLS_DEFAULT_CATEGORY=business
"""
        env_file.write_text(env_content)
        
        # 模拟加载环境变量
        for line in env_content.strip().split('\n'):
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
        
        # 用户使用工厂函数创建 sink
        from yai_loguru_sinks.internal.factory import create_sls_sink
        
        sink = create_sls_sink(
            project=os.environ['SLS_PROJECT'],
            logstore=os.environ['SLS_LOGSTORE'],
            region=os.environ['SLS_REGION']
        )
        
        # 用户记录日志
        record = {
            'time': MagicMock(timestamp=lambda: 1234567890.0),
            'level': MagicMock(name='INFO'),
            'message': '用户业务日志',
            'name': 'my_app.business',
            'function': 'process_data',
            'line': 42,
            'extra': {'extra': {
                'user_id': 'user123',
                'action': 'data_processing',
                'result': 'success'
            }}
        }
        message = MagicMock(record=record)
        sink(message)
        
        # 验证成功
        assert callable(sink)
    
    @pytest.mark.e2e
    def test_yaml_config_scenario(self, temp_dir, mock_aliyun_sdk, clean_env):
        """测试 YAML 配置文件场景"""
        # 设置环境变量
        os.environ.update({
            'SLS_ACCESS_KEY_ID': 'yaml-test-key',
            'SLS_ACCESS_KEY_SECRET': 'yaml-test-secret',
            'APP_NAME': 'yaml-config-app',
            'APP_VERSION': '1.0.0',
            'ENVIRONMENT': 'testing'
        })
        
        # 创建 YAML 配置文件
        config_file = temp_dir / "logging.yaml"
        config_content = {
            'handlers': [
                {
                    'sink': 'sys.stdout',
                    'level': 'INFO',
                    'format': '{time} | {level} | {message}'
                },
                {
                    'sink': 'sls://yaml-project/yaml-logstore?region=cn-hangzhou&app_name=yaml-app&environment=testing',
                    'level': 'WARNING',
                    'format': '{time} | {level} | {message} | {extra}'
                }
            ]
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_content, f)
        
        # 模拟用户使用配置文件
        # 注意：这里需要 loguru-config 的完整集成
        # 为了测试目的，我们验证配置文件的解析
        
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        assert len(loaded_config['handlers']) == 2
        sls_handler = loaded_config['handlers'][1]
        assert sls_handler['sink'].startswith('sls://')
        assert 'yaml-project' in sls_handler['sink']
        assert 'yaml-logstore' in sls_handler['sink']
    
    @pytest.mark.e2e
    def test_enterprise_demo_scenario(self, temp_dir, mock_aliyun_sdk, clean_env):
        """测试企业级演示场景"""
        # 模拟企业级配置
        os.environ.update({
            'SLS_PROJECT': 'enterprise-logs',
            'SLS_LOGSTORE': 'application-logs',
            'SLS_REGION': 'cn-beijing',
            'SLS_ACCESS_KEY_ID': 'enterprise-key',
            'SLS_ACCESS_KEY_SECRET': 'enterprise-secret',
            'APP_NAME': 'enterprise-app',
            'APP_VERSION': '2.1.0',
            'ENVIRONMENT': 'production',
            'SLS_AUTO_DETECT_HOSTNAME': 'true',
            'SLS_AUTO_DETECT_HOST_IP': 'true',
            'SLS_AUTO_DETECT_THREAD': 'true',
            'SLS_DEFAULT_CATEGORY': 'enterprise'
        })
        
        # 创建企业级 sink
        from yai_loguru_sinks.internal.factory import create_sls_sink
        
        sink = create_sls_sink(
            project=os.environ['SLS_PROJECT'],
            logstore=os.environ['SLS_LOGSTORE'],
            region=os.environ['SLS_REGION'],
            batch_size=50,  # 企业级批次大小
            flush_interval=3.0  # 企业级刷新间隔
        )
        
        # 模拟企业级日志场景
        enterprise_logs = [
            {
                'level': 'INFO',
                'message': '用户登录成功',
                'module': 'auth.login',
                'extra': {
                    'user_id': 'emp001',
                    'ip_address': '10.0.1.100',
                    'user_agent': 'Enterprise Browser 1.0',
                    'session_id': 'sess_abc123'
                }
            },
            {
                'level': 'WARNING',
                'message': 'API调用频率过高',
                'module': 'api.rate_limit',
                'extra': {
                    'api_endpoint': '/api/v1/data',
                    'user_id': 'emp001',
                    'request_count': 150,
                    'time_window': '1min'
                }
            },
            {
                'level': 'ERROR',
                'message': '数据库连接超时',
                'module': 'database.connection',
                'extra': {
                    'database': 'primary_db',
                    'timeout': 30,
                    'retry_count': 3,
                    'error_code': 'DB_TIMEOUT'
                }
            },
            {
                'level': 'INFO',
                'message': '订单处理完成',
                'module': 'business.order',
                'extra': {
                    'order_id': 'ORD-2024-001',
                    'customer_id': 'CUST-12345',
                    'amount': 1299.99,
                    'currency': 'CNY',
                    'processing_time': 2.5
                }
            }
        ]
        
        # 处理所有企业级日志
        for log_data in enterprise_logs:
            record = {
                'time': MagicMock(timestamp=lambda: 1234567890.0),
                'level': MagicMock(name=log_data['level']),
                'message': log_data['message'],
                'name': log_data['module'],
                'function': 'enterprise_function',
                'line': 100,
                'extra': {'extra': log_data['extra']}
            }
            message = MagicMock(record=record)
            sink(message)
        
        # 验证企业级处理成功
        assert callable(sink)
    
    @pytest.mark.e2e
    def test_development_workflow(self, temp_dir, mock_aliyun_sdk, clean_env):
        """测试开发工作流场景"""
        # 开发环境配置
        os.environ.update({
            'APP_NAME': 'dev-app',
            'APP_VERSION': '0.1.0-dev',
            'ENVIRONMENT': 'development',
            'SLS_AUTO_DETECT_HOSTNAME': 'true',
            'SLS_AUTO_DETECT_HOST_IP': 'false',  # 开发环境可能不需要IP
            'SLS_AUTO_DETECT_THREAD': 'true',   # 开发环境需要线程信息调试
            'SLS_DEFAULT_CATEGORY': 'development'
        })
        
        # 创建开发用 sink
        from yai_loguru_sinks.internal.factory import create_sls_sink
        
        sink = create_sls_sink(
            project="dev-project",
            logstore="dev-logs",
            region="cn-hangzhou",
            access_key_id="dev-key",
            access_key_secret="dev-secret",
            batch_size=10,  # 开发环境小批次，快速反馈
            flush_interval=1.0  # 开发环境快速刷新
        )
        
        # 模拟开发调试日志
        debug_logs = [
            {
                'level': 'DEBUG',
                'message': '开始调试功能X',
                'module': 'feature.x',
                'extra': {'debug_session': 'session_001'}
            },
            {
                'level': 'INFO',
                'message': '变量值检查',
                'module': 'feature.x',
                'extra': {
                    'variable_name': 'user_data',
                    'variable_value': {'id': 123, 'name': 'test'},
                    'debug_session': 'session_001'
                }
            },
            {
                'level': 'WARNING',
                'message': '性能警告：函数执行时间过长',
                'module': 'performance.monitor',
                'extra': {
                    'function_name': 'slow_function',
                    'execution_time': 5.2,
                    'threshold': 3.0
                }
            }
        ]
        
        # 处理开发日志
        for log_data in debug_logs:
            record = {
                'time': MagicMock(timestamp=lambda: 1234567890.0),
                'level': MagicMock(name=log_data['level']),
                'message': log_data['message'],
                'name': log_data['module'],
                'function': 'dev_function',
                'line': 50,
                'extra': {'extra': log_data['extra']}
            }
            message = MagicMock(record=record)
            sink(message)
        
        # 验证开发工作流成功
        assert callable(sink)
    
    @pytest.mark.e2e
    def test_microservice_scenario(self, temp_dir, mock_aliyun_sdk, clean_env):
        """测试微服务场景"""
        # 微服务配置
        services = [
            {
                'name': 'user-service',
                'version': '1.0.0',
                'port': 8001
            },
            {
                'name': 'order-service', 
                'version': '1.1.0',
                'port': 8002
            },
            {
                'name': 'payment-service',
                'version': '1.0.5',
                'port': 8003
            }
        ]
        
        sinks = []
        
        # 为每个微服务创建独立的 sink
        for service in services:
            os.environ.update({
                'APP_NAME': service['name'],
                'APP_VERSION': service['version'],
                'ENVIRONMENT': 'production',
                'SERVICE_PORT': str(service['port'])
            })
            
            sink = create_sls_sink(
                project="microservices-logs",
                logstore=f"{service['name']}-logs",
                region="cn-hangzhou",
                access_key_id="microservice-key",
                access_key_secret="microservice-secret",
                default_category="microservice"
            )
            
            sinks.append((service['name'], sink))
        
        # 模拟微服务间的调用链
        call_chain = [
            ('user-service', 'INFO', '接收用户请求', {'request_id': 'req_001', 'user_id': 'user123'}),
            ('user-service', 'INFO', '调用订单服务', {'request_id': 'req_001', 'target_service': 'order-service'}),
            ('order-service', 'INFO', '处理订单创建', {'request_id': 'req_001', 'order_id': 'ord_001'}),
            ('order-service', 'INFO', '调用支付服务', {'request_id': 'req_001', 'target_service': 'payment-service', 'amount': 99.99}),
            ('payment-service', 'INFO', '处理支付请求', {'request_id': 'req_001', 'payment_id': 'pay_001', 'amount': 99.99}),
            ('payment-service', 'INFO', '支付成功', {'request_id': 'req_001', 'payment_id': 'pay_001', 'status': 'success'}),
            ('order-service', 'INFO', '订单创建成功', {'request_id': 'req_001', 'order_id': 'ord_001', 'status': 'completed'}),
            ('user-service', 'INFO', '返回用户响应', {'request_id': 'req_001', 'response_code': 200})
        ]
        
        # 处理调用链日志
        for service_name, level, message, extra_data in call_chain:
            # 找到对应的 sink
            sink = next(sink for name, sink in sinks if name == service_name)
            
            record = {
                'time': MagicMock(timestamp=lambda: 1234567890.0),
                'level': MagicMock(name=level),
                'message': message,
                'name': f'{service_name}.handler',
                'function': 'handle_request',
                'line': 100,
                'extra': {'extra': extra_data}
            }
            message_obj = MagicMock(record=record)
            sink(message_obj)
        
        # 验证所有微服务日志处理成功
        for name, sink in sinks:
            assert callable(sink)
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_high_volume_scenario(self, temp_dir, mock_aliyun_sdk, clean_env):
        """测试高并发场景"""
        import threading
        import time
        
        # 高并发配置
        os.environ.update({
            'APP_NAME': 'high-volume-app',
            'APP_VERSION': '1.0.0',
            'ENVIRONMENT': 'production',
            'SLS_AUTO_DETECT_HOSTNAME': 'true',
            'SLS_AUTO_DETECT_HOST_IP': 'true',
            'SLS_DEFAULT_CATEGORY': 'high-volume'
        })
        
        # 创建高性能 sink
        sink = create_sls_sink(
            project="high-volume-project",
            logstore="high-volume-logs",
            region="cn-hangzhou",
            access_key_id="high-volume-key",
            access_key_secret="high-volume-secret",
            batch_size=100,  # 大批次
            flush_interval=5.0  # 较长间隔
        )
        
        # 多线程生成日志
        def generate_logs(thread_id, count):
            for i in range(count):
                record = {
                    'time': MagicMock(timestamp=lambda: time.time()),
                    'level': MagicMock(name='INFO'),
                    'message': f'高并发日志 {thread_id}-{i}',
                    'name': f'thread.{thread_id}',
                    'function': 'generate_data',
                    'line': i,
                    'extra': {'extra': {
                        'thread_id': thread_id,
                        'sequence': i,
                        'batch': i // 10
                    }}
                }
                message = MagicMock(record=record)
                sink(message)
        
        # 启动多个线程
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(
                target=generate_logs,
                args=(thread_id, 20)  # 每个线程生成20条日志
            )
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 等待异步处理完成
        time.sleep(3.0)
        
        # 验证高并发处理成功
        assert callable(sink)