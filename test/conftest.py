"""Fixtures pytest cho toàn bộ test suite."""
import sqlite3
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_db() -> sqlite3.Connection:
    """Tạo database SQLite tạm thời cho mỗi test.

    Returns:
        sqlite3.Connection: Kết nối đến DB tạm.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row

        # Chạy schema.sql
        schema_path = Path(__file__).resolve().parents[1] / "src" / "db" / "schema.sql"
        if schema_path.exists():
            conn.executescript(schema_path.read_text(encoding="utf-8"))

        yield conn
        conn.close()
