import os
import logging
from .security import validate_share_path
from .config import hyyshareConfig

class DirectorySetup:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('hyyshareSetup')
    
    def ensure_directory_exists(self):
        """确保共享目录存在，不存在则创建"""
        try:
            # 验证路径安全性
            if not validate_share_path(self.config.share_path):
                self.logger.error(f"Invalid share path: {self.config.share_path}")
                return False
            
            # 创建目录（如果不存在）
            if not os.path.exists(self.config.share_path):
                os.makedirs(self.config.share_path, exist_ok=True)
                self.logger.info(self.config.get_message("dir_created"))
                return True
            
            # 确保是目录
            if not os.path.isdir(self.config.share_path):
                self.logger.error(f"Path is not a directory: {self.config.share_path}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error creating directory: {e}")
            return False
    
    def add_default_content(self):
        """向共享目录添加默认内容"""
        try:
            created = False
            for filename, content in self.config.default_content.items():
                filepath = os.path.join(self.config.share_path, filename)
                if not os.path.exists(filepath):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created = True
            
            if created:
                self.logger.info(self.config.get_message("default_content"))
            return created
        except Exception as e:
            self.logger.error(f"Error adding default content: {e}")
            return False
    
    def initialize_share(self):
        """初始化共享目录"""
        if not self.ensure_directory_exists():
            return False
        
        self.add_default_content()
        return True

def create_default_config():
    """创建默认配置文件"""
    config = hyyshareConfig()
    config.save_to_file()
    return config

def load_or_create_config():
    """加载或创建配置"""
    try:
        return hyyshareConfig.load_from_file()
    except Exception:
        return create_default_config()