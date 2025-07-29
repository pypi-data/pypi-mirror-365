import os
import logging
from http.server import SimpleHTTPRequestHandler
from .security import AuthenticationMiddleware, sanitize_filename

class hyyshareHandler(SimpleHTTPRequestHandler):
    def __init__(self, config, user_manager, *args, **kwargs):
        self.config = config
        self.user_manager = user_manager
        self.auth_middleware = AuthenticationMiddleware(user_manager)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        if not self.auth_middleware.process_request(self):
            return
        
        try:
            path = self.translate_path(self.path)
            if os.path.isdir(path):
                self.serve_directory(path)
            else:
                super().do_GET()
        except Exception as e:
            logging.error(f"Request handling error: {e}")
            self.send_error(500, f"Server error: {e}")
    
    def serve_directory(self, path):
        """提供目录服务（优先index.html）"""
        index_path = os.path.join(path, 'index.html')
        if os.path.exists(index_path):
            self.path = self.path.rstrip('/') + '/index.html'
            super().do_GET()
        else:
            self.list_directory(path)
    
    def send_auth_challenge(self):
        """发送身份验证质询"""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="hyyshare"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Authentication required</h1>')
    
    def translate_path(self, path):
        path = path.replace('/', os.sep).lstrip(os.sep)
        if path.startswith(self.config.share_name):
            path = path[len(self.config.share_name):].lstrip(os.sep)
        return os.path.join(self.config.share_path, path)
    
    def list_directory(self, path):
        try:
            entries = os.listdir(path)
            entries.sort(key=lambda a: a.lower())
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Directory Listing - {path}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin: 5px 0; }}
        a {{ text-decoration: none; color: #0366d6; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Directory: {path}</h1>
    <ul>
        <li><a href="../">.. (Parent Directory)</a></li>
"""
            
            for name in entries:
                fullpath = os.path.join(path, name)
                display_name = name
                if os.path.isdir(fullpath):
                    display_name += "/"
                html += f'        <li><a href="{name}">{display_name}</a></li>\n'
            
            html += """    </ul>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            logging.error(f"Directory listing error: {e}")
            self.send_error(500, f"Server error: {e}")