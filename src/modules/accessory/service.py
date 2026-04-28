"""Service nghiệp vụ quản lý phụ kiện + combo."""
from src.modules.accessory import repository as acc_repo
from src.core.exceptions import ValidationError, NotFoundError, BusinessError
from src.core.validators import validate_required
from src.core import logger
from src.core.config_loader import get_config

_LOAI_PK = {"noi_that", "ngoai_that", "dien_tu", "bao_ve", "trang_tri"}


def list_accessories() -> list[dict]:
    return acc_repo.list_all()


def get_accessory(accessory_id: int) -> dict:
    result = acc_repo.get_by_id(accessory_id)
    if not result:
        raise NotFoundError(f"Không tìm thấy phụ kiện id={accessory_id}")
    return result


def create_accessory(
    ten: str,
    loai: str,
    gia: float,
    mo_ta: str | None = None,
    ton_kho: int = 0,
    current_user: dict | None = None,
) -> int:
    validate_required({"ten": ten, "loai": loai})
    if gia < 0:
        raise ValidationError("Giá không được âm.")
    if loai not in _LOAI_PK:
        raise ValidationError(f"Loại phụ kiện phải là một trong: {', '.join(_LOAI_PK)}")
    if ton_kho < 0:
        raise ValidationError("Tồn kho không được âm.")

    acc_id = acc_repo.create(ten, mo_ta, loai, gia, ton_kho)
    if current_user:
        logger.log(current_user.get("id"), "create", "accessories", acc_id, f"Thêm phụ kiện {ten}")
    return acc_id


def update_accessory(
    accessory_id: int, current_user: dict | None = None, **kwargs
) -> None:
    if "gia" in kwargs and kwargs["gia"] < 0:
        raise ValidationError("Giá không được âm.")
    if "loai" in kwargs and kwargs["loai"] not in _LOAI_PK:
        raise ValidationError(f"Loại phụ kiện phải là một trong: {', '.join(_LOAI_PK)}")
    if "ton_kho" in kwargs and kwargs["ton_kho"] < 0:
        raise ValidationError("Tồn kho không được âm.")

    acc_repo.update(accessory_id, **kwargs)
    if current_user:
        logger.log(
            current_user.get("id"), "update", "accessories", accessory_id,
            f"Cập nhật phụ kiện id={accessory_id}"
        )


def delete_accessory(accessory_id: int, current_user: dict | None = None) -> None:
    if acc_repo.has_contracts(accessory_id):
        raise BusinessError("Phụ kiện đã có trong hợp đồng, không thể xóa.")
    acc_repo.delete(accessory_id)
    if current_user:
        logger.log(
            current_user.get("id"), "delete", "accessories", accessory_id,
            f"Xóa phụ kiện id={accessory_id}"
        )


def search_accessories(filters: dict) -> list[dict]:
    return acc_repo.search(filters)


def kiem_tra_het_pk() -> list[dict]:
    """Trả list phụ kiện có ton_kho = 0."""
    conn = acc_repo.get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, ten, loai, gia, ton_kho FROM accessories WHERE ton_kho = 0 ORDER BY ten"
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def kiem_tra_canh_bao_pk() -> list[dict]:
    """Trả list phụ kiện có ton_kho thấp hơn ngưỡng."""
    cfg = get_config()
    threshold = cfg.getint("stock", "min_stock", fallback=3)
    return acc_repo.get_low_stock(threshold)


# --- Combo ---
def list_combos() -> list[dict]:
    return acc_repo.list_combos()


def get_combo(combo_id: int) -> dict:
    result = acc_repo.get_combo_by_id(combo_id)
    if not result:
        raise NotFoundError(f"Không tìm thấy combo id={combo_id}")
    return result


def create_combo(
    ten: str,
    gia_combo: float,
    items: list[dict] | None = None,
    mo_ta: str | None = None,
    current_user: dict | None = None,
) -> int:
    """Tạo combo cùng các item.

    Args:
        items: list of {"accessory_id": int, "so_luong": int}
    """
    validate_required({"ten": ten})
    if gia_combo < 0:
        raise ValidationError("Giá combo không được âm.")

    conn = acc_repo.get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO combo_accessories (ten, gia_combo, mo_ta) VALUES (?, ?, ?)",
            (ten, gia_combo, mo_ta),
        )
        combo_id = cursor.lastrowid

        if items:
            for item in items:
                acc_repo.add_combo_item(
                    combo_id,
                    item["accessory_id"],
                    item["so_luong"],
                )
        conn.commit()
    finally:
        conn.close()

    if current_user:
        logger.log(
            current_user.get("id"), "create", "combo_accessories", combo_id,
            f"Tạo combo {ten}"
        )
    return combo_id


def update_combo(combo_id: int, current_user: dict | None = None, **kwargs) -> None:
    if "gia_combo" in kwargs and kwargs["gia_combo"] < 0:
        raise ValidationError("Giá combo không được âm.")
    acc_repo.update_combo(combo_id, **kwargs)
    if current_user:
        logger.log(
            current_user.get("id"), "update", "combo_accessories", combo_id,
            f"Cập nhật combo id={combo_id}"
        )


def delete_combo(combo_id: int, current_user: dict | None = None) -> None:
    acc_repo.delete_combo(combo_id)
    if current_user:
        logger.log(
            current_user.get("id"), "delete", "combo_accessories", combo_id,
            f"Xóa combo id={combo_id}"
        )


def get_combo_items(combo_id: int) -> list[dict]:
    return acc_repo.get_combo_items(combo_id)


def update_combo_items(combo_id: int, items: list[dict], current_user: dict | None = None) -> None:
    """Cập nhật toàn bộ item của combo (thay thế)."""
    conn = acc_repo.get_connection()
    try:
        acc_repo.delete_combo_items(combo_id)
        for item in items:
            acc_repo.add_combo_item(combo_id, item["accessory_id"], item["so_luong"])
        conn.commit()
    finally:
        conn.close()
    if current_user:
        logger.log(
            current_user.get("id"), "update", "combo_items", combo_id,
            f"Cập nhật items combo id={combo_id}"
        )


def update_ton_kho(accessory_id: int, delta: int) -> None:
    acc_repo.update_ton_kho(accessory_id, delta)