import os
import json
import logging
from hashlib import sha256

class UserManager:
    def __init__(self, config):
        self.config = config
        self.users_file = config.users_file
        self.logger = logging.getLogger('hyyshareUserManager')
        self.users = self.load_users()
    
    def load_users(self):
        """加载用户数据"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")
            return {}
    
    def save_users(self):
        """保存用户数据"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f)
            return True
        except Exception as e:
            self.logger.error(f"Error saving users: {e}")
            return False
    
    def add_user(self, username, password):
        """添加新用户"""
        if username in self.users:
            self.logger.warning(f"User '{username}' already exists")
            return False
        
        hashed_password = sha256(password.encode()).hexdigest()
        self.users[username] = hashed_password
        self.save_users()
        self.logger.info(f"Added user: {username}")
        return True
    
    def remove_user(self, username):
        """移除用户"""
        if username not in self.users:
            self.logger.warning(f"User '{username}' does not exist")
            return False
        
        del self.users[username]
        self.save_users()
        self.logger.info(f"Removed user: {username}")
        return True
    
    def authenticate(self, username, password):
        """验证用户凭据"""
        if username not in self.users:
            return False
        
        hashed_password = sha256(password.encode()).hexdigest()
        return self.users[username] == hashed_password
    
    def list_users(self):
        """列出所有用户"""
        return list(self.users.keys())

def hash_password(password):
    """哈希密码"""
    return sha256(password.encode()).hexdigest()

def validate_username(username):
    """验证用户名有效性"""
    return 3 <= len(username) <= 20 and username.isalnum()