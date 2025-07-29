import logging
from http import HTTPStatus
from pathlib import Path

class AuthenticationMiddleware:
    def __init__(self, user_manager):
        self.user_manager = user_manager
        self.logger = logging.getLogger('hyyshareAuth')
    
    def process_request(self, handler):
        """处理身份验证请求"""
        if not self.user_manager.config.enable_auth:
            return True
        
        auth_header = handler.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            handler.send_auth_challenge()
            return False
        
        try:
            import base64
            credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
            username, password = credentials.split(':', 1)
            
            if self.user_manager.authenticate(username, password):
                return True
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
        
        handler.send_error(HTTPStatus.UNAUTHORIZED, "Invalid credentials")
        return False

def generate_api_key(length=32):
    """生成API密钥"""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_share_path(path):
    """验证共享路径安全性"""
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
        
        # 确保路径不是根目录
        if resolved == Path(resolved.root):
            return False
        
        return True
    except Exception:
        return False

def sanitize_filename(filename):
    """清理文件名防止路径遍历攻击"""
    import re
    # 移除特殊字符和路径遍历序列
    sanitized = re.sub(r'[^\w\s.-]', '', filename)
    sanitized = sanitized.replace('..', '')
    return sanitized