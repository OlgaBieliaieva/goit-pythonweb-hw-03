from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import os
import pathlib
import urllib.parse

from jinja2 import Environment, FileSystemLoader

def format_datetime(value):    
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")  
        return dt.strftime("%d-%m-%Y %H:%M")  
    except ValueError as e:
        print(f"Error parsing timestamp: {e}")  
        return value



STORAGE_DIR = 'storage'
DATA_FILE = os.path.join(STORAGE_DIR, 'data.json')
jinja = Environment(loader=FileSystemLoader("templates"))
jinja.filters['format_datetime'] = format_datetime  

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.render_template('read.jinja')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))        
        data_parse = urllib.parse.unquote_plus(data.decode())        
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}        

        timestamp = datetime.now().isoformat()

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as file:
                try:
                    messages = json.load(file)
                except json.JSONDecodeError:
                    messages = {}  
        else:
            messages = {}
        
        messages[timestamp] = data_dict

        with open(DATA_FILE, 'w', encoding='utf-8') as file:
            json.dump(messages, file, ensure_ascii=False, indent=2)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
    
    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def render_template(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        with open('storage/data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        template = jinja.get_template(filename)
        content = template.render(messages=data)
        self.wfile.write(content.encode())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

if __name__ == '__main__':
    run()