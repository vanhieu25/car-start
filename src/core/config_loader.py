"""Đọc file cấu hình config.ini cho toàn bộ ứng dụng."""
import configparser
from pathlib import Path


_CONFIG: configparser.ConfigParser | None = None


def get_config() -> configparser.ConfigParser:
    """Trả về ConfigParser đã đọc từ src/config.ini (singleton).

    Returns:
        configparser.ConfigParser
    """
    global _CONFIG
    if _CONFIG is None:
        config_path = Path(__file__).resolve().parents[1] / "config.ini"
        _CONFIG = configparser.ConfigParser()
        if config_path.exists():
            _CONFIG.read(config_path, encoding="utf-8")
        else:
            _CONFIG.add_section("database")
            _CONFIG.set("database", "path", "app.db")
            _CONFIG.add_section("session")
            _CONFIG.set("session", "timeout", "1800")
            _CONFIG.add_section("stock")
            _CONFIG.set("stock", "min_stock", "3")
    return _CONFIG
