import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from .logs import logger


class ServerFinished(Exception):
    pass


class TestHandler(BaseHTTPRequestHandler):
    PORT = 7138
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        data = json.loads(self.rfile.read(content_length))

        print(data["summary"])
        if data["finished"]:
            raise ServerFinished

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write("ok")

    def log_message(self, *args, **kwargs):
        pass


class TestServer:
    ADDRESS = f"http://127.0.0.1:{TestHandler.PORT}"

    @classmethod
    def serve(cls):
        server = HTTPServer(("", TestHandler.PORT), TestHandler)
        logger.debug(f"Listening to localhost:{TestHandler.PORT}")
        server.serve_forever()
