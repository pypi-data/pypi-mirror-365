"""
SLS Sink 核心实现

包含 SlsSink 主体类，负责初始化、日志处理和关闭逻辑。
"""

import threading
from typing import Any
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
        self.pack_id_manager = create_pack_id_manager(
            enable_pack_id=config.enable_pack_id,
            context_prefix=config.context_prefix,
            pack_id_per_batch=config.pack_id_per_batch,
            pack_id_per_message=config.pack_id_per_message
        )
        
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
            
            # 构造日志数据
            log_data = {
                'timestamp': record['time'].timestamp(),
                'level': record['level'].name,
                'message': str(record['message']),
                'module': record.get('name', ''),
                'function': record.get('function', ''),
                'line': record.get('line', 0),
            }
            
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