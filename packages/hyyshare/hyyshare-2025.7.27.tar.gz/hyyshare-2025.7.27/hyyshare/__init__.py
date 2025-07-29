from .version import __version__
from .server import start_server
from .config import hyyshareConfig
from .server import start_server, cleanup_system
from .config import hyyshareConfig
from .user_manager import UserManager
from .utils import is_admin
import sys
import ctypes

class Admin:
    """Classes that automatically elevate privileges (Windows only)"""
    def __init__(self):
        self._restart_with_admin()

    def _restart_with_admin(self):
        if not is_admin():
            params = ' '.join([f'"{x}"' if ' ' in x else x for x in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                sys.executable,
                params,
                None,
                1
            )
            sys.exit()

__version__ = "2025.7.27"
__all__ = ['start_server', 'cleanup_system', 'hyyshareConfig', 'UserManager', '__version__', "Admin"]

def run_server(share_name="hyyshare", hostname="hyyshare.localhost", 
               share_path="~", port=8545, language="english", enable_auth=False):
    """
    启动hyyshare服务器的便捷函数
    
    参数:
        share_name (str): 共享名称
        hostname (str): 主机名
        share_path (str): 共享目录路径
        port (int): 服务器端口
        language (str): 输出语言 ('english' 或 'chinese')
        enable_auth (bool): 是否启用身份验证
    """
    start_server(
        share_name=share_name,
        hostname=hostname,
        share_path=share_path,
        port=port,
        language=language,
        enable_auth=enable_auth
    )

def cleanup():
    """清理系统设置的便捷函数"""
    cleanup_system()