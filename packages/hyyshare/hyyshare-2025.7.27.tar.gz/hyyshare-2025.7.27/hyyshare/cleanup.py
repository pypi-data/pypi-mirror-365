import os
import re
import logging
import ctypes
import winreg

class CleanupManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('hyyshareCleanup')
    
    def remove_hosts_entry(self):
        """从hosts文件中移除条目"""
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        try:
            with open(hosts_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已存在该条目
            if self.config.hostname not in content:  # 使用config.hostname
                self.logger.info(f"No entry found for {self.config.hostname} in hosts file")
                return False
            
            # 移除所有匹配的条目
            pattern = re.compile(rf'^\s*127\.0\.0\.1\s+{re.escape(self.config.hostname)}\s*$', re.MULTILINE)  # 使用config.hostname
            new_content = pattern.sub('', content)
            
            with open(hosts_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.logger.info(f"Removed {self.config.hostname} from hosts file")  # 使用config.hostname
            return True
        except Exception as e:
            self.logger.error(f"Error removing hosts entry: {e}")
            return False
    
    def unregister_network_location(self):
        """从Windows注册表移除网络位置"""
        try:
            # 移除注册表项
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace"
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{reg_path}\\{{hyyshare}}")
            except FileNotFoundError:
                pass
            
            # 移除其他相关注册表项
            class_path = r"Software\Classes\CLSID\{hyyshare}"
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{class_path}\\Shell\\Open\\Command")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{class_path}\\Shell\\Open")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{class_path}\\Shell")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{class_path}\\DefaultIcon")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, class_path)
            except FileNotFoundError:
                pass
            
            # 刷新资源管理器
            ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x0000, None, None)
            self.logger.info("Unregistered 'hyyshare' network location")
            return True
        except Exception as e:
            self.logger.error(f"Error unregistering network location: {e}")
            return False
    
    def cleanup_all(self):
        """执行所有清理操作"""
        self.remove_hosts_entry()
        self.unregister_network_location()
        self.logger.info("Cleanup completed")

def remove_config_file(filename="hyyshare_config.json"):
    """移除配置文件"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    except Exception as e:
        logging.error(f"Error removing config file: {e}")
        return False

def remove_users_file(filename="hyyshare_users.json"):
    """移除用户文件"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
    except Exception as e:
        logging.error(f"Error removing users file: {e}")
        return False