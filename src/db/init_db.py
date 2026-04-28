"""Khởi tạo cơ sở dữ liệu (xóa cũ → chạy schema → seed)."""
import sqlite3
from pathlib import Path

from src.core.config_loader import get_config


def init_db(db_path: str | None = None) -> None:
    """Xóa DB cũ (nếu có), chạy schema.sql và seed.sql.

    Args:
        db_path: Đường dẫn file DB. Nếu None, đọc từ config.ini.
    """
    if db_path is None:
        cfg = get_config()
        db_path = cfg.get("database", "path", fallback="app.db")

    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()

    schema_path = Path(__file__).with_name("schema.sql")
    seed_path = Path(__file__).with_name("seed.sql")

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")

        if schema_path.exists():
            conn.executescript(schema_path.read_text(encoding="utf-8"))

        if seed_path.exists():
            conn.executescript(seed_path.read_text(encoding="utf-8"))

        conn.commit()


if __name__ == "__main__":
    init_db()
