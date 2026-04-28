"""Repository CRUD cho bảng suppliers + supplier_ratings."""
from src.db.connection import get_connection
from src.core.exceptions import NotFoundError


def list_all() -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ten, dia_chi, sdt, email, nguoi_lien_he FROM suppliers ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_by_id(supplier_id: int) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ten, dia_chi, sdt, email, nguoi_lien_he FROM suppliers WHERE id = ?",
            (supplier_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create(ten: str, dia_chi: str | None = None, sdt: str | None = None,
          email: str | None = None, nguoi_lien_he: str | None = None) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO suppliers (ten, dia_chi, sdt, email, nguoi_lien_he)
            VALUES (?, ?, ?, ?, ?)
            """,
            (ten, dia_chi, sdt, email, nguoi_lien_he),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update(supplier_id: int, **kwargs) -> None:
    allowed = {"ten", "dia_chi", "sdt", "email", "nguoi_lien_he"}
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return

    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [supplier_id]
        cursor = conn.execute(
            f"UPDATE suppliers SET {set_clause} WHERE id = ?",
            values,
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy nhà cung cấp id={supplier_id}")
        conn.commit()
    finally:
        conn.close()


def delete(supplier_id: int) -> None:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy nhà cung cấp id={supplier_id}")
        conn.commit()
    finally:
        conn.close()


def add_rating(supplier_id: int, chat_luong: int, thoi_gian_giao: int,
               gia_ca: int, ghi_chu: str | None = None) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO supplier_ratings (supplier_id, chat_luong, thoi_gian_giao, gia_ca, ghi_chu)
            VALUES (?, ?, ?, ?, ?)
            """,
            (supplier_id, chat_luong, thoi_gian_giao, gia_ca, ghi_chu),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_ratings(supplier_id: int) -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, chat_luong, thoi_gian_giao, gia_ca, ghi_chu, ngay_danh_gia
            FROM supplier_ratings
            WHERE supplier_id = ?
            ORDER BY ngay_danh_gia DESC
            """,
            (supplier_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_average_rating(supplier_id: int) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT AVG(chat_luong) as avg_chat_luong,
                   AVG(thoi_gian_giao) as avg_thoi_gian_giao,
                   AVG(gia_ca) as avg_gia_ca,
                   COUNT(*) as so_danh_gia
            FROM supplier_ratings
            WHERE supplier_id = ?
            """,
            (supplier_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_import_history(supplier_id: int) -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT sm.id, sm.car_id, sm.so_luong, sm.gia_nhap, sm.ngay_nhap, sm.ghi_chu,
                   car.hang, car.dong_xe
            FROM stock_movements sm
            JOIN cars car ON sm.car_id = car.ma_xe
            WHERE sm.supplier_id = ?
            ORDER BY sm.ngay_nhap DESC
            """,
            (supplier_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()