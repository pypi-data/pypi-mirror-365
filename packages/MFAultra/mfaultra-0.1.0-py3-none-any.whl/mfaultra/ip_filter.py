from typing import Dict, Any, Optional, List

class IPFilter:
    """IP过滤器，用于阻止或允许特定IP地址"""
    
    def __init__(self, storage):
        """
        初始化IP过滤器
        
        参数:
            storage: 存储适配器实例
        """
        self.storage = storage
    
    def block_ip(self, ip_address: str, reason: str = None) -> None:
        """
        阻止IP地址
        
        参数:
            ip_address: IP地址
            reason: 阻止原因(可选)
        """
        # 获取当前IP规则
        ip_rules = self.storage.get_ip_rules()
        
        # 添加或更新规则
        ip_rules[ip_address] = {
            "status": "blocked",
            "reason": reason,
            "timestamp": int(time.time())
        }
        
        # 保存更新后的规则
        self.storage.save_ip_rules(ip_rules)
    
    def unblock_ip(self, ip_address: str) -> None:
        """
        解除阻止IP地址
        
        参数:
            ip_address: IP地址
        """
        # 获取当前IP规则
        ip_rules = self.storage.get_ip_rules()
        
        # 移除规则
        if ip_address in ip_rules:
            del ip_rules[ip_address]
        
        # 保存更新后的规则
        self.storage.save_ip_rules(ip_rules)
    
    def is_blocked(self, ip_address: str) -> bool:
        """
        检查IP地址是否被阻止
        
        参数:
            ip_address: IP地址
            
        返回:
            布尔值，表示IP地址是否被阻止
        """
        # 获取当前IP规则
        ip_rules = self.storage.get_ip_rules()
        
        # 检查IP是否被阻止
        return ip_address in ip_rules and ip_rules[ip_address]["status"] == "blocked"
    
    def get_ip_status(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        获取IP地址状态
        
        参数:
            ip_address: IP地址
            
        返回:
            IP状态字典或None
        """
        # 获取当前IP规则
        ip_rules = self.storage.get_ip_rules()
        
        return ip_rules.get(ip_address)
    
    def list_blocked_ips(self) -> List[Dict[str, Any]]:
        """
        获取所有被阻止的IP地址列表
        
        返回:
            被阻止的IP地址列表
        """
        # 获取当前IP规则
        ip_rules = self.storage.get_ip_rules()
        
        # 过滤出被阻止的IP
        return [
            {
                "ip_address": ip,
                "reason": rule.get("reason"),
                "timestamp": rule.get("timestamp")
            }
            for ip, rule in ip_rules.items()
            if rule["status"] == "blocked"
        ]    