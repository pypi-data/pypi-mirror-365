import os
import json
from pathlib import Path

class hyyshareConfig:
    def __init__(self, share_name="hyyshare", hostname="hyyshare.localhost", 
                 share_path=os.path.expanduser("~"), port=8545, enable_auth=False):
        self.share_name = share_name
        self.hostname = hostname
        self.share_path = self._resolve_share_path(share_path)
        self.port = port
        self.language = "english"
        self.enable_auth = enable_auth
        self.users_file = "hyyshare_users.json"
        self.default_content = {
            "index.html": "<html><body><h1>Welcome to hyyshare!</h1></body></html>",
            "readme.txt": "This is a shared directory created by hyyshare"
        }
    
    def _resolve_share_path(self, path):
        """解析并验证共享路径"""
        # 扩展用户目录符号 (~)
        expanded_path = os.path.expanduser(path)
        # 获取绝对路径
        absolute_path = os.path.abspath(expanded_path)
        
        # 验证路径是否安全
        if not self._is_valid_share_path(absolute_path):
            raise ValueError(f"Invalid share path: {absolute_path}")
        
        return absolute_path
    
    def _is_valid_share_path(self, path):
        """验证共享路径是否安全有效"""
        from pathlib import Path
        try:
            resolved = Path(path).resolve()
            
            # 防止共享敏感系统目录
            protected = [
                Path("C:\\Windows"),
                Path("C:\\Program Files"),
                Path("C:\\Program Files (x86)"),
                Path("C:\\ProgramData"),
                Path.home() / "AppData"
            ]
            
            for prot in protected:
                if resolved.is_relative_to(prot):
                    return False
            
            return True
        except Exception:
            return False
    
    def set_language(self, lang):
        if lang.lower() in ["chinese", "cn", "zh"]:
            self.language = "chinese"
        else:
            self.language = "english"
    
    def get_message(self, key):
        messages = {
            "server_start": {
                "english": f"""
=============================================
hyyshare Service Started!
Access Methods:
1. File Explorer: \\\\{self.hostname}\\{self.share_name}
2. Browser: http://{self.hostname}:{self.port}/{self.share_name}
Shared Directory: {self.share_path}
=============================================
""",
                "chinese": f"""
=============================================
hyyshare 服务已启动!
访问方式:
1. 文件资源管理器: \\\\{self.hostname}\\{self.share_name}
2. 浏览器: http://{self.hostname}:{self.port}/{self.share_name}
共享目录: {self.share_path}
=============================================
"""
            },
            "reg_success": {
                "english": "Registered 'hyyshare' network location in File Explorer",
                "chinese": "已在文件资源管理器注册 'hyyshare' 网络位置"
            },
            "reg_error": {
                "english": "Registry error",
                "chinese": "注册表错误"
            },
            "admin_required": {
                "english": "Please run as administrator to complete setup",
                "chinese": "请以管理员权限运行此程序以完成初始设置"
            },
            "dir_created": {
                "english": f"Created directory: {self.share_path}",
                "chinese": f"已创建目录: {self.share_path}"
            },
            "default_content": {
                "english": "Added default content to shared directory",
                "chinese": "已向共享目录添加默认内容"
            },
            "auth_enabled": {
                "english": "Authentication enabled",
                "chinese": "已启用身份验证"
            },
            "auth_disabled": {
                "english": "Authentication disabled",
                "chinese": "已禁用身份验证"
            }
        }
        return messages[key][self.language]
    
    def to_dict(self):
        return {
            "share_name": self.share_name,
            "hostname": self.hostname,
            "share_path": self.share_path,
            "port": self.port,
            "enable_auth": self.enable_auth
        }
    
    def save_to_file(self, filename="hyyshare_config.json"):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f)
    
    @classmethod
    def load_from_file(cls, filename="hyyshare_config.json"):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # 兼容旧版本配置文件
            if "server_name" in data:
                # 将旧字段名映射到新字段名
                data["hostname"] = data.pop("server_name")
            
            return cls(**data)
        except FileNotFoundError:
            return cls()