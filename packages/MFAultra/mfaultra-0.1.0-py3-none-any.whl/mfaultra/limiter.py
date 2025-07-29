import time
from typing import Dict, Any, Optional

class LoginAttemptLimiter:
    """登录尝试限制器，防止暴力破解"""
    
    def __init__(self, storage, max_attempts: int = 5, lockout_time: int = 300):
        """
        初始化登录尝试限制器
        
        参数:
            storage: 存储适配器实例
            max_attempts: 最大尝试次数
            lockout_time: 锁定时间(秒)
        """
        self.storage = storage
        self.max_attempts = max_attempts
        self.lockout_time = lockout_time
    
    def record_failed_attempt(self, username: str, ip_address: str) -> None:
        """
        记录失败的登录尝试
        
        参数:
            username: 用户名
            ip_address: 客户端IP地址
        """
        # 获取用户
        user = self.storage.get_user_by_username(username)
        if not user:
            return
        
        user_id = user["id"]
        
        # 获取当前尝试记录
        attempts = self.storage.get_login_attempts(user_id)
        
        # 添加新的失败尝试
        current_time = int(time.time())
        attempts.append({
            "timestamp": current_time,
            "ip_address": ip_address
        })
        
        # 只保留最近的尝试
        recent_attempts = [
            attempt for attempt in attempts 
            if current_time - attempt["timestamp"] <= self.lockout_time
        ]
        
        # 保存更新后的尝试记录
        self.storage.save_login_attempts(user_id, recent_attempts)
    
    def reset_failed_attempts(self, user_id: str) -> None:
        """
        重置失败尝试计数
        
        参数:
            user_id: 用户ID
        """
        self.storage.save_login_attempts(user_id, [])
    
    def is_locked(self, user_id: str) -> bool:
        """
        检查用户是否被锁定
        
        参数:
            user_id: 用户ID
            
        返回:
            布尔值，表示用户是否被锁定
        """
        # 获取当前尝试记录
        attempts = self.storage.get_login_attempts(user_id)
        
        # 过滤掉过期的尝试
        current_time = int(time.time())
        recent_attempts = [
            attempt for attempt in attempts 
            if current_time - attempt["timestamp"] <= self.lockout_time
        ]
        
        # 如果尝试次数超过最大限制，则用户被锁定
        return len(recent_attempts) >= self.max_attempts
    
    def get_remaining_lockout_time(self, user_id: str) -> int:
        """
        获取剩余锁定时间(秒)
        
        参数:
            user_id: 用户ID
            
        返回:
            剩余锁定时间(秒)，如果未锁定则返回0
        """
        if not self.is_locked(user_id):
            return 0
        
        # 获取当前尝试记录
        attempts = self.storage.get_login_attempts(user_id)
        
        # 找到最早的未过期尝试
        current_time = int(time.time())
        recent_attempts = [
            attempt for attempt in attempts 
            if current_time - attempt["timestamp"] <= self.lockout_time
        ]
        
        if not recent_attempts:
            return 0
        
        # 计算剩余锁定时间
        first_attempt_time = recent_attempts[0]["timestamp"]
        lockout_until = first_attempt_time + self.lockout_time
        return max(0, lockout_until - current_time)    