import bcrypt
from typing import Dict, Any, Optional, List

class UserManager:
    """用户管理器，负责用户的创建、查询和更新"""
    
    def __init__(self, storage):
        """
        初始化用户管理器
        
        参数:
            storage: 存储适配器实例
        """
        self.storage = storage
    
    def create_user(self, 
                   username: str, 
                   password: str, 
                   email: str,
                   metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        创建新用户
        
        参数:
            username: 用户名
            password: 明文密码
            email: 电子邮箱
            metadata: 用户元数据(可选)
            
        返回:
            包含用户信息的字典
        """
        # 生成密码哈希
        password_hash = self._hash_password(password)
        
        # 构建用户数据
        user = {
            "id": self.storage.generate_id("user"),
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "metadata": metadata or {},
            "created_at": int(time.time()),
            "updated_at": int(time.time()),
            "is_active": True,
            "mfa_enabled": False,
            "password_history": [password_hash]  # 记录密码历史
        }
        
        # 保存用户
        self.storage.save_user(user)
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        通过ID获取用户
        
        参数:
            user_id: 用户ID
            
        返回:
            用户字典或None
        """
        return self.storage.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        通过用户名获取用户
        
        参数:
            username: 用户名
            
        返回:
            用户字典或None
        """
        return self.storage.get_user_by_username(username)
    
    def update_user(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        更新用户信息
        
        参数:
            user_id: 用户ID
            **kwargs: 要更新的字段和值
            
        返回:
            更新后的用户字典
            
        抛出:
            ValueError: 如果用户不存在
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 更新用户字段
        for key, value in kwargs.items():
            if key in user:
                user[key] = value
        
        user["updated_at"] = int(time.time())
        
        # 保存更新后的用户
        self.storage.save_user(user)
        
        return user
    
    def delete_user(self, user_id: str) -> None:
        """
        删除用户
        
        参数:
            user_id: 用户ID
            
        抛出:
            ValueError: 如果用户不存在
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        self.storage.delete_user(user_id)
    
    def verify_password(self, user_id: str, password: str) -> bool:
        """
        验证密码
        
        参数:
            user_id: 用户ID
            password: 明文密码
            
        返回:
            密码是否匹配的布尔值
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'])
    
    def change_password(self, 
                       user_id: str, 
                       old_password: str, 
                       new_password: str) -> None:
        """
        更改用户密码
        
        参数:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        抛出:
            ValueError: 如果用户不存在或旧密码不正确
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 验证旧密码
        if not self.verify_password(user_id, old_password):
            raise ValueError("旧密码不正确")
        
        # 检查新密码是否与历史密码相同
        new_password_hash = self._hash_password(new_password)
        if new_password_hash in user['password_history']:
            raise ValueError("新密码不能与最近使用的密码相同")
        
        # 更新密码
        user['password_hash'] = new_password_hash
        
        # 更新密码历史(保留最近的5个密码)
        user['password_history'] = [new_password_hash] + user['password_history'][:4]
        
        # 保存更新后的用户
        self.storage.save_user(user)
    
    def _hash_password(self, password: str) -> bytes:
        """
        哈希密码
        
        参数:
            password: 明文密码
            
        返回:
            哈希后的密码
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())    