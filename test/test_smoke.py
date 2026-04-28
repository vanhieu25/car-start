"""Smoke test cơ bản: kiểm tra import và init_db chạy không lỗi."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.init_db import init_db
from src.db.connection import get_connection


def test_import_main():
    """Kiểm tra import src.main không lỗi."""
    import src.main
    assert hasattr(src.main, "main")


def test_init_db_creates_tables(tmp_db):
    """Kiểm tra init_db tạo đúng các bảng."""
    cursor = tmp_db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = {row["name"] for row in cursor.fetchall()}

    expected_tables = {
        "employees",
        "users",
        "activity_log",
        "customers",
        "cars",
        "suppliers",
        "supplier_ratings",
        "accessories",
        "combo_accessories",
        "combo_items",
        "stock_movements",
        "purchase_orders",
        "purchase_order_items",
        "promotions",
        "contracts",
        "contract_accessories",
        "contract_promotions",
        "installments",
        "installment_payments",
        "warranties",
        "warranty_requests",
        "maintenance_schedules",
        "maintenance_history",
        "roadside_assistance",
        "campaigns",
        "events",
        "leads",
        "complaints",
    }
    assert expected_tables.issubset(tables), f"Thiếu bảng: {expected_tables - tables}"


def test_seed_data(tmp_db):
    """Kiểm tra seed data có admin user."""
    # Chạy seed.sql
    seed_path = Path(__file__).resolve().parent.parent / "src" / "db" / "seed.sql"
    if seed_path.exists():
        tmp_db.executescript(seed_path.read_text(encoding="utf-8"))

    cursor = tmp_db.execute("SELECT * FROM users WHERE username = 'admin'")
    user = cursor.fetchone()
    assert user is not None
    assert user["role"] == "admin"
    assert user["is_active"] == 1
