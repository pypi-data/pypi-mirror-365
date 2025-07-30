import time
import base64
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any
from datetime import datetime

from code_exec.serivce.code_dispose import dispose
from code_exec.model import model


class CodeExecHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/exec":
            self.handle_code_exec()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"code exec")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def handle_code_exec(self):
        begin = time.time_ns()
        response_data = {}

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 精确到毫秒
            print(f"[{request_time}] request: {data}")

            code = data.get("code")
            base64_code = data.get("base64_code")
            language = data.get("language", "python")
            inputs = data.get("inputs", dict)

            if not isinstance(inputs, dict):
                raise ValueError("inputs must be a dict")

            if base64_code:
                try:
                    decoded_bytes = base64.b64decode(base64_code)
                    code = decoded_bytes.decode('utf-8')
                    print(f"Decoded code from base64_code: {code[:100]}...")
                except Exception as e:
                    raise ValueError(f"Failed to decode base64 code: {str(e)}")

            if not code:
                raise ValueError("Code cannot be empty")

            ret = dispose(language, inputs, code)

            response_obj = model.res_success(ret)
            response_data = self._extract_response_data(response_obj)

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            print(f"Error: {error_msg}")
            response_data = {"error": error_msg}
            self.send_response(400)
        except ValueError as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            response_data = {"error": error_msg}
            self.send_response(400)
        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            response_obj = model.res_failed(error_msg)
            response_data = self._extract_response_data(response_obj)
            self.send_response(500)
        else:
            self.send_response(200)
        finally:
            print(f"Request handled in {(time.time_ns() - begin) / 1e6:.2f} ms\n")

            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, default=str).encode('utf-8'))

    def _extract_response_data(self, response_obj) -> Dict[str, Any]:
        if hasattr(response_obj, 'body'):
            return json.loads(response_obj.body.decode('utf-8'))
        elif isinstance(response_obj, dict):
            return response_obj
        else:
            return {"result": response_obj}

    def log_message(self, format, *args):
        pass
def run():
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, CodeExecHandler)
    print("Starting server on port 8080...")
    httpd.serve_forever()
