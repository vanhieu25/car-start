"""Service nghiệp vụ quản lý kho xe (stock movements + purchase orders)."""
from src.db.connection import get_connection
from src.modules.car import repository as car_repo
from src.modules.supplier import repository as supplier_repo
from src.core.exceptions import ValidationError, NotFoundError
from src.core.validators import validate_required
from src.core import logger
from src.core.config_loader import get_config


def nhap_kho(car_id: str, supplier_id: int | None, so_luong: int,
            gia_nhap: float, ghi_chu: str | None = None,
            current_user: dict | None = None) -> int:
    """Nhập kho xe mới vào car_id với số lượng và giá nhập."""
    if so_luong <= 0:
        raise ValidationError("Số lượng nhập kho phải > 0.")
    if gia_nhap < 0:
        raise ValidationError("Giá nhập không được âm.")
    validate_required({"car_id": car_id})

    car = car_repo.get_by_id(car_id)
    if not car:
        raise NotFoundError(f"Không tìm thấy xe ma_xe={car_id}")

    if supplier_id:
        supplier = supplier_repo.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundError(f"Không tìm thấy nhà cung cấp id={supplier_id}")

    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO stock_movements (car_id, supplier_id, so_luong, gia_nhap, ghi_chu)
            VALUES (?, ?, ?, ?, ?)
            """,
            (car_id, supplier_id, so_luong, gia_nhap, ghi_chu),
        )
        conn.execute(
            "UPDATE cars SET ton_kho = ton_kho + ?, trang_thai = 'con_hang' WHERE ma_xe = ?",
            (so_luong, car_id),
        )
        conn.commit()
        movement_id = cursor.lastrowid
    finally:
        conn.close()

    if current_user:
        logger.log(
            current_user.get("id"), "create", "stock_movements", movement_id,
            f"Nhập kho {so_luong} xe {car_id} @ {gia_nhap:,.0f} VND"
        )
    return movement_id


def kiem_tra_canh_bao() -> list[dict]:
    """Trả về danh sách xe có tồn kho thấp hơn ngưỡng MIN_STOCK."""
    cfg = get_config()
    threshold = cfg.getint("stock", "min_stock", fallback=3)
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT ma_xe, hang, dong_xe, mau_sac, gia_ban, ton_kho
            FROM cars
            WHERE ton_kho < ?
            ORDER BY ton_kho ASC
            """,
            (threshold,),
        )
        results = [dict(row) for row in cursor.fetchall()]
        for r in results:
            r["threshold"] = threshold
        return results
    finally:
        conn.close()


def lich_su_nhap_kho(car_id: str | None = None, supplier_id: int | None = None) -> list[dict]:
    """Lấy lịch sử nhập kho, có thể lọc theo xe hoặc NCC."""
    conn = get_connection()
    try:
        conditions = []
        params = []
        if car_id:
            conditions.append("sm.car_id = ?")
            params.append(car_id)
        if supplier_id:
            conditions.append("sm.supplier_id = ?")
            params.append(supplier_id)

        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = conn.execute(
            f"""
            SELECT sm.id, sm.car_id, sm.supplier_id, sm.so_luong, sm.gia_nhap,
                   sm.ngay_nhap, sm.ghi_chu,
                   car.hang, car.dong_xe,
                   s.ten as supplier_ten
            FROM stock_movements sm
            JOIN cars car ON sm.car_id = car.ma_xe
            LEFT JOIN suppliers s ON sm.supplier_id = s.id
            WHERE {where}
            ORDER BY sm.ngay_nhap DESC
            """,
            params,
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()