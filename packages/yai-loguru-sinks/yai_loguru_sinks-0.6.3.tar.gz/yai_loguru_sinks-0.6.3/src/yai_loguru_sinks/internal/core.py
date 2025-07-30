"""
SLS Sink 核心实现

包含 SlsSink 主体类，负责初始化、日志处理和关闭逻辑。
"""

import threading
import socket
from typing import Any, Dict
from queue import Queue, Empty

try:
    from aliyun.log import LogClient  # type: ignore
    HAS_ALIYUN_SDK = True
except ImportError:
    HAS_ALIYUN_SDK = False
    LogClient = None

from .data import SlsConfig
from .async_handler import AsyncHandler
from .sls_pack_id import create_pack_id_manager


class SlsSink:
    """SLS Sink 实现类"""
    
    def __init__(self, config: SlsConfig) -> None:
        if not HAS_ALIYUN_SDK:
            raise ImportError(
                "阿里云 SDK 未安装，请运行: uv add aliyun-log-python-sdk"
            )
        
        self.config = config
        self.client = LogClient(
            config.endpoint,
            config.access_key_id,
            config.access_key_secret
        )
        
        # 初始化 PackId 管理器
        self.pack_id_manager = create_pack_id_manager()
        
        # 初始化队列和异步处理器
        self.log_queue: Queue = Queue()
        self.stop_event = threading.Event()
        self.async_handler = AsyncHandler(self)
        
        # 启动后台线程
        self.flush_thread = threading.Thread(
            target=self.async_handler.flush_worker, 
            daemon=True
        )
        self.flush_thread.start()
    
    def __call__(self, message: Any) -> None:
        """Loguru sink 调用接口"""
        try:
            record = message.record
            
            # 基础字段映射
            log_data = {
                'timestamp': record['time'].timestamp(),
                'level': record['level'].name,
                'message': str(record['message']),
                'module': record.get('name', ''),
                'function': record.get('function', ''),
                'line': record.get('line', 0),
                
                # 新增必需字段
                'app_name': self.config.app_name,
                'version': self.config.app_version,
                'environment': self.config.environment,
                'category': self._get_log_category(record),
            }
            
            # 自动检测系统信息
            if self.config.auto_detect_hostname:
                log_data['hostname'] = self._get_hostname()
            
            if self.config.auto_detect_host_ip:
                log_data['host_ip'] = self._get_host_ip()
                
            if self.config.auto_detect_thread:
                log_data['thread'] = self._get_thread_info(record)
            
            # 处理 extra 字段 - loguru 将 extra 参数存储在 record['extra']['extra'] 中
            record_extra = record.get('extra', {})
            if 'extra' in record_extra and record_extra['extra']:
                log_data['extra'] = record_extra['extra']
            
            self.log_queue.put(log_data)
                
        except Exception as e:
            # 避免日志处理错误影响主程序
            print(f"SLS日志处理错误: {e}")
    
    def close(self) -> None:
        """关闭 sink，发送剩余日志"""
        self.stop_event.set()
        
        if self.flush_thread.is_alive():
            self.flush_thread.join(timeout=5.0)
        
        # 发送剩余的日志
        self.async_handler.flush_remaining_logs()
    
    def _get_hostname(self) -> str:
        """获取主机名"""
        try:
            return socket.gethostname()
        except Exception:
            return "unknown-host"
    
    def _get_host_ip(self) -> str:
        """获取主机IP"""
        try:
            # 获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "unknown-ip"
    
    def _get_thread_info(self, record: Dict[str, Any]) -> str:
        """获取线程信息"""
        try:
            thread_name = threading.current_thread().name
            thread_id = threading.get_ident()
            return f"{thread_name}({thread_id})"
        except Exception:
            return "unknown-thread"
    
    def _get_log_category(self, record: Dict[str, Any]) -> str:
        """获取日志分类"""
        # 可以根据模块名、级别等自动分类
        module_name = record.get('name', '')
        level = record['level'].name
        
        # 简单的分类逻辑
        if 'error' in level.lower() or 'exception' in str(record.get('message', '')).lower():
            return "error"
        elif 'api' in module_name.lower():
            return "api"
        elif 'business' in module_name.lower():
            return "business"
        else:
            return self.config.default_category