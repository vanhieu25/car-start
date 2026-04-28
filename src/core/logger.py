"""Ghi log hoạt động vào bảng activity_log."""
from src.db.connection import get_connection


def log(
    user_id: int | None,
    action: str,
    table: str | None = None,
    record_id: int | None = None,
    detail: str | None = None,
) -> None:
    """Ghi một bản ghi vào activity_log.

    Args:
        user_id: ID người dùng thực hiện hành động.
        action: Mô tả hành động (VD: 'create', 'update', 'delete').
        table: Tên bảng bị tác động.
        record_id: ID bản ghi bị tác động.
        detail: Chi tiết bổ sung.
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO activity_log (user_id, hanh_dong, bang, ban_ghi_id, chi_tiet)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, action, table, record_id, detail),
        )
        conn.commit()
    finally:
        conn.close()
