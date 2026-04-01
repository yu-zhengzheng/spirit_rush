"""
网页监控器：持续监控 data_panel.md 并在浏览器中渲染显示
运行: python monitor.py
访问: http://localhost:5001
"""
import http.server
import socketserver
import os
import sys

PORT = 5001
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data_panel.md')
HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
last_mtime = 0
cached_content = ""
html_template = ""
should_stop = False

def read_data_panel():
    global last_mtime, cached_content
    try:
        mtime = os.path.getmtime(DATA_FILE)
        if mtime != last_mtime:
            last_mtime = mtime
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                cached_content = f.read()
    except Exception as e:
        cached_content = f"读取失败: {e}"
    return cached_content

def load_html():
    global html_template
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html_template = f.read()
    except Exception as e:
        html_template = f"加载HTML失败: {e}"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global should_stop
        if should_stop:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Server Stopped</h1></body></html>')
            return
            
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_template.encode('utf-8'))
        elif self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            content = read_data_panel()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        global should_stop
        if self.path == '/stop':
            should_stop = True
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            # 延迟关闭，让响应发送完成
            def shutdown():
                import time
                time.sleep(0.5)
                httpd.shutdown()
            import threading
            threading.Thread(target=shutdown, daemon=True).start()
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    load_html()
    read_data_panel()
    
    print(f"[Spirit Rush] Monitor started")
    print(f"Visit http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")
    except OSError as e:
        print(f"Error: {e}")
        sys.exit(1)