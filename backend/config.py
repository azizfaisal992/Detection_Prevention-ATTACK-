"""Local-only service configuration."""

from pathlib import Path

TCP_HOST = "127.0.0.1"
TCP_PORT = 5002
HTTP_HOST = "127.0.0.1"
HTTP_PORT = 8080
SOCKET_TIMEOUT_SECONDS = 3.0
MAX_MESSAGE_BYTES = 16 * 1024
MAX_HTTP_BODY_BYTES = 16 * 1024
SESSION_LIFETIME_SECONDS = 30 * 60

BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"

