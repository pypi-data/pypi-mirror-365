from typing import Dict, Any, Optional, List, Set

class RBACManager:
    """基于角色的访问控制管理器"""
    
    def __init__(self, storage):
        """
        初始化RBAC管理器
        
        参数:
            storage: 存储适配器实例
        """
        self.storage = storage
    
    def create_role(self, role_id: str, description: str) -> Dict[str, Any]:
        """
        创建角色
        
        参数:
            role_id: 角色ID
            description: 角色描述
            
        返回:
            包含角色信息的字典
        """
        role = {
            "id": role_id,
            "description": description,
            "permissions": [],
            "parent_roles": []
        }
        
        self.storage.save_role(role)
        return role
    
    def delete_role(self, role_id: str) -> None:
        """
        删除角色
        
        参数:
            role_id: 角色ID
        """
        # 首先移除所有用户的该角色
        self.storage.remove_role_from_all_users(role_id)
        
        # 然后删除角色
        self.storage.delete_role(role_id)
    
    def add_permission_to_role(self, role_id: str, permission: str) -> None:
        """
        为角色添加权限
        
        参数:
            role_id: 角色ID
            permission: 权限名称
        """
        role = self.storage.get_role(role_id)
        if not role:
            raise ValueError(f"角色 {role_id} 不存在")
        
        if permission not in role["permissions"]:
            role["permissions"].append(permission)
            self.storage.save_role(role)
    
    def remove_permission_from_role(self, role_id: str, permission: str) -> None:
        """
        从角色中移除权限
        
        参数:
            role_id: 角色ID
            permission: 权限名称
        """
        role = self.storage.get_role(role_id)
        if not role:
            raise ValueError(f"角色 {role_id} 不存在")
        
        if permission in role["permissions"]:
            role["permissions"].remove(permission)
            self.storage.save_role(role)
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> None:
        """
        为用户分配角色
        
        参数:
            user_id: 用户ID
            role_id: 角色ID
        """
        # 检查角色是否存在
        role = self.storage.get_role(role_id)
        if not role:
            raise ValueError(f"角色 {role_id} 不存在")
        
        # 分配角色给用户
        self.storage.assign_role_to_user(user_id, role_id)
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> None:
        """
        从用户移除角色
        
        参数:
            user_id: 用户ID
            role_id: 角色ID
        """
        self.storage.remove_role_from_user(user_id, role_id)
    
    def get_user_roles(self, user_id: str) -> List[str]:
        """
        获取用户的所有角色
        
        参数:
            user_id: 用户ID
            
        返回:
            角色ID列表
        """
        return self.storage.get_user_roles(user_id)
    
    def get_role_permissions(self, role_id: str) -> List[str]:
        """
        获取角色的所有权限，包括继承的权限
        
        参数:
            role_id: 角色ID
            
        返回:
            权限列表
        """
        role = self.storage.get_role(role_id)
        if not role:
            return []
        
        # 收集直接权限
        permissions = set(role["permissions"])
        
        # 收集继承的权限
        for parent_role_id in role.get("parent_roles", []):
            parent_permissions = self.get_role_permissions(parent_role_id)
            permissions.update(parent_permissions)
        
        return list(permissions)
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """
        获取用户的所有权限
        
        参数:
            user_id: 用户ID
            
        返回:
            权限列表
        """
        roles = self.get_user_roles(user_id)
        permissions = set()
        
        for role_id in roles:
            role_permissions = self.get_role_permissions(role_id)
            permissions.update(role_permissions)
        
        return list(permissions)
    
    def user_has_permission(self, user_id: str, permission: str) -> bool:
        """
        检查用户是否有特定权限
        
        参数:
            user_id: 用户ID
            permission: 权限名称
            
        返回:
            布尔值，表示用户是否有该权限
        """
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions
    
    def add_parent_role(self, role_id: str, parent_role_id: str) -> None:
        """
        添加父角色，实现权限继承
        
        参数:
            role_id: 子角色ID
            parent_role_id: 父角色ID
        """
        # 检查角色是否存在
        role = self.storage.get_role(role_id)
        if not role:
            raise ValueError(f"角色 {role_id} 不存在")
        
        # 检查父角色是否存在
        parent_role = self.storage.get_role(parent_role_id)
        if not parent_role:
            raise ValueError(f"父角色 {parent_role_id} 不存在")
        
        # 添加父角色
        if parent_role_id not in role["parent_roles"]:
            role["parent_roles"].append(parent_role_id)
            self.storage.save_role(role)
    
    def remove_parent_role(self, role_id: str, parent_role_id: str) -> None:
        """
        移除父角色
        
        参数:
            role_id: 子角色ID
            parent_role_id: 父角色ID
        """
        role = self.storage.get_role(role_id)
        if not role:
            raise ValueError(f"角色 {role_id} 不存在")
        
        if parent_role_id in role["parent_roles"]:
            role["parent_roles"].remove(parent_role_id)
            self.storage.save_role(role)    