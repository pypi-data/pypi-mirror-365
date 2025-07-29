import ctypes
import winreg
import sys
import os
import logging
import socket

logger = logging.getLogger('hyyshareUtils')

def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def register_network_location(config):
    """注册网络位置"""
    try:
        # 创建注册表项
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"{reg_path}\\{{hyyshare}}")
        winreg.SetValue(key, "", winreg.REG_SZ, "hyyshare")
        winreg.CloseKey(key)
        
        # 设置图标和属性
        class_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                    r"Software\Classes\CLSID\{hyyshare}")
        winreg.SetValue(class_key, "", winreg.REG_SZ, "hyyshare")
        
        icon_key = winreg.CreateKey(class_key, "DefaultIcon")
        winreg.SetValue(icon_key, "", winreg.REG_SZ, 
                       r"C:\Windows\System32\SHELL32.dll,15")
        
        shell_key = winreg.CreateKey(class_key, "Shell")
        open_key = winreg.CreateKey(shell_key, "Open")
        command_key = winreg.CreateKey(open_key, "Command")
        winreg.SetValue(command_key, "", winreg.REG_SZ, 
                       f'explorer.exe "\\\\{config.hostname}\\{config.share_name}"')  # 使用 config.hostname
        
        # 刷新资源管理器
        ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
        logger.info(config.get_message("reg_success"))
        return True
    except Exception as e:
        logger.error(f"{config.get_message('reg_error')}: {e}")
        return False

def add_hosts_entry(config):
    """添加hosts条目指向本地 - 更健壮的实现"""
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    entry = f"127.0.0.1\t{config.hostname}\n"  # 使用 config.hostname
    
    try:
        # 尝试以多种编码方式读取 hosts 文件
        encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16', 'gbk', 'gb2312', 'gb18030']
        content = None
        
        for encoding in encodings:
            try:
                with open(hosts_path, 'r', encoding=encoding) as f:
                    content = f.read()
                logger.info(f"Successfully read hosts file with {encoding} encoding")
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if content is None:
            # 所有编码尝试失败，使用二进制模式读取并忽略错误
            try:
                with open(hosts_path, 'rb') as f:
                    content_bytes = f.read()
                # 尝试UTF-8解码，忽略错误
                content = content_bytes.decode('utf-8', errors='ignore')
                logger.warning("Used binary mode to read hosts file and ignored decoding errors")
            except Exception as e:
                logger.error(f"Failed to read hosts file: {e}")
                return False
        
        # 检查是否已存在该条目 - 使用 config.hostname
        if config.hostname in content:
            logger.info(f"{config.hostname} already exists in hosts file")
            return True
        
        # 添加新条目
        new_content = content + entry
        
        # 以管理员权限写入
        if is_admin():
            # 使用UTF-8编码写入，这是现代Windows的标准
            try:
                with open(hosts_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"Successfully added {config.hostname} to hosts file")
                return True
            except Exception as e:
                logger.error(f"Failed to write to hosts file: {e}")
                return False
        else:
            # 请求管理员权限重新运行
            logger.info("Requesting admin privileges to modify hosts file...")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, 
                                              f'"{sys.argv[0]}" --add-hosts', None, 1)
            return False
    except Exception as e:
        logger.error(f"Hosts file error: {e}")
        return False

def check_port_available(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except socket.error:
            return False

def find_available_port(start_port=8545, max_attempts=20):
    """查找可用端口"""
    port = start_port
    attempts = 0
    while attempts < max_attempts:
        if check_port_available(port):
            return port
        port += 1
        attempts += 1
    return None

def get_local_ip():
    """获取本地IP地址"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

def create_shortcut(target, shortcut_path):
    """创建快捷方式（仅Windows）"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.save()
        return True
    except ImportError:
        logging.warning("Shortcut creation requires pywin32 package")
        return False
    except Exception as e:
        logging.error(f"Error creating shortcut: {e}")
        return False