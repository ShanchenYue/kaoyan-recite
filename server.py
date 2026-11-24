# -*- coding: utf-8 -*-
"""
本地启动服务器 (手机和电脑在同一WiFi时，手机也能访问)
"""
import http.server
import socketserver
import socket
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} {format % args}")

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    local_ip = socket.gethostbyname(socket.gethostname())
    print("\n" + "="*50)
    print(f"  考研政治背诵播放器 服务器已启动!")
    print(f"="*50)
    print(f"  本机访问:   http://localhost:{PORT}")
    print(f"  手机访问:   http://{local_ip}:{PORT}")
    print(f"  (手机和电脑需在同一个WiFi)")
    print(f"="*50 + "\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
