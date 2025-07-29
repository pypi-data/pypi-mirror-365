class AuthError(Exception):
    """认证基础异常"""
    pass

class UserNotFoundError(AuthError):
    """用户不存在异常"""
    pass

class InvalidCredentialsError(AuthError):
    """无效凭证异常"""
    pass

class MFARequiredError(AuthError):
    """需要MFA验证异常"""
    pass

class InvalidMFAError(AuthError):
    """无效MFA验证码异常"""
    pass

class AccountLockedError(AuthError):
    """账户锁定异常"""
    pass

class IPBlockedError(AuthError):
    """IP地址被阻止异常"""
    pass

class PermissionDeniedError(AuthError):
    """权限拒绝异常"""
    pass    