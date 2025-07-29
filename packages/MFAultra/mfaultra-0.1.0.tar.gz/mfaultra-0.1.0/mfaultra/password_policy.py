from typing import Dict, Any, List, Optional, Callable
import re

class PasswordPolicy:
    """密码策略管理器，用于定义和验证密码复杂性要求"""
    
    def __init__(self, 
                 min_length: int = 8,
                 max_length: int = 128,
                 require_uppercase: bool = True,
                 require_lowercase: bool = True,
                 require_digits: bool = True,
                 require_special_chars: bool = True,
                 allowed_special_chars: str = r'!@#$%^&*()-_=+[]{}|;:\",.<>/?',
                 custom_validators: List[Callable[[str], bool]] = None):
        """
        初始化密码策略
        
        参数:
            min_length: 最小密码长度
            max_length: 最大密码长度
            require_uppercase: 是否要求包含大写字母
            require_lowercase: 是否要求包含小写字母
            require_digits: 是否要求包含数字
            require_special_chars: 是否要求包含特殊字符
            allowed_special_chars: 允许的特殊字符集合
            custom_validators: 自定义验证函数列表
        """
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special_chars = require_special_chars
        self.allowed_special_chars = allowed_special_chars
        self.custom_validators = custom_validators or []
    
    def validate(self, password: str) -> Dict[str, bool]:
        """
        验证密码是否符合策略要求
        
        参数:
            password: 待验证的密码
            
        返回:
            包含验证结果的字典，键为验证项，值为布尔值表示是否通过
        """
        results = {
            "length": self.min_length <= len(password) <= self.max_length,
            "uppercase": any(c.isupper() for c in password) if self.require_uppercase else True,
            "lowercase": any(c.islower() for c in password) if self.require_lowercase else True,
            "digits": any(c.isdigit() for c in password) if self.require_digits else True,
            "special_chars": any(c in self.allowed_special_chars for c in password) if self.require_special_chars else True,
            "allowed_chars": all(c.isalnum() or c in self.allowed_special_chars for c in password),
            "custom": all(validator(password) for validator in self.custom_validators)
        }
        
        return results
    
    def is_valid(self, password: str) -> bool:
        """
        检查密码是否完全符合策略要求
        
        参数:
            password: 待验证的密码
            
        返回:
            布尔值，表示密码是否有效
        """
        return all(self.validate(password).values())
    
    def get_errors(self, password: str) -> List[str]:
        """
        获取密码不符合策略的错误信息
        
        参数:
            password: 待验证的密码
            
        返回:
            包含错误信息的列表
        """
        errors = []
        validation_results = self.validate(password)
        
        if not validation_results["length"]:
            errors.append(f"密码长度必须在{self.min_length}到{self.max_length}个字符之间")
        
        if not validation_results["uppercase"]:
            errors.append("密码必须包含至少一个大写字母")
        
        if not validation_results["lowercase"]:
            errors.append("密码必须包含至少一个小写字母")
        
        if not validation_results["digits"]:
            errors.append("密码必须包含至少一个数字")
        
        if not validation_results["special_chars"]:
            errors.append(f"密码必须包含至少一个特殊字符: {self.allowed_special_chars}")
        
        if not validation_results["allowed_chars"]:
            errors.append(f"密码包含不允许的字符，只允许字母、数字和以下特殊字符: {self.allowed_special_chars}")
        
        if not validation_results["custom"]:
            errors.append("密码不符合自定义验证规则")
        
        return errors    