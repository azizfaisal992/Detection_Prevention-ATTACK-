"""Bounded newline-delimited JSON helpers for the TCP protocol."""

import json

try:
    from .config import MAX_MESSAGE_BYTES
except ImportError:  # Support direct execution from the backend directory.
    from config import MAX_MESSAGE_BYTES


class ProtocolError(ValueError):
    """Raised when a TCP message is invalid or exceeds the size limit."""


def send_message(sock, payload):
    encoded = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
    if len(encoded) > MAX_MESSAGE_BYTES:
        raise ProtocolError("Message is too large")
    sock.sendall(encoded)


def receive_message(sock):
    data = bytearray()
    while len(data) <= MAX_MESSAGE_BYTES:
        chunk = sock.recv(min(4096, MAX_MESSAGE_BYTES + 1 - len(data)))
        if not chunk:
            raise ProtocolError("Connection closed before a complete message")
        data.extend(chunk)
        newline = data.find(b"\n")
        if newline != -1:
            try:
                message = json.loads(data[:newline].decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ProtocolError("Invalid JSON message") from exc
            if not isinstance(message, dict):
                raise ProtocolError("JSON message must be an object")
            return message
    raise ProtocolError("Message is too large")

