import sys
import os
import logging
import socket
import urllib.request
from http.server import HTTPServer
from .handler import hyyshareHandler
from .utils import is_admin, register_network_location, add_hosts_entry, find_available_port, check_port_available
from .config import hyyshareConfig
from .setup import DirectorySetup
from .user_manager import UserManager
from .cleanup import CleanupManager, remove_config_file, remove_users_file

def setup_logging():
    """设置日志记录器"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('hyyshare_server.log')
        ]
    )
    return logging.getLogger('hyyshareServer')

def download_favicon(share_path):
    """从指定URL下载favicon.ico到共享目录"""
    favicon_path = os.path.join(share_path, 'favicon.ico')
    if os.path.exists(favicon_path):
        return True
    
    try:
        favicon_url = "http://hyysn.cn/hyyshare/favicon.ico"
        urllib.request.urlretrieve(favicon_url, favicon_path)
        logging.info(f"Downloaded favicon.ico from {favicon_url}")
        return True
    except Exception as e:
        logging.error(f"Failed to download favicon.ico: {e}")
        return False

def start_server(share_name="hyyshare", hostname="hyyshare.localhost", 
                 share_path="~", port=8545, language="english", enable_auth=False):
    """
    启动hyyshare服务器
    
    参数:
        share_name (str): 共享名称
        hostname (str): 主机名
        share_path (str): 共享目录路径
        port (int): 服务器端口
        language (str): 输出语言 ('english' 或 'chinese')
        enable_auth (bool): 是否启用身份验证
    """
    # 检查操作系统
    if os.name != 'nt':
        logging.error("This program only supports Windows systems")
        sys.exit(1)
    
    logger = setup_logging()
    
    # 初始化配置
    try:
        config = hyyshareConfig(
            share_name=share_name,
            hostname=hostname,
            share_path=share_path,
            port=port,
            enable_auth=enable_auth
        )
        config.set_language(language)
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # 检查端口是否可用
    if not check_port_available(config.port):
        new_port = find_available_port(config.port)
        if new_port:
            logger.warning(f"Port {config.port} is in use, switching to port {new_port}")
            config.port = new_port
        else:
            logger.error("No available ports found")
            sys.exit(1)
    
    # 初始化共享目录
    setup = DirectorySetup(config)
    if not setup.initialize_share():
        logger.error("Failed to initialize share directory")
        sys.exit(1)
    
    # 下载 favicon.ico
    download_favicon(config.share_path)
    
    # 初始化用户管理器
    user_manager = UserManager(config)
    
    # 添加hosts条目
    if not add_hosts_entry(config):
        if is_admin():
            logger.error(f"Please manually add to hosts file: 127.0.0.1\t{config.hostname}")
        else:
            logger.warning(config.get_message("admin_required"))
        sys.exit(1)
    
    # 创建服务器
    server_address = ('', config.port)
    handler = lambda *args: hyyshareHandler(config, user_manager, *args)
    httpd = HTTPServer(server_address, handler)
    
    # 输出启动信息
    logger.info(config.get_message("server_start"))
    
    # 注册网络位置
    register_network_location(config)
    
    # 保存配置
    config.save_to_file()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nServer shutting down...")
        httpd.server_close()
    except Exception as e:
        logger.error(f"Server error: {e}")

def cleanup_system():
    """清理系统设置：移除hosts条目和注册表项，删除配置文件"""
    logger = setup_logging()
    try:
        # 尝试加载配置
        config = hyyshareConfig.load_from_file()
    except FileNotFoundError:
        logger.info("No configuration file found, using default settings")
        config = hyyshareConfig()
    
    cleanup = CleanupManager(config)
    cleanup.cleanup_all()
    
    # 删除配置文件
    if remove_config_file():
        logger.info("Removed configuration file")
    
    if remove_users_file():
        logger.info("Removed users file")
    
    logger.info("System cleanup completed")