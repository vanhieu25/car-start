"""Repository CRUD cho bảng promotions."""
from src.db.connection import get_connection
from src.core.exceptions import NotFoundError


def list_all() -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """SELECT id, ten, mo_ta, loai, kieu_giam, muc_giam, tu_ngay, den_ngay,
                      pham_vi, pham_vi_id, dieu_kien_ton_kho_ngay, trang_thai
               FROM promotions ORDER BY id"""
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_by_id(promotion_id: int) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """SELECT id, ten, mo_ta, loai, kieu_giam, muc_giam, tu_ngay, den_ngay,
                      pham_vi, pham_vi_id, dieu_kien_ton_kho_ngay, trang_thai
               FROM promotions WHERE id = ?""",
            (promotion_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create(
    ten: str,
    loai: str,
    kieu_giam: str,
    muc_giam: float,
    tu_ngay: str | None,
    den_ngay: str | None,
    pham_vi: str,
    pham_vi_id: str | None = None,
    dieu_kien_ton_kho_ngay: int | None = None,
    trang_thai: str = "dang_chay",
    mo_ta: str | None = None,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO promotions (ten, mo_ta, loai, kieu_giam, muc_giam, tu_ngay, den_ngay,
                                      pham_vi, pham_vi_id, dieu_kien_ton_kho_ngay, trang_thai)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ten, mo_ta, loai, kieu_giam, muc_giam, tu_ngay, den_ngay, pham_vi, pham_vi_id, dieu_kien_ton_kho_ngay, trang_thai),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update(promotion_id: int, **kwargs) -> None:
    allowed = {
        "ten", "mo_ta", "loai", "kieu_giam", "muc_giam",
        "tu_ngay", "den_ngay", "pham_vi", "pham_vi_id",
        "dieu_kien_ton_kho_ngay", "trang_thai",
    }
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return
    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [promotion_id]
        cursor = conn.execute(
            f"UPDATE promotions SET {set_clause} WHERE id = ?", values
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy khuyến mãi id={promotion_id}")
        conn.commit()
    finally:
        conn.close()


def delete(promotion_id: int) -> None:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM promotions WHERE id = ?", (promotion_id,))
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy khuyến mãi id={promotion_id}")
        conn.commit()
    finally:
        conn.close()


def find_active(ngay: str | None = None) -> list[dict]:
    """Tìm các KM đang chạy và còn hiệu lực."""
    conn = get_connection()
    try:
        if ngay is None:
            from datetime import date
            ngay = str(date.today())

        cursor = conn.execute(
            """SELECT id, ten, mo_ta, loai, kieu_giam, muc_giam, tu_ngay, den_ngay,
                      pham_vi, pham_vi_id, dieu_kien_ton_kho_ngay, trang_thai
               FROM promotions
               WHERE trang_thai = 'dang_chay'
                 AND (tu_ngay IS NULL OR tu_ngay <= ?)
                 AND (den_ngay IS NULL OR den_ngay >= ?)""",
            (ngay, ngay),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()