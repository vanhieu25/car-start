"""Repository CRUD cho bảng accessories + combo."""
from src.db.connection import get_connection
from src.core.exceptions import NotFoundError


def list_all() -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ten, mo_ta, loai, gia, ton_kho FROM accessories ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_by_id(accessory_id: int) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ten, mo_ta, loai, gia, ton_kho FROM accessories WHERE id = ?",
            (accessory_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create(ten: str, mo_ta: str | None, loai: str, gia: float, ton_kho: int = 0) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO accessories (ten, mo_ta, loai, gia, ton_kho) VALUES (?, ?, ?, ?, ?)",
            (ten, mo_ta, loai, gia, ton_kho),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update(accessory_id: int, **kwargs) -> None:
    allowed = {"ten", "mo_ta", "loai", "gia", "ton_kho"}
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return
    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [accessory_id]
        cursor = conn.execute(f"UPDATE accessories SET {set_clause} WHERE id = ?", values)
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy phụ kiện id={accessory_id}")
        conn.commit()
    finally:
        conn.close()


def delete(accessory_id: int) -> None:
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM accessories WHERE id = ?", (accessory_id,))
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy phụ kiện id={accessory_id}")
        conn.commit()
    finally:
        conn.close()


def search(filters: dict) -> list[dict]:
    conn = get_connection()
    try:
        conditions = []
        params = []
        if filters.get("loai"):
            conditions.append("loai = ?")
            params.append(filters["loai"])
        if filters.get("ten"):
            conditions.append("ten LIKE ?")
            params.append(f"%{filters['ten']}%")
        if filters.get("min_gia") is not None:
            conditions.append("gia >= ?")
            params.append(filters["min_gia"])
        if filters.get("max_gia") is not None:
            conditions.append("gia <= ?")
            params.append(filters["max_gia"])
        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = conn.execute(
            f"SELECT id, ten, mo_ta, loai, gia, ton_kho FROM accessories WHERE {where} ORDER BY id",
            params,
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def update_ton_kho(accessory_id: int, delta: int) -> None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE accessories SET ton_kho = ton_kho + ? WHERE id = ?",
            (delta, accessory_id),
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy phụ kiện id={accessory_id}")
        conn.commit()
    finally:
        conn.close()


def get_low_stock(threshold: int = 3) -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ten, loai, gia, ton_kho FROM accessories WHERE ton_kho < ? ORDER BY ton_kho ASC",
            (threshold,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


# --- Combo ---
def list_combos() -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ten, gia_combo, mo_ta FROM combo_accessories ORDER BY id"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_combo_by_id(combo_id: int) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ten, gia_combo, mo_ta FROM combo_accessories WHERE id = ?",
            (combo_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_combo(ten: str, gia_combo: float, mo_ta: str | None = None) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO combo_accessories (ten, gia_combo, mo_ta) VALUES (?, ?, ?)",
            (ten, gia_combo, mo_ta),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_combo(combo_id: int, **kwargs) -> None:
    allowed = {"ten", "gia_combo", "mo_ta"}
    fields = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not fields:
        return
    conn = get_connection()
    try:
        set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values()) + [combo_id]
        cursor = conn.execute(
            f"UPDATE combo_accessories SET {set_clause} WHERE id = ?", values
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy combo id={combo_id}")
        conn.commit()
    finally:
        conn.close()


def delete_combo(combo_id: int) -> None:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM combo_accessories WHERE id = ?", (combo_id,)
        )
        if cursor.rowcount == 0:
            raise NotFoundError(f"Không tìm thấy combo id={combo_id}")
        conn.commit()
    finally:
        conn.close()


def get_combo_items(combo_id: int) -> list[dict]:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT ci.id, ci.accessory_id, ci.so_luong, a.ten, a.gia
            FROM combo_items ci
            JOIN accessories a ON ci.accessory_id = a.id
            WHERE ci.combo_id = ?
            """,
            (combo_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def add_combo_item(combo_id: int, accessory_id: int, so_luong: int) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO combo_items (combo_id, accessory_id, so_luong) VALUES (?, ?, ?)",
            (combo_id, accessory_id, so_luong),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def delete_combo_items(combo_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM combo_items WHERE combo_id = ?", (combo_id,))
        conn.commit()
    finally:
        conn.close()


def has_contracts(accessory_id: int) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM contract_accessories WHERE accessory_id = ?",
            (accessory_id,),
        )
        return cursor.fetchone()[0] > 0
    finally:
        conn.close()