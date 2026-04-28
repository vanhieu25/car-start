"""Repository CRUD bảng employees."""
from src.db.connection import get_connection
from src.core.exceptions import NotFoundError


def list_all() -> list[dict]:
    """Trả về danh sách tất cả nhân viên."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ho_ten, sdt, email, ngay_vao_lam, trang_thai, ghi_chu FROM employees ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_by_id(employee_id: int) -> dict | None:
    """Tìm nhân viên theo ID."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ho_ten, sdt, email, ngay_vao_lam, trang_thai, ghi_chu FROM employees WHERE id = ?",
            (employee_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create(ho_ten: str, sdt: str | None, email: str | None, ngay_vao_lam: str | None, trang_thai: str, ghi_chu: str | None) -> int:
    """Thêm nhân viên mới, trả về ID."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO employees (ho_ten, sdt, email, ngay_vao_lam, trang_thai, ghi_chu)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (ho_ten, sdt, email, ngay_vao_lam, trang_thai, ghi_chu),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update(employee_id: int, **kwargs) -> None:
    """Cập nhật thông tin nhân viên.

    Raises:
        NotFoundError: Nếu không tìm thấy.
    """
    allowed = {"ho_ten", "sdt", "email", "ngay_vao_lam", "trang_thai", "ghi_chu"}
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return

    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [employee_id]
        cursor = conn.execute(
            f"UPDATE employees SET {set_clause} WHERE id = ?",
            values,
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy nhân viên id={employee_id}")
        conn.commit()
    finally:
        conn.close()


def delete(employee_id: int) -> None:
    """Xóa nhân viên.

    Raises:
        NotFoundError: Nếu không tìm thấy.
    """
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy nhân viên id={employee_id}")
        conn.commit()
    finally:
        conn.close()


def get_my_profile(user: dict) -> dict | None:
    """Nhân viên tự xem thông tin của mình.

    Args:
        user: Dict user chứa 'employee_id'.
    """
    employee_id = user.get("employee_id")
    if employee_id is None:
        return None
    return get_by_id(employee_id)
