"""Repository CRUD cho bảng cars."""
from src.db.connection import get_connection
from src.core.exceptions import NotFoundError


def list_all() -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT ma_xe, hang, dong_xe, nam_sx, mau_sac, gia_ban, ton_kho, trang_thai FROM cars ORDER BY ma_xe"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_by_id(ma_xe: str) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT ma_xe, hang, dong_xe, nam_sx, mau_sac, gia_ban, ton_kho, trang_thai FROM cars WHERE ma_xe = ?",
            (ma_xe,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create(ma_xe: str, hang: str, dong_xe: str, nam_sx: int, mau_sac: str | None,
          gia_ban: float, ton_kho: int = 0, trang_thai: str = "con_hang") -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO cars (ma_xe, hang, dong_xe, nam_sx, mau_sac, gia_ban, ton_kho, trang_thai)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (ma_xe, hang, dong_xe, nam_sx, mau_sac, gia_ban, ton_kho, trang_thai),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update(ma_xe: str, **kwargs) -> None:
    allowed = {"hang", "dong_xe", "nam_sx", "mau_sac", "gia_ban", "ton_kho", "trang_thai"}
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return

    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [ma_xe]
        cursor = conn.execute(
            f"UPDATE cars SET {set_clause} WHERE ma_xe = ?",
            values,
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy xe ma_xe={ma_xe}")
        conn.commit()
    finally:
        conn.close()


def delete(ma_xe: str) -> None:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM cars WHERE ma_xe = ?", (ma_xe,))
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy xe ma_xe={ma_xe}")
        conn.commit()
    finally:
        conn.close()


def search(filters: dict) -> list[dict]:
    """Tìm kiếm nâng cao theo nhiều tiêu chí."""
    conn = get_connection()
    try:
        conditions = []
        params = []

        if filters.get("hang"):
            conditions.append("hang LIKE ?")
            params.append(f"%{filters['hang']}%")
        if filters.get("dong_xe"):
            conditions.append("dong_xe LIKE ?")
            params.append(f"%{filters['dong_xe']}%")
        if filters.get("nam_sx"):
            conditions.append("nam_sx = ?")
            params.append(filters["nam_sx"])
        if filters.get("mau_sac"):
            conditions.append("mau_sac LIKE ?")
            params.append(f"%{filters['mau_sac']}%")
        if filters.get("trang_thai"):
            conditions.append("trang_thai = ?")
            params.append(filters["trang_thai"])
        if filters.get("min_gia") is not None:
            conditions.append("gia_ban >= ?")
            params.append(filters["min_gia"])
        if filters.get("max_gia") is not None:
            conditions.append("gia_ban <= ?")
            params.append(filters["max_gia"])
        if filters.get("min_ton_kho") is not None:
            conditions.append("ton_kho >= ?")
            params.append(filters["min_ton_kho"])

        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = conn.execute(
            f"""
            SELECT ma_xe, hang, dong_xe, nam_sx, mau_sac, gia_ban, ton_kho, trang_thai
            FROM cars
            WHERE {where}
            ORDER BY ma_xe
            """,
            params,
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def has_contracts(ma_xe: str) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM contracts WHERE car_id = ?",
            (ma_xe,),
        )
        return cursor.fetchone()[0] > 0
    finally:
        conn.close()


def update_ton_kho(ma_xe: str, delta: int) -> None:
    """Cập nhật tồn kho (tăng/giảm)."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE cars SET ton_kho = ton_kho + ? WHERE ma_xe = ?",
            (delta, ma_xe),
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy xe ma_xe={ma_xe}")
        conn.commit()
    finally:
        conn.close()


def get_low_stock(threshold: int) -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT ma_xe, hang, dong_xe, ton_kho FROM cars WHERE ton_kho < ? ORDER BY ton_kho ASC",
            (threshold,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()