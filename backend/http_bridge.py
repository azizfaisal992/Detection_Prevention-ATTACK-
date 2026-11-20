"""Restricted localhost HTTP-to-TCP bridge for the React dashboard."""

import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from .config import HTTP_HOST, HTTP_PORT, MAX_HTTP_BODY_BYTES
    from .protocol import ProtocolError
    from .tcp_client import request_balance, request_login, request_logout, request_status
except ImportError:
    from config import HTTP_HOST, HTTP_PORT, MAX_HTTP_BODY_BYTES
    from protocol import ProtocolError
    from tcp_client import request_balance, request_login, request_logout, request_status

ALLOWED_ORIGINS = {
    "http://127.0.0.1:5173",
    "http://localhost:5173",
}


class LocalBridgeServer(ThreadingHTTPServer):
    allow_reuse_address = False


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "MasqueradeGuardBridge/2.0"

    def do_GET(self):
        if self.path != "/api/status":
            self._send_json(404, {
                "status": "error",
                "message": "Not found",
            })
            return

        try:
            self._send_json(200, request_status())
        except (
            ConnectionRefusedError,
            TimeoutError,
            socket.timeout,
            OSError,
            ProtocolError,
        ) as exc:
            self._send_json(503, {
                "status": "error",
                "tcp_connected": False,
                "message": "Protected TCP server is unavailable",
                "detail": str(exc),
            })

    def do_POST(self):
        handlers = {
            "/api/login": self._login,
            "/api/balance": self._balance,
            "/api/logout": self._logout,
        }
        handler = handlers.get(self.path)
        if not handler:
            self._send_json(404, {"status": "error", "message": "Not found"})
            return
        try:
            payload = self._read_json_body()
            response = handler(payload)
            self._send_json(self._response_status(response), response)
        except ValueError as exc:
            self._send_json(400, {
                "status": "error",
                "code": "INVALID_REQUEST",
                "message": str(exc),
            })
        except (
            ConnectionRefusedError,
            TimeoutError,
            socket.timeout,
            OSError,
            ProtocolError,
        ) as exc:
            self._send_json(503, {
                "status": "error",
                "message": "Protected TCP server is unavailable",
                "detail": str(exc),
            })

    def _login(self, payload):
        username = payload.get("username")
        password = payload.get("password")
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValueError("Username and password are required")
        return request_login(username, password)

    def _balance(self, payload):
        token = payload.get("session_token")
        if not isinstance(token, str):
            raise ValueError("Session token is required")
        return request_balance(token)

    def _logout(self, payload):
        token = payload.get("session_token")
        if not isinstance(token, str):
            raise ValueError("Session token is required")
        return request_logout(token)

    def _read_json_body(self):
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json")
        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError as exc:
            raise ValueError("A valid Content-Length is required") from exc
        if not 0 < content_length <= MAX_HTTP_BODY_BYTES:
            raise ValueError("Request body is empty or too large")
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Request body must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("JSON request must be an object")
        return payload

    @staticmethod
    def _response_status(response):
        if response.get("status") == "ok":
            return 200
        return {
            "INVALID_CREDENTIALS": 401,
            "INVALID_SESSION": 401,
            "ACCESS_DENIED": 403,
        }.get(response.get("code"), 400)

    def do_OPTIONS(self):
        if self.path not in {"/api/status", "/api/login", "/api/balance", "/api/logout"}:
            self._send_json(404, {
                "status": "error",
                "message": "Not found",
            })
            return
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        origin = self.headers.get("Origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format_string, *args):
        print(f"HTTP bridge: {self.address_string()} - {format_string % args}")


def start_bridge():
    server = LocalBridgeServer((HTTP_HOST, HTTP_PORT), BridgeHandler)
    print(f"HTTP bridge listening on http://{HTTP_HOST}:{HTTP_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    start_bridge()

