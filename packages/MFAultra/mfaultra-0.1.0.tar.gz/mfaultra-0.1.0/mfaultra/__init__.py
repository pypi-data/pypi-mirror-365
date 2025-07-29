"""MFAultra - 强大的多因素认证和权限管理模块"""

__version__ = "0.1.0"
__author__ = "LitDDD"

from .auth import AuthManager
from .user import UserManager
from .mfa import MFAManager
from .rbac import RBACManager
from .session import SessionManager
from .limiter import LoginAttemptLimiter
from .ip_filter import IPFilter
from .password_policy import PasswordPolicy
from .audit import AuditLog
from .storage.base import StorageAdapter
from .storage.memory import InMemoryStorageAdapter
from .exceptions import (
    AuthError,
    UserNotFoundError,
    InvalidCredentialsError,
    MFARequiredError,
    InvalidMFAError,
    AccountLockedError,
    IPBlockedError,
    PermissionDeniedError
)    