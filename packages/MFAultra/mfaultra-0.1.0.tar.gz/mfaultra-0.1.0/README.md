# MFAultra - 强大的身份验证模块

MFAultra是一个功能强大的Python身份验证模块，提供多因素认证、RBAC权限管理、IP限制、登录尝试限制等安全功能。该模块设计灵活，易于集成到各种Python应用中。

## 特性

- **多因素认证**：支持TOTP(时间一次性密码)和备份码
- **RBAC权限系统**：基于角色的访问控制，支持角色继承
- **IP限制**：可配置阻止或允许特定IP地址
- **登录尝试限制**：防止暴力破解，支持账户锁定
- **会话管理**：安全的会话令牌管理
- **密码策略**：可自定义密码复杂度要求
- **审计日志**：记录系统安全相关事件
- **模块化设计**：各组件可独立使用和扩展

## 安装
pip install MFAultra
## 快速开始

下面是一个简单的示例，展示如何使用MFAultra模块：
#### from mfaultra.auth import AuthManager
#### from mfaultra.user import UserManager
#### from mfaultra.mfa import MFAManager
#### from mfaultra.rbac import RBACManager
#### from mfaultra.session import SessionManager
#### from mfaultra.limiter import LoginAttemptLimiter
#### from mfaultra.ip_filter import IPFilter
#### from mfaultra.password_policy import PasswordPolicy
#### from mfaultra.storage.memory import InMemoryStorageAdapter

# 创建存储适配器
#### storage = InMemoryStorageAdapter()

# 初始化各个管理器
#### user_manager = UserManager(storage)
#### mfa_manager = MFAManager(storage)
#### rbac_manager = RBACManager(storage)
#### session_manager = SessionManager(storage, session_lifetime=3600)
#### limiter = LoginAttemptLimiter(storage, max_attempts=5, lockout_time=300)
#### ip_filter = IPFilter(storage)
#### password_policy = PasswordPolicy(
    min_length=8,
    require_uppercase=True,
    require_digits=True,
    require_special_chars=True
#### )

# 初始化认证管理器
#### auth_manager = AuthManager(
    user_manager=user_manager,
    mfa_manager=mfa_manager,
    session_manager=session_manager,
    limiter=limiter,
    ip_filter=ip_filter,
    rbac_manager=rbac_manager,
    password_policy=password_policy
#### )

# 创建管理员角色
#### rbac_manager.create_role('admin', '系统管理员')
#### rbac_manager.add_permission_to_role('admin', 'user:manage')
#### rbac_manager.add_permission_to_role('admin', 'role:manage')

# 注册新用户
#### admin_user = auth_manager.register_user(
    username='admin',
    password='Admin123!',
    email='admin@example.com'
#### )

# 为管理员分配角色
#### rbac_manager.assign_role_to_user(admin_user['id'], 'admin')

# 启用MFA
#### otp_url = mfa_manager.enable_mfa(admin_user['id'])
#### print(f"管理员MFA已启用，请使用OTP应用扫描: {otp_url}")

# 模拟登录过程
#### try:
    # 这里的MFA代码需要从真实的OTP应用获取
    mfa_code = input("请输入管理员MFA代码: ")
    admin_token = auth_manager.authenticate(
        username='admin',
        password='Admin123!',
        ip_address='127.0.0.1',
        mfa_code=mfa_code
    )
    
    print(f"管理员登录成功，会话令牌: {admin_token}")
    
    # 验证会话
    session_info = auth_manager.validate_session(admin_token, '127.0.0.1')
    print(f"用户: {session_info['user']['username']}, 角色: {session_info['user']['roles']}")
    
    # 检查权限
    has_permission = rbac_manager.user_has_permission(session_info['user']['id'], 'user:manage')
    print(f"用户是否有 user:manage 权限: {has_permission}")
    
#### except Exception as e:
    print(f"登录失败: {str(e)}")
## 文档

完整的文档和API参考将在后续版本中提供。

## 贡献

我们欢迎贡献！请查看我们的贡献指南获取更多信息。

## 许可证

本项目采用MIT许可证。有关详细信息，请参阅LICENSE文件。

## 作者

LitDDD - [主页](https://www.douyin.com/user/MS4wLjABAAAACQczOtUtm27WBmLg8dcGpgTrWXR6LjKp2lyJJS3XwnM?from_tab_name=main)    