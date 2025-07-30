"""
SLS 异步处理模块

包含后台工作线程和消息发送逻辑。
"""

import time
from typing import Dict, Any, List
from queue import Empty

try:
    from aliyun.log.logitem import LogItem  # type: ignore
    from aliyun.log.putlogsrequest import PutLogsRequest  # type: ignore
    HAS_ALIYUN_SDK = True
except ImportError:
    HAS_ALIYUN_SDK = False
    LogItem = None
    PutLogsRequest = None


class AsyncHandler:
    """异步处理器，负责后台工作线程和消息发送"""
    
    def __init__(self, sink_instance: Any) -> None:
        """初始化异步处理器
        
        Args:
            sink_instance: SlsSink 实例的引用
        """
        self.sink = sink_instance
    
    def flush_worker(self) -> None:
        """后台线程工作函数，定期刷新日志"""
        messages = []
        
        while not self.sink.stop_event.is_set():
            try:
                # 收集消息
                try:
                    # 等待消息或超时
                    message = self.sink.log_queue.get(timeout=self.sink.config.flush_interval)
                    
                    messages.append(message)
                    
                    # 继续收集直到批量大小或队列为空
                    while len(messages) < self.sink.config.batch_size:
                        try:
                            message = self.sink.log_queue.get_nowait()
                            messages.append(message)
                        except Empty:
                            break
                            
                except Empty:
                    # 超时，如果有消息就发送
                    pass
                
                # 发送消息
                if messages:
                    self.send_messages(messages)
                    messages.clear()
                    
            except Exception as e:
                print(f"SLS刷新工作线程错误: {e}")
                time.sleep(1)  # 避免错误循环
    
    def send_messages(self, messages: List[Dict[str, Any]]) -> None:
        """发送消息到SLS"""
        if not messages:
            return
        
        try:
            # 获取批次级别的 PackId
            batch_pack_id = self.sink.pack_id_manager.get_batch_pack_id()
            
            # 转换为SLS LogItem格式
            log_items = []
            for msg in messages:
                # 构建日志内容 - 包含所有字段
                contents = [
                    ('level', msg['level']),
                    ('message', msg['message']),
                    ('module', msg['module']),
                    ('function', msg['function']),
                    ('line', str(msg['line'])),
                    # 新增的必需字段
                    ('app_name', msg.get('app_name', '')),
                    ('version', msg.get('version', '')),
                    ('environment', msg.get('environment', '')),
                    ('category', msg.get('category', '')),
                ]
                
                # 添加可选的系统信息字段
                if 'hostname' in msg:
                    contents.append(('hostname', msg['hostname']))
                if 'host_ip' in msg:
                    contents.append(('host_ip', msg['host_ip']))
                if 'thread' in msg:
                    contents.append(('thread', msg['thread']))
                
                # 添加 extra 字段（如果存在）
                if 'extra' in msg and msg['extra']:
                    import json
                    contents.append(('extra', json.dumps(msg['extra'], ensure_ascii=False)))
                
                log_item = LogItem()
                log_item.set_time(int(msg['timestamp']))
                log_item.set_contents(contents)
                log_items.append(log_item)
            
            # 准备 LogTags - PackId 应该放在这里
            logtags = []
            if batch_pack_id:
                logtags.append(('__pack_id__', batch_pack_id))
            
            # 创建请求 - 添加 logtags 参数
            request = PutLogsRequest(
                project=self.sink.config.project,
                logstore=self.sink.config.logstore,
                topic=self.sink.config.topic,
                source=self.sink.config.source,
                logitems=log_items,
                compress=self.sink.config.compress,
                logtags=logtags if logtags else None
            )
            
            # 发送到SLS
            response = self.sink.client.put_logs(request)
            
            # 注意：put_logs 如果成功不会抛出异常，失败会抛出 LogException
            # 所以这里不需要检查 is_success()，能执行到这里说明发送成功
                
        except Exception as e:
            print(f"SLS消息发送错误: {e}")
    
    def flush_remaining_logs(self) -> None:
        """发送剩余的日志"""
        messages = []
        try:
            while not self.sink.log_queue.empty():
                message = self.sink.log_queue.get_nowait()
                enhanced_message = self.sink.pack_id_manager.enhance_log_data(message)
                messages.append(enhanced_message)
        except Empty:
            pass
        
        if messages:
            self.send_messages(messages)