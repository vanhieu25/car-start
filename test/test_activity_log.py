"""Test activity log được ghi khi thực hiện write operations."""
from src.core import logger
from src.modules.employee import service as emp_service


def _insert_test_user(conn, user_id: int, username: str = "testuser") -> None:
    """Helper: thêm user test vào DB để thỏa mãn FK activity_log.user_id."""
    conn.execute(
        "INSERT INTO users (id, username, password_hash, role, is_active) VALUES (?, ?, ?, ?, 1)",
        (user_id, username, "hash", "admin")
    )
    conn.commit()


def test_log_creates_record(tmp_db):
    """Test hàm log tạo bản ghi activity_log."""
    _insert_test_user(tmp_db, 1)
    logger.log(user_id=1, action="test_action", table="test_table", record_id=99, detail="test detail")

    cursor = tmp_db.execute("SELECT * FROM activity_log WHERE hanh_dong = 'test_action'")
    row = cursor.fetchone()
    assert row is not None
    assert row["user_id"] == 1
    assert row["bang"] == "test_table"
    assert row["ban_ghi_id"] == 99


def test_create_employee_logs_activity(tmp_db):
    """Test tạo nhân viên ghi log."""
    _insert_test_user(tmp_db, 1)
    current_user = {"id": 1, "username": "admin", "role": "admin"}
    emp_id = emp_service.create_employee(
        ho_ten="Log Test",
        current_user=current_user
    )

    cursor = tmp_db.execute(
        "SELECT * FROM activity_log WHERE bang = 'employees' AND ban_ghi_id = ?",
        (emp_id,)
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["hanh_dong"] == "create"
    assert row["user_id"] == 1


def test_update_employee_logs_activity(tmp_db):
    """Test cập nhật nhân viên ghi log."""
    _insert_test_user(tmp_db, 2)
    emp_id = emp_service.create_employee(ho_ten="Original")
    current_user = {"id": 2, "username": "user", "role": "nhan_vien"}

    emp_service.update_employee(emp_id, ho_ten="Updated", current_user=current_user)

    cursor = tmp_db.execute(
        "SELECT COUNT(*) as cnt FROM activity_log WHERE hanh_dong = 'update' AND ban_ghi_id = ?",
        (emp_id,)
    )
    row = cursor.fetchone()
    assert row["cnt"] >= 1
