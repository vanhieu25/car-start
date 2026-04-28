"""Quản lý kết nối SQLite cho ứng dụng."""
import sqlite3
from pathlib import Path
from src.core.config_loader import get_config

_TEST_CONN = None


class _NoCloseConnection:
    """Wrapper cho connection test mode, ngăn repository đóng connection."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def __getattr__(self, name: str):
        return getattr(self._conn, name)

    def close(self):
        pass


def set_test_connection(conn: sqlite3.Connection | None) -> None:
    """Đặt connection test mode (dùng trong pytest)."""
    global _TEST_CONN
    _TEST_CONN = conn


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Mở kết nối SQLite và bật các PRAGMA cần thiết.

    Args:
        db_path: Đường dẫn đến file DB. Nếu None, đọc từ config.ini.

    Returns:
        sqlite3.Connection đã bật foreign_keys và WAL mode.
    """
    global _TEST_CONN
    if _TEST_CONN is not None:
        return _NoCloseConnection(_TEST_CONN)

    if db_path is None:
        cfg = get_config()
        db_path = cfg.get("database", "path", fallback="app.db")

    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = sqlite3.Row
    return conn
