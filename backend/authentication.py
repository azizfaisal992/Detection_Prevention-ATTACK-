"""Password verification and server-side session management."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

try:
    from .config import ACCOUNTS_FILE, SESSIONS_FILE, SESSION_LIFETIME_SECONDS
    from .storage import read_json, update_json
except ImportError:
    from config import ACCOUNTS_FILE, SESSIONS_FILE, SESSION_LIFETIME_SECONDS
    from storage import read_json, update_json

PBKDF2_ITERATIONS = 310_000


def _utc_now():
    return datetime.now(timezone.utc)


def _format_time(value):
    return value.isoformat().replace("+00:00", "Z")


def _parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _token_hash(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_password(password, salt_hex, expected_hash_hex):
    if not all(isinstance(value, str) for value in (password, salt_hex, expected_hash_hex)):
        return False
    try:
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            PBKDF2_ITERATIONS,
        ).hex()
    except ValueError:
        return False
    return hmac.compare_digest(actual, expected_hash_hex)


def authenticate(username, password):
    if not isinstance(username, str) or not isinstance(password, str):
        return None
    account = read_json(ACCOUNTS_FILE, {}).get(username)
    if not account:
        # Perform comparable work for an unknown user to reduce timing differences.
        hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), b"unknown-user-salt", PBKDF2_ITERATIONS)
        return None
    if not verify_password(password, account.get("salt", ""), account.get("password_hash", "")):
        return None
    return account


def create_session(username):
    token = secrets.token_urlsafe(32)
    token_digest = _token_hash(token)
    created_at = _utc_now()
    expires_at = created_at + timedelta(seconds=SESSION_LIFETIME_SECONDS)

    def add_session(sessions):
        sessions = _remove_expired(sessions, created_at)
        sessions[token_digest] = {
            "username": username,
            "created_at": _format_time(created_at),
            "expires_at": _format_time(expires_at),
            "valid": True,
        }
        return sessions

    update_json(SESSIONS_FILE, add_session, {})
    return token, _format_time(expires_at)


def get_valid_session(token):
    if not isinstance(token, str) or not 32 <= len(token) <= 128:
        return None
    sessions = read_json(SESSIONS_FILE, {})
    session = sessions.get(_token_hash(token))
    if not session or not session.get("valid"):
        return None
    try:
        if _parse_time(session["expires_at"]) <= _utc_now():
            invalidate_session(token)
            return None
    except (KeyError, TypeError, ValueError):
        return None
    return session


def invalidate_session(token):
    if not isinstance(token, str) or not 32 <= len(token) <= 128:
        return False
    digest = _token_hash(token)
    invalidated = False

    def invalidate(sessions):
        nonlocal invalidated
        if digest in sessions and sessions[digest].get("valid"):
            sessions[digest]["valid"] = False
            invalidated = True
        return sessions

    update_json(SESSIONS_FILE, invalidate, {})
    return invalidated


def _remove_expired(sessions, now):
    result = {}
    for digest, session in sessions.items():
        try:
            if session.get("valid") and _parse_time(session["expires_at"]) > now:
                result[digest] = session
        except (KeyError, TypeError, ValueError):
            continue
    return result
