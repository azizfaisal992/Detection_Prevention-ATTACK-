"""Protected TCP banking server with authenticated account access."""

import socket
import threading

try:
    from .authentication import (
        authenticate,
        create_session,
        get_valid_session,
        invalidate_session,
    )
    from .config import ACCOUNTS_FILE, SOCKET_TIMEOUT_SECONDS, TCP_HOST, TCP_PORT
    from .protocol import ProtocolError, receive_message, send_message
    from .storage import initialize_storage, read_json
except ImportError:  # Support `python backend/server.py` from the project root.
    from authentication import authenticate, create_session, get_valid_session, invalidate_session
    from config import ACCOUNTS_FILE, SOCKET_TIMEOUT_SECONDS, TCP_HOST, TCP_PORT
    from protocol import ProtocolError, receive_message, send_message
    from storage import initialize_storage, read_json


def process_request(request):
    action = request.get("action")
    if action == "status":
        return {
            "status": "ok",
            "service": "MasqueradeGuard protected TCP server",
            "tcp_connected": True,
            "message": "Protected TCP banking server is reachable",
        }

    if action == "login":
        username = request.get("username")
        password = request.get("password")
        if not isinstance(username, str) or not isinstance(password, str):
            return _error("INVALID_REQUEST", "Username and password are required")
        account = authenticate(username, password)
        if not account:
            return _error("INVALID_CREDENTIALS", "Invalid username or password")
        token, expires_at = create_session(username)
        return {
            "status": "ok",
            "message": "Login successful",
            "username": username,
            "display_name": account["display_name"],
            "session_token": token,
            "expires_at": expires_at,
        }

    if action == "check_balance":
        session = get_valid_session(request.get("session_token"))
        if not session:
            return _error("INVALID_SESSION", "Authentication is required")
        username = session["username"]
        requested_username = request.get("username")
        if requested_username is not None and requested_username != username:
            return _error("ACCESS_DENIED", "You may only access your own account")
        account = read_json(ACCOUNTS_FILE, {}).get(username)
        if not account:
            return _error("ACCOUNT_NOT_FOUND", "Account is unavailable")
        return {
            "status": "ok",
            "message": "Authorized balance request",
            "username": username,
            "display_name": account["display_name"],
            "balance": account["balance"],
            "currency": account["currency"],
        }

    if action == "logout":
        if not invalidate_session(request.get("session_token")):
            return _error("INVALID_SESSION", "Session is already invalid or expired")
        return {"status": "ok", "message": "Logout successful"}

    return _error("UNKNOWN_ACTION", "Unsupported TCP action")


def _error(code, message):
    return {"status": "error", "code": code, "message": message}


def handle_client(conn, address):
    conn.settimeout(SOCKET_TIMEOUT_SECONDS)
    try:
        request = receive_message(conn)
        send_message(conn, process_request(request))
    except (ProtocolError, socket.timeout) as exc:
        try:
            send_message(conn, {
                "status": "error",
                "code": "INVALID_REQUEST",
                "message": str(exc),
            })
        except OSError:
            pass
    except OSError as exc:
        print(f"Client {address[0]} disconnected: {exc}")


def serve_connection(conn, address):
    with conn:
        handle_client(conn, address)


def start_server():
    initialize_storage()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((TCP_HOST, TCP_PORT))
        server.listen(20)
        print(f"Protected TCP server listening on {TCP_HOST}:{TCP_PORT}")
        while True:
            conn, address = server.accept()
            thread = threading.Thread(
                target=serve_connection,
                args=(conn, address),
                daemon=True,
            )
            thread.start()


if __name__ == "__main__":
    start_server()

