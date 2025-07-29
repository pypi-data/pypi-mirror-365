import time
from typing import Dict, Any, List

class AuditLog:
    """审计日志管理器，记录系统安全相关事件"""
    
    def __init__(self, storage):
        """
        初始化审计日志管理器
        
        参数:
            storage: 存储适配器实例
        """
        self.storage = storage
    
    def log_event(self, 
                 event_type: str, 
                 user_id: str = None, 
                 message: str = None,
                 metadata: Dict[str, Any] = None) -> None:
        """
        记录审计事件
        
        参数:
            event_type: 事件类型
            user_id: 用户ID(可选)
            message: 事件消息(可选)
            metadata: 事件元数据(可选)
        """
        # 构建审计日志条目
        log_entry = {
            "id": self.storage.generate_id("audit"),
            "timestamp": int(time.time()),
            "event_type": event_type,
            "user_id": user_id,
            "message": message,
            "metadata": metadata or {}
        }
        
        # 保存日志条目
        self.storage.save_audit_log(log_entry)
    
    def get_events(self, 
                  event_type: str = None, 
                  user_id: str = None,
                  start_time: int = None,
                  end_time: int = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取审计事件
        
        参数:
            event_type: 事件类型(可选)
            user_id: 用户ID(可选)
            start_time: 开始时间戳(可选)
            end_time: 结束时间戳(可选)
            limit: 返回结果数量限制(可选)
            
        返回:
            符合条件的审计事件列表
        """
        # 获取所有审计日志
        all_logs = self.storage.get_audit_logs()
        
        # 过滤日志
        filtered_logs = []
        
        for log in all_logs:
            # 应用过滤器
            if event_type and log["event_type"] != event_type:
                continue
                
            if user_id and log["user_id"] != user_id:
                continue
                
            if start_time and log["timestamp"] < start_time:
                continue
                
            if end_time and log["timestamp"] > end_time:
                continue
                
            filtered_logs.append(log)
        
        # 按时间降序排序
        sorted_logs = sorted(filtered_logs, key=lambda x: x["timestamp"], reverse=True)
        
        # 应用限制
        return sorted_logs[:limit]    