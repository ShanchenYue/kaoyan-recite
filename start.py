# -*- coding: utf-8 -*-
"""
考研政治背诵播放器 - 一键启动服务器
自动监听 0.0.0.0:8000, 电脑和手机(同WiFi)都能访问
"""
import http.server
import socketserver
import socket
import os
import webbrowser
import threading

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 安静点

def open_browser():
    import time
    time.sleep(1.0)
    try:
        webbrowser.open(f'http://localhost:{PORT}')
    except:
        pass

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print()
        print("=" * 55)
        print("  📚 考研政治背诵播放器 - 服务器已启动")
        print("=" * 55)
        print(f"  电脑访问 :  http://localhost:{PORT}")
        print(f"  手机访问 :  http://{local_ip}:{PORT}")
        print(f"  (手机需和电脑在同一个 WiFi)")
        print()
        print("  想打包成 APK? 看 app 目录下的 APK打包说明.md")
        print("=" * 55)
        print("  Ctrl+C 停止\n")

        # 自动打开浏览器
        threading.Thread(target=open_browser, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")
