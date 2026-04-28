"""Fixtures pytest cho toàn bộ test suite."""
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

# Thêm src vào path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

@pytest.fixture(autouse=True)
def mock_db_connection(tmp_path):
    """Fixture tự động tạo DB tạm và set test connection cho mọi test."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = sqlite3.Row

    # Chạy schema.sql
    schema_path = Path(__file__).resolve().parents[1] / "src" / "db" / "schema.sql"
    if schema_path.exists():
        conn.executescript(schema_path.read_text(encoding="utf-8"))

    # Set test connection
    import src.db.connection as conn_module
    conn_module.set_test_connection(conn)

    yield conn

    conn_module.set_test_connection(None)
    conn.close()


@pytest.fixture
def tmp_db(mock_db_connection) -> sqlite3.Connection:
    """Trả về connection DB tạm.

    Depends on mock_db_connection để đảm bảo schema đã được tạo.
    """
    return mock_db_connection
