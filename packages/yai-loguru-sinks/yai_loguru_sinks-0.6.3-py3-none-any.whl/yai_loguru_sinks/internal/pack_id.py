"""
阿里云 SLS PackId 管理器

提供 PackId 生成和管理功能，用于关联日志上下文。
PackId 格式: {context_prefix}-{log_group_id}
"""

import os
import time
import hashlib
import threading
from typing import Optional


class PackIdGenerator:
    """PackId 生成器
    
    PackId 格式: {context_prefix}-{log_group_id}
    - context_prefix: 上下文前缀，用于关联相关日志
    - log_group_id: 日志组ID，递增数字
    
    使用场景：
    1. 自动生成：每个应用实例自动生成唯一的上下文前缀
    2. 手动指定：可以手动指定上下文前缀，用于特定的日志分组
    """
    
    def __init__(self, context_prefix: Optional[str] = None) -> None:
        """初始化 PackId 生成器
        
        Args:
            context_prefix: 自定义上下文前缀，为空时自动生成
        """
        self.context_prefix = context_prefix or self._generate_context_prefix()
        self.log_group_counter = 0
        self._lock = threading.Lock()
    
    def _generate_context_prefix(self) -> str:
        """生成上下文前缀
        
        使用机器标识 + 进程ID + 时间戳的组合，确保唯一性
        格式：8位MD5哈希值
        
        Returns:
            8位字符串作为上下文前缀
        """
        import socket
        
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = "unknown"
        
        pid = os.getpid()
        timestamp = int(time.time() * 1000)  # 毫秒时间戳
        
        # 生成短哈希作为前缀
        raw_data = f"{hostname}-{pid}-{timestamp}"
        hash_obj = hashlib.md5(raw_data.encode())
        return hash_obj.hexdigest()[:8]
    
    def next_pack_id(self) -> str:
        """生成下一个 PackId
        
        线程安全的递增计数器，确保每个 PackId 唯一
        
        Returns:
            格式为 {context_prefix}-{log_group_id} 的 PackId
        """
        with self._lock:
            self.log_group_counter += 1
            return f"{self.context_prefix}-{self.log_group_counter:06d}"
    
    def get_context_prefix(self) -> str:
        """获取当前上下文前缀
        
        Returns:
            当前的上下文前缀
        """
        return self.context_prefix
    
    def reset_counter(self) -> None:
        """重置计数器
        
        注意：这会导致 PackId 重复，仅在特殊情况下使用
        """
        with self._lock:
            self.log_group_counter = 0
    
    def get_current_count(self) -> int:
        """获取当前计数器值
        
        Returns:
            当前的日志组计数
        """
        with self._lock:
            return self.log_group_counter


def create_pack_id_generator(context_prefix: Optional[str] = None) -> PackIdGenerator:
    """创建 PackId 生成器的工厂函数
    
    Args:
        context_prefix: 自定义上下文前缀，为空时自动生成
    
    Returns:
        PackIdGenerator 实例
    """
    return PackIdGenerator(context_prefix)


# 全局默认生成器（可选使用）
_default_generator: Optional[PackIdGenerator] = None


def get_default_generator() -> PackIdGenerator:
    """获取全局默认的 PackId 生成器
    
    单例模式，确保整个应用使用同一个生成器
    
    Returns:
        全局默认的 PackIdGenerator 实例
    """
    global _default_generator
    if _default_generator is None:
        _default_generator = PackIdGenerator()
    return _default_generator


def generate_pack_id() -> str:
    """使用默认生成器生成 PackId
    
    便捷函数，直接生成 PackId
    
    Returns:
        新的 PackId
    """
    return get_default_generator().next_pack_id()