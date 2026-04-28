"""Repository CRUD cho bảng customers."""
from src.db.connection import get_connection
from src.core.exceptions import NotFoundError


def list_all() -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ho_ten, sdt, email, dia_chi, ngay_sinh, hang_khach_hang, ghi_chu FROM customers ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_by_id(customer_id: int) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ho_ten, sdt, email, dia_chi, ngay_sinh, hang_khach_hang, ghi_chu FROM customers WHERE id = ?",
            (customer_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create(ho_ten: str, sdt: str | None, email: str | None,
           dia_chi: str | None = None, ngay_sinh: str | None = None,
           hang_khach_hang: str = "dong", ghi_chu: str | None = None) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO customers (ho_ten, sdt, email, dia_chi, ngay_sinh, hang_khach_hang, ghi_chu)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (ho_ten, sdt, email, dia_chi, ngay_sinh, hang_khach_hang, ghi_chu),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update(customer_id: int, **kwargs) -> None:
    allowed = {"ho_ten", "sdt", "email", "dia_chi", "ngay_sinh", "hang_khach_hang", "ghi_chu"}
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return

    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [customer_id]
        cursor = conn.execute(
            f"UPDATE customers SET {set_clause} WHERE id = ?",
            values,
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy khách hàng id={customer_id}")
        conn.commit()
    finally:
        conn.close()


def delete(customer_id: int) -> None:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy khách hàng id={customer_id}")
        conn.commit()
    finally:
        conn.close()


def search(keyword: str) -> list[dict]:
    """Tìm kiếm theo tên, SĐT, hoặc email."""
    conn = get_connection()
    try:
        pattern = f"%{keyword}%"
        cursor = conn.execute(
            """
            SELECT id, ho_ten, sdt, email, dia_chi, ngay_sinh, hang_khach_hang, ghi_chu
            FROM customers
            WHERE ho_ten LIKE ? OR sdt LIKE ? OR email LIKE ?
            ORDER BY id
            """,
            (pattern, pattern, pattern),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_contract_stats(customer_id: int) -> dict:
    """Đếm số hợp đồng và tổng giá trị của khách hàng."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT COUNT(*) as so_hop_dong, COALESCE(SUM(tong_thanh_toan), 0) as tong_gia_tri
            FROM contracts
            WHERE customer_id = ? AND trang_thai != 'da_huy'
            """,
            (customer_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else {"so_hop_dong": 0, "tong_gia_tri": 0.0}
    finally:
        conn.close()


def has_contracts(customer_id: int) -> bool:
    """Kiểm tra khách hàng có hợp đồng không."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM contracts WHERE customer_id = ?",
            (customer_id,),
        )
        return cursor.fetchone()[0] > 0
    finally:
        conn.close()