"""Small, thread-safe JSON storage with atomic file replacement."""

import json
import os
import tempfile
import threading
from copy import deepcopy
from contextlib import contextmanager

try:
    from .config import ACCOUNTS_FILE, DATA_DIR, SESSIONS_FILE
except ImportError:
    from config import ACCOUNTS_FILE, DATA_DIR, SESSIONS_FILE

_storage_lock = threading.RLock()


def initialize_storage():
    """Create mutable JSON stores if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SESSIONS_FILE.exists():
        write_json(SESSIONS_FILE, {})
    if not ACCOUNTS_FILE.exists():
        raise FileNotFoundError(f"Protected account data is missing: {ACCOUNTS_FILE}")


def read_json(path, default=None):
    """Return a complete JSON document while coordinating server threads."""
    with _storage_lock:
        with _file_lock(path):
            return _read_unlocked(path, default)


def write_json(path, data):
    """Atomically replace a JSON document so partial writes are never exposed."""
    with _storage_lock:
        with _file_lock(path):
            _write_unlocked(path, data)


def update_json(path, updater, default=None):
    """Apply a read-modify-write operation under one process-wide lock."""
    with _storage_lock:
        with _file_lock(path):
            current = _read_unlocked(path, default)
            updated = updater(current)
            _write_unlocked(path, updated)
            return updated


def _read_unlocked(path, default):
    if not path.exists():
        return deepcopy(default)
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_unlocked(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
        text=True,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


@contextmanager
def _file_lock(path):
    """Use an OS file lock so separate local processes cannot race a write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(f"{path.suffix}.lock")
    with lock_path.open("a+b") as lock_file:
        lock_file.seek(0, os.SEEK_END)
        if lock_file.tell() == 0:
            lock_file.write(b"0")
            lock_file.flush()
        lock_file.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
