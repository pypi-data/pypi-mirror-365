import pyotp
from typing import Dict, Any, Optional, List

class MFAManager:
    """多因素认证管理器，处理TOTP和备份码等MFA方式"""
    
    def __init__(self, storage):
        """
        初始化MFA管理器
        
        参数:
            storage: 存储适配器实例
        """
        self.storage = storage
    
    def generate_mfa_secret(self) -> str:
        """
        生成MFA密钥
        
        返回:
            MFA密钥
        """
        return pyotp.random_base32()
    
    def get_mfa_uri(self, secret: str, username: str, issuer: str = "MFAultra") -> str:
        """
        获取MFA二维码URI
        
        参数:
            secret: MFA密钥
            username: 用户名
            issuer: 发行者名称
            
        返回:
            MFA二维码URI
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(username, issuer_name=issuer)
    
    def enable_mfa(self, user_id: str, secret: str) -> List[str]:
        """
        启用MFA
        
        参数:
            user_id: 用户ID
            secret: MFA密钥
            
        返回:
            备份码列表
        """
        # 生成备份码
        backup_codes = self._generate_backup_codes()
        
        # 保存MFA信息
        mfa_data = {
            "user_id": user_id,
            "secret": secret,
            "backup_codes": backup_codes,
            "enabled": True
        }
        
        self.storage.save_mfa_data(mfa_data)
        
        # 更新用户状态
        user = self.storage.get_user_by_id(user_id)
        if user:
            user["mfa_enabled"] = True
            self.storage.save_user(user)
        
        return backup_codes
    
    def disable_mfa(self, user_id: str) -> None:
        """
        禁用MFA
        
        参数:
            user_id: 用户ID
        """
        # 删除MFA信息
        self.storage.delete_mfa_data(user_id)
        
        # 更新用户状态
        user = self.storage.get_user_by_id(user_id)
        if user:
            user["mfa_enabled"] = False
            self.storage.save_user(user)
    
    def is_mfa_enabled(self, user_id: str) -> bool:
        """
        检查用户是否启用了MFA
        
        参数:
            user_id: 用户ID
            
        返回:
            布尔值，表示是否启用了MFA
        """
        mfa_data = self.storage.get_mfa_data(user_id)
        return bool(mfa_data and mfa_data.get("enabled", False))
    
    def verify_mfa_code(self, user_id: str, code: str) -> bool:
        """
        验证MFA验证码
        
        参数:
            user_id: 用户ID
            code: MFA验证码
            
        返回:
            布尔值，表示验证码是否有效
        """
        mfa_data = self.storage.get_mfa_data(user_id)
        if not mfa_data or not mfa_data.get("enabled", False):
            return False
        
        # 检查是否是备份码
        if code in mfa_data.get("backup_codes", []):
            # 使备份码失效
            backup_codes = mfa_data["backup_codes"]
            backup_codes.remove(code)
            mfa_data["backup_codes"] = backup_codes
            self.storage.save_mfa_data(mfa_data)
            return True
        
        # 检查TOTP码
        totp = pyotp.TOTP(mfa_data["secret"])
        return totp.verify(code)
    
    def regenerate_backup_codes(self, user_id: str) -> List[str]:
        """
        重新生成备份码
        
        参数:
            user_id: 用户ID
            
        返回:
            新的备份码列表
        """
        mfa_data = self.storage.get_mfa_data(user_id)
        if not mfa_data or not mfa_data.get("enabled", False):
            raise ValueError("MFA未启用")
        
        # 生成新的备份码
        backup_codes = self._generate_backup_codes()
        mfa_data["backup_codes"] = backup_codes
        
        # 保存更新后的MFA数据
        self.storage.save_mfa_data(mfa_data)
        
        return backup_codes
    
    def _generate_backup_codes(self, count: int = 10, length: int = 8) -> List[str]:
        """
        生成备份码
        
        参数:
            count: 备份码数量
            length: 每个备份码的长度
            
        返回:
            备份码列表
        """
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return [
            ''.join(secrets.choice(alphabet) for i in range(length))
            for _ in range(count)
        ]    