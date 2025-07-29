"""
SLS Sink 的 PackId 扩展

为 SLS Sink 提供 PackId 支持，包括配置和集成逻辑。
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .pack_id import PackIdGenerator


@dataclass
class SlsPackIdConfig:
    """SLS PackId 配置"""
    
    # PackId 功能开关
    enable_pack_id: bool = True
    
    # 上下文前缀配置
    context_prefix: Optional[str] = None
    
    # PackId 策略配置
    pack_id_per_batch: bool = True  # 每批次一个 PackId
    pack_id_per_message: bool = False  # 每条消息一个 PackId（性能较低）


class SlsPackIdManager:
    """SLS PackId 管理器
    
    负责为 SLS Sink 提供 PackId 生成和管理功能
    """
    
    def __init__(self, config: SlsPackIdConfig) -> None:
        """初始化 PackId 管理器
        
        Args:
            config: PackId 配置
        """
        self.config = config
        self.generator: Optional[PackIdGenerator] = None
        
        if config.enable_pack_id:
            self.generator = PackIdGenerator(config.context_prefix)
    
    def is_enabled(self) -> bool:
        """检查 PackId 功能是否启用
        
        Returns:
            是否启用 PackId
        """
        return self.config.enable_pack_id and self.generator is not None
    
    def get_context_prefix(self) -> Optional[str]:
        """获取上下文前缀
        
        Returns:
            上下文前缀，如果未启用则返回 None
        """
        if self.generator:
            return self.generator.get_context_prefix()
        return None
    
    def generate_pack_id(self) -> Optional[str]:
        """生成新的 PackId
        
        Returns:
            新的 PackId，如果未启用则返回 None
        """
        if self.generator:
            return self.generator.next_pack_id()
        return None
    
    def enhance_log_data(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """增强日志数据，添加 PackId 相关字段
        
        Args:
            log_data: 原始日志数据
            
        Returns:
            增强后的日志数据
        """
        if not self.is_enabled():
            return log_data
        
        enhanced_data = log_data.copy()
        
        # 添加上下文前缀
        context_prefix = self.get_context_prefix()
        if context_prefix:
            enhanced_data['context_prefix'] = context_prefix
        
        # 如果配置为每条消息一个 PackId，则在这里生成
        if self.config.pack_id_per_message:
            pack_id = self.generate_pack_id()
            if pack_id:
                enhanced_data['__pack_id__'] = pack_id
        
        return enhanced_data
    
    def enhance_log_contents(self, contents: List[tuple], pack_id: Optional[str] = None) -> List[tuple]:
        """增强日志内容，添加 PackId 相关字段
        
        Args:
            contents: 原始日志内容列表
            pack_id: 可选的 PackId，如果提供则使用，否则可能从配置生成
            
        Returns:
            增强后的日志内容列表
        """
        if not self.is_enabled():
            return contents
        
        enhanced_contents = contents.copy()
        
        # 添加 PackId
        if pack_id:
            enhanced_contents.append(('__pack_id__', pack_id))
        
        # 添加上下文前缀
        context_prefix = self.get_context_prefix()
        if context_prefix:
            enhanced_contents.append(('context_prefix', context_prefix))
        
        return enhanced_contents
    
    def get_batch_pack_id(self) -> Optional[str]:
        """获取批次级别的 PackId
        
        当配置为每批次一个 PackId 时使用
        
        Returns:
            批次 PackId，如果未启用或不是批次模式则返回 None
        """
        if not self.is_enabled() or not self.config.pack_id_per_batch:
            return None
        
        return self.generate_pack_id()


def create_pack_id_manager(
    enable_pack_id: bool = True,
    context_prefix: Optional[str] = None,
    pack_id_per_batch: bool = True,
    pack_id_per_message: bool = False
) -> SlsPackIdManager:
    """创建 SLS PackId 管理器的工厂函数
    
    Args:
        enable_pack_id: 是否启用 PackId 功能
        context_prefix: 自定义上下文前缀
        pack_id_per_batch: 每批次一个 PackId
        pack_id_per_message: 每条消息一个 PackId
        
    Returns:
        SlsPackIdManager 实例
    """
    config = SlsPackIdConfig(
        enable_pack_id=enable_pack_id,
        context_prefix=context_prefix,
        pack_id_per_batch=pack_id_per_batch,
        pack_id_per_message=pack_id_per_message
    )
    
    return SlsPackIdManager(config)