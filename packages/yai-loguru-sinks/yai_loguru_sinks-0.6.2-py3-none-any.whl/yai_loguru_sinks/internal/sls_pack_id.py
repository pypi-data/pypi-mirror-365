"""
SLS Sink 的 PackId 扩展

为 SLS Sink 提供 PackId 支持，默认启用固定 PackId。
"""

from .pack_id import PackIdGenerator


class SlsPackIdManager:
    """SLS PackId 管理器
    
    简化版本：
    - 默认启用 PackId 功能
    - 在初始化时生成一个固定的 PackId
    - 整个 sink 生命周期内使用同一个 PackId
    """
    
    def __init__(self) -> None:
        """初始化 PackId 管理器，生成固定的 PackId"""
        self.generator = PackIdGenerator()
        self.fixed_pack_id = self.generator.next_pack_id()
    
    def get_context_prefix(self) -> str:
        """获取上下文前缀"""
        return self.generator.get_context_prefix()
    
    def get_batch_pack_id(self) -> str:
        """获取固定的 PackId
        
        Returns:
            固定的 PackId，整个 sink 生命周期内不变
        """
        return self.fixed_pack_id


def create_pack_id_manager() -> SlsPackIdManager:
    """创建 SLS PackId 管理器的工厂函数"""
    return SlsPackIdManager()