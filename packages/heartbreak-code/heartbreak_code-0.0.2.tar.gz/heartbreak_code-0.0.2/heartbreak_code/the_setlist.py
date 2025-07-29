
# heartbreak_code/the_setlist.py

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import os

from heartbreak_code.storyboard import Storyboard


class Request:
    def __init__(self, handler):
        self.path = handler.path
        self.method = handler.command
        self.headers = dict(handler.headers)
        self.body = None
        if 'Content-Length' in self.headers:
            content_length = int(self.headers['Content-Length'])
            self.body = handler.rfile.read(content_length).decode('utf-8')

class Response:
    def __init__(self, handler, setlist_instance):
        self.handler = handler
        self.setlist_instance = setlist_instance
        self.status_code = 200
        self.headers = {}
        self.body = ""

    def status(self, code):
        self.status_code = code
        return self

    def header(self, name, value):
        self.headers[name] = value
        return self

    def send(self, content):
        self.body = content
        self._send_response()

    def json(self, data):
        self.header('Content-Type', 'application/json')
        self.body = json.dumps(data)
        self._send_response()

    def render(self, template_name, context=None):
        self.setlist_instance.render_template(self, template_name, context)

    def _send_response(self):
        self.handler.send_response(self.status_code)
        for name, value in self.headers.items():
            self.handler.send_header(name, value)
        self.handler.end_headers()
        self.handler.wfile.write(self.body.encode('utf-8'))

class Setlist:
    def __init__(self, interpreter):
        self.routes = {
            'GET': {},
            'POST': {},
            'PUT': {},
            'DELETE': {},
        }
        self.server = None
        self.server_thread = None
        self.interpreter = interpreter
        self.storyboard = Storyboard(interpreter)

    def render_template(self, res, template_name, context=None):
        template_path = os.path.join(os.getcwd(), "templates", template_name)
        try:
            rendered_html = self.storyboard.render(template_path, context)
            res.header('Content-Type', 'text/html').send(rendered_html)
        except Exception as e:
            print(f"The Setlist: Error rendering template {template_name}: {e}")
            res.status(500).send(f"Internal Server Error: {e}")

    def _add_route(self, method, path, handler_func):
        self.routes[method][path] = handler_func
        print(f"The Setlist: Added {method} route for {path}")

    def get(self, path, handler_func):
        self._add_route('GET', path, handler_func)

    def post(self, path, handler_func):
        self._add_route('POST', path, handler_func)

    def put(self, path, handler_func):
        self._add_route('PUT', path, handler_func)

    def delete(self, path, handler_func):
        self._add_route('DELETE', path, handler_func)

    def _handle_request(self, handler):
        method = handler.command
        path = handler.path

        if method in self.routes and path in self.routes[method]:
            req = Request(handler)
            res = Response(handler, self)
            try:
                self.routes[method][path](req, res)
            except Exception as e:
                print(f"The Setlist: Error handling request for {method} {path}: {e}")
                res.status(500).send(f"Internal Server Error: {e}")
        else:
            handler.send_response(404)
            handler.end_headers()
            handler.wfile.write(b"404 Not Found")

    def start_server(self, port=8000):
        if self.server:
            print("The Setlist: Server is already running.")
            return

        handler_class = type('HeartbreakHandler', (BaseHTTPRequestHandler,), {
            'do_GET': lambda self: self.server.setlist_instance._handle_request(self),
            'do_POST': lambda self: self.server.setlist_instance._handle_request(self),
            'do_PUT': lambda self: self.server.setlist_instance._handle_request(self),
            'do_DELETE': lambda self: self.server.setlist_instance._handle_request(self),
            'log_message': lambda self, format, *args: None # Suppress logging
        })

        self.server = HTTPServer(('', port), handler_class)
        self.server.setlist_instance = self # Link back to the Setlist instance

        print(f"The Setlist: Starting server on port {port}...")
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True # Allow main program to exit
        self.server_thread.start()
        print(f"The Setlist: Server running at http://localhost:{port}/")

    def stop_server(self):
        if self.server:
            print("The Setlist: Stopping server...")
            self.server.shutdown()
            self.server.server_close()
            self.server_thread.join()
            self.server = None
            self.server_thread = None
            print("The Setlist: Server stopped.")
        else:
            print("The Setlist: Server is not running.")
