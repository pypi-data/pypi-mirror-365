import uuid
import time
from typing import Dict, Any, Optional, List
from .user import UserManager
from .mfa import MFAManager
from .rbac import RBACManager
from .session import SessionManager
from .limiter import LoginAttemptLimiter
from .ip_filter import IPFilter
from .password_policy import PasswordPolicy
from .audit import AuditLog
from .exceptions import (
    AuthError,
    UserNotFoundError,
    InvalidCredentialsError,
    MFARequiredError,
    InvalidMFAError,
    AccountLockedError,
    IPBlockedError
)

class AuthManager:
    """认证管理器，协调用户认证的各个方面"""
    
    def __init__(self, 
                 user_manager: UserManager,
                 mfa_manager: MFAManager,
                 session_manager: SessionManager,
                 limiter: LoginAttemptLimiter,
                 ip_filter: IPFilter,
                 rbac_manager: Optional[RBACManager] = None,
                 password_policy: Optional[PasswordPolicy] = None,
                 audit_log: Optional[AuditLog] = None):
        """
        初始化认证管理器
        
        参数:
            user_manager: 用户管理器实例
            mfa_manager: MFA管理器实例
            session_manager: 会话管理器实例
            limiter: 登录尝试限制器实例
            ip_filter: IP过滤器实例
            rbac_manager: RBAC管理器实例(可选)
            password_policy: 密码策略实例(可选)
            audit_log: 审计日志实例(可选)
        """
        self.user_manager = user_manager
        self.mfa_manager = mfa_manager
        self.session_manager = session_manager
        self.limiter = limiter
        self.ip_filter = ip_filter
        self.rbac_manager = rbac_manager
        self.password_policy = password_policy
        self.audit_log = audit_log
    
    def register_user(self, 
                     username: str, 
                     password: str, 
                     email: str,
                     metadata: Dict[str, Any] = None,
                     roles: List[str] = None) -> Dict[str, Any]:
        """
        注册新用户
        
        参数:
            username: 用户名
            password: 密码
            email: 电子邮箱
            metadata: 用户元数据(可选)
            roles: 分配的角色列表(可选)
            
        返回:
            包含用户信息的字典
            
        抛出:
            AuthError: 如果注册失败
        """
        # 验证密码策略
        if self.password_policy and not self.password_policy.is_valid(password):
            errors = self.password_policy.get_errors(password)
            raise AuthError(f"密码不符合策略要求: {', '.join(errors)}")
        
        # 检查用户名是否已存在
        if self.user_manager.get_user_by_username(username):
            raise AuthError("用户名已存在")
        
        # 创建用户
        user = self.user_manager.create_user(
            username=username,
            password=password,
            email=email,
            metadata=metadata or {}
        )
        
        # 分配角色
        if roles and self.rbac_manager:
            for role in roles:
                self.rbac_manager.assign_role_to_user(user['id'], role)
        
        # 记录审计日志
        if self.audit_log:
            self.audit_log.log_event(
                event_type="user_registered",
                user_id=user['id'],
                message=f"用户 {username} 已注册"
            )
        
        return user
    
    def authenticate(self, 
                    username: str, 
                    password: str, 
                    ip_address: str,
                    mfa_code: Optional[str] = None) -> str:
        """
        验证用户身份并创建会话
        
        参数:
            username: 用户名
            password: 密码
            ip_address: 客户端IP地址
            mfa_code: MFA验证码(可选)
            
        返回:
            会话令牌
            
        抛出:
            UserNotFoundError: 如果用户不存在
            InvalidCredentialsError: 如果凭证无效
            MFARequiredError: 如果需要MFA验证
            InvalidMFAError: 如果MFA验证码无效
            AccountLockedError: 如果账户被锁定
            IPBlockedError: 如果IP地址被阻止
        """
        # 检查IP是否被阻止
        if self.ip_filter.is_blocked(ip_address):
            raise IPBlockedError("该IP地址已被阻止")
        
        # 获取用户
        user = self.user_manager.get_user_by_username(username)
        if not user:
            # 记录失败尝试
            self.limiter.record_failed_attempt(username, ip_address)
            raise UserNotFoundError("用户不存在")
        
        # 检查账户是否被锁定
        if self.limiter.is_locked(user['id']):
            remaining_time = self.limiter.get_remaining_lockout_time(user['id'])
            raise AccountLockedError(f"账户已被锁定，剩余锁定时间: {remaining_time}秒")
        
        # 验证密码
        if not self.user_manager.verify_password(user['id'], password):
            # 记录失败尝试
            self.limiter.record_failed_attempt(username, ip_address)
            raise InvalidCredentialsError("密码不正确")
        
        # 检查是否需要MFA
        if self.mfa_manager.is_mfa_enabled(user['id']):
            if not mfa_code:
                raise MFARequiredError("需要MFA验证码")
            
            if not self.mfa_manager.verify_mfa_code(user['id'], mfa_code):
                raise InvalidMFAError("MFA验证码无效")
        
        # 重置失败尝试计数
        self.limiter.reset_failed_attempts(user['id'])
        
        # 创建会话
        session_token = self.session_manager.create_session(
            user_id=user['id'],
            ip_address=ip_address
        )
        
        # 记录审计日志
        if self.audit_log:
            self.audit_log.log_event(
                event_type="user_logged_in",
                user_id=user['id'],
                message=f"用户 {username} 已登录",
                metadata={"ip_address": ip_address}
            )
        
        return session_token
    
    def validate_session(self, 
                        session_token: str, 
                        ip_address: str) -> Dict[str, Any]:
        """
        验证会话令牌
        
        参数:
            session_token: 会话令牌
            ip_address: 客户端IP地址
            
        返回:
            包含会话信息和用户信息的字典
            
        抛出:
            AuthError: 如果会话无效
        """
        # 验证会话
        session = self.session_manager.validate_session(session_token, ip_address)
        if not session:
            raise AuthError("无效的会话")
        
        # 获取用户信息
        user = self.user_manager.get_user_by_id(session['user_id'])
        if not user:
            # 会话存在但用户不存在，无效状态
            self.session_manager.invalidate_session(session_token)
            raise AuthError("无效的会话")
        
        # 获取用户角色(如果有RBAC管理器)
        if self.rbac_manager:
            user['roles'] = self.rbac_manager.get_user_roles(user['id'])
            user['permissions'] = self.rbac_manager.get_user_permissions(user['id'])
        
        return {
            "session": session,
            "user": user
        }
    
    def logout(self, session_token: str) -> None:
        """
        用户注销，使会话无效
        
        参数:
            session_token: 会话令牌
        """
        # 使会话无效
        self.session_manager.invalidate_session(session_token)
        
        # 记录审计日志
        if self.audit_log:
            session = self.session_manager.get_session(session_token)
            if session:
                user = self.user_manager.get_user_by_id(session['user_id'])
                if user:
                    self.audit_log.log_event(
                        event_type="user_logged_out",
                        user_id=user['id'],
                        message=f"用户 {user['username']} 已注销"
                    )    