"""Internal client used by the HTTP bridge to reach the TCP server."""

import socket

try:
    from .config import SOCKET_TIMEOUT_SECONDS, TCP_HOST, TCP_PORT
    from .protocol import receive_message, send_message
except ImportError:
    from config import SOCKET_TIMEOUT_SECONDS, TCP_HOST, TCP_PORT
    from protocol import receive_message, send_message


def send_request(payload):
    with socket.create_connection(
        (TCP_HOST, TCP_PORT),
        timeout=SOCKET_TIMEOUT_SECONDS,
    ) as client:
        client.settimeout(SOCKET_TIMEOUT_SECONDS)
        send_message(client, payload)
        return receive_message(client)


def request_status():
    return send_request({"action": "status"})


def request_login(username, password):
    return send_request({
        "action": "login",
        "username": username,
        "password": password,
    })


def request_balance(session_token):
    return send_request({
        "action": "check_balance",
        "session_token": session_token,
    })


def request_logout(session_token):
    return send_request({
        "action": "logout",
        "session_token": session_token,
    })

