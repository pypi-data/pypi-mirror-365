import uuid
import time
from typing import Dict, Any, Optional

class SessionManager:
    """会话管理器，负责创建、验证和管理用户会话"""
    
    def __init__(self, storage, session_lifetime: int = 3600):
        """
        初始化会话管理器
        
        参数:
            storage: 存储适配器实例
            session_lifetime: 会话有效期(秒)
        """
        self.storage = storage
        self.session_lifetime = session_lifetime
    
    def create_session(self, user_id: str, ip_address: str) -> str:
        """
        创建新会话
        
        参数:
            user_id: 用户ID
            ip_address: 客户端IP地址
            
        返回:
            会话令牌
        """
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 创建会话数据
        session = {
            "id": session_id,
            "user_id": user_id,
            "ip_address": ip_address,
            "created_at": int(time.time()),
            "last_activity": int(time.time()),
            "expires_at": int(time.time()) + self.session_lifetime,
            "is_active": True
        }
        
        # 保存会话
        self.storage.save_session(session)
        
        return session_id
    
    def validate_session(self, session_token: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        验证会话有效性
        
        参数:
            session_token: 会话令牌
            ip_address: 客户端IP地址
            
        返回:
            会话数据字典或None
        """
        # 获取会话
        session = self.storage.get_session(session_token)
        
        if not session:
            return None
        
        # 检查会话是否活跃
        if not session.get("is_active", False):
            return None
        
        # 检查IP地址
        if session.get("ip_address") != ip_address:
            return None
        
        # 检查会话是否过期
        current_time = int(time.time())
        if session.get("expires_at", 0) < current_time:
            # 会话已过期，使其无效
            self.invalidate_session(session_token)
            return None
        
        # 更新最后活动时间
        session["last_activity"] = current_time
        self.storage.save_session(session)
        
        return session
    
    def invalidate_session(self, session_token: str) -> None:
        """
        使会话无效
        
        参数:
            session_token: 会话令牌
        """
        # 获取会话
        session = self.storage.get_session(session_token)
        
        if session:
            # 标记会话为无效
            session["is_active"] = False
            self.storage.save_session(session)
    
    def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        获取会话数据
        
        参数:
            session_token: 会话令牌
            
        返回:
            会话数据字典或None
        """
        return self.storage.get_session(session_token)
    
    def refresh_session(self, session_token: str, ip_address: str) -> Optional[str]:
        """
        刷新会话，延长有效期
        
        参数:
            session_token: 会话令牌
            ip_address: 客户端IP地址
            
        返回:
            新的会话令牌或None(如果刷新失败)
        """
        # 验证当前会话
        session = self.validate_session(session_token, ip_address)
        
        if not session:
            return None
        
        # 创建新会话
        new_session_token = self.create_session(
            user_id=session["user_id"],
            ip_address=ip_address
        )
        
        # 使旧会话无效
        self.invalidate_session(session_token)
        
        return new_session_token    