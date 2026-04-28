"""Repository xử lý truy vấn bảng users."""
import sqlite3

from src.db.connection import get_connection
from src.core.exceptions import NotFoundError


def get_user_by_username(username: str) -> dict | None:
    """Tìm user theo username.

    Returns:
        Dict chứa thông tin user hoặc None nếu không tìm thấy.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, username, password_hash, role, employee_id, is_active FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        conn.close()


def update_password(user_id: int, new_hash: str) -> None:
    """Cập nhật mật khẩu cho user.

    Raises:
        NotFoundError: Nếu user không tồn tại.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (new_hash, user_id),
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy user id={user_id}")
        conn.commit()
    finally:
        conn.close()
