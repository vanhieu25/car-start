"""Service nghiệp vụ quản lý khuyến mãi."""
from datetime import date
from src.modules.promotion import repository as promo_repo
from src.core.exceptions import ValidationError, NotFoundError, BusinessError
from src.core.validators import validate_required
from src.core import logger

_LOAI_KM = {"giam_tien", "tang_pk", "giam_lai", "combo"}
_KIEU_GIAM = {"co_dinh", "phan_tram"}
_PHAM_VI = {"toan_bo", "hang_xe", "dong_xe", "ton_kho_lau"}
_TRANG_THAI_KM = {"dang_chay", "tam_dung", "da_ket_thuc"}


def list_promotions() -> list[dict]:
    return promo_repo.list_all()


def get_promotion(promotion_id: int) -> dict:
    result = promo_repo.get_by_id(promotion_id)
    if not result:
        raise NotFoundError(f"Không tìm thấy khuyến mãi id={promotion_id}")
    return result


def create_promotion(
    ten: str,
    loai: str,
    kieu_giam: str,
    muc_giam: float,
    pham_vi: str,
    tu_ngay: str | None = None,
    den_ngay: str | None = None,
    pham_vi_id: str | None = None,
    dieu_kien_ton_kho_ngay: int | None = None,
    trang_thai: str = "dang_chay",
    mo_ta: str | None = None,
    current_user: dict | None = None,
) -> int:
    validate_required({"ten": ten})
    if loai not in _LOAI_KM:
        raise ValidationError(f"Loại KM phải là một trong: {', '.join(_LOAI_KM)}")
    if kieu_giam not in _KIEU_GIAM:
        raise ValidationError(f"Kiểu giảm phải là: co_dinh hoặc phan_tram")
    if pham_vi not in _PHAM_VI:
        raise ValidationError(f"Phạm vi phải là một trong: {', '.join(_PHAM_VI)}")
    if muc_giam < 0:
        raise ValidationError("Mức giảm không được âm.")
    if trang_thai not in _TRANG_THAI_KM:
        raise ValidationError("Trạng thái không hợp lệ.")

    promo_id = promo_repo.create(
        ten, loai, kieu_giam, muc_giam, tu_ngay, den_ngay,
        pham_vi, pham_vi_id, dieu_kien_ton_kho_ngay, trang_thai, mo_ta,
    )
    if current_user:
        logger.log(current_user.get("id"), "create", "promotions", promo_id, f"Tạo KM {ten}")
    return promo_id


def update_promotion(
    promotion_id: int, current_user: dict | None = None, **kwargs
) -> None:
    if "loai" in kwargs and kwargs["loai"] not in _LOAI_KM:
        raise ValidationError(f"Loại KM phải là một trong: {', '.join(_LOAI_KM)}")
    if "kieu_giam" in kwargs and kwargs["kieu_giam"] not in _KIEU_GIAM:
        raise ValidationError(f"Kiểu giảm phải là: co_dinh hoặc phan_tram")
    if "pham_vi" in kwargs and kwargs["pham_vi"] not in _PHAM_VI:
        raise ValidationError(f"Phạm vi phải là một trong: {', '.join(_PHAM_VI)}")
    if "muc_giam" in kwargs and kwargs["muc_giam"] < 0:
        raise ValidationError("Mức giảm không được âm.")
    if "trang_thai" in kwargs and kwargs["trang_thai"] not in _TRANG_THAI_KM:
        raise ValidationError("Trạng thái không hợp lệ.")

    promo_repo.update(promotion_id, **kwargs)
    if current_user:
        logger.log(
            current_user.get("id"), "update", "promotions", promotion_id,
            f"Cập nhật KM id={promotion_id}"
        )


def delete_promotion(promotion_id: int, current_user: dict | None = None) -> None:
    promo_repo.delete(promotion_id)
    if current_user:
        logger.log(
            current_user.get("id"), "delete", "promotions", promotion_id,
            f"Xóa KM id={promotion_id}"
        )


def tam_dung(promotion_id: int, current_user: dict | None = None) -> None:
    """Tạm dừng khuyến mãi."""
    promo_repo.update(promotion_id, trang_thai="tam_dung")
    if current_user:
        logger.log(
            current_user.get("id"), "update", "promotions", promotion_id,
            f"Tạm dừng KM id={promotion_id}"
        )


def kich_hoat(promotion_id: int, current_user: dict | None = None) -> None:
    """Kích hoạt lại khuyến mãi."""
    promo_repo.update(promotion_id, trang_thai="dang_chay")
    if current_user:
        logger.log(
            current_user.get("id"), "update", "promotions", promotion_id,
            f"Kích hoạt KM id={promotion_id}"
        )


def tim_km_ap_dung(
    car_id: str | None = None,
    hang: str | None = None,
    dong_xe: str | None = None,
    ngay: str | None = None,
) -> list[dict]:
    """Tìm các KM áp dụng cho xe dựa trên phạm vi.

    Args:
        car_id: Mã xe để kiểm tra ton_kho_lau
        hang, dong_xe: Hãng/dòng xe để lọc theo phạm vi
        ngay: Ngày áp dụng (mặc định hôm nay)
    """
    if ngay is None:
        ngay = str(date.today())

    all_active = promo_repo.find_active(ngay)
    applicable = []

    for km in all_active:
        if _is_applicable(km, car_id, hang, dong_xe, ngay):
            applicable.append(km)

    return applicable


def _is_applicable(
    km: dict, car_id: str | None, hang: str | None, dong_xe: str | None, ngay: str
) -> bool:
    pham_vi = km.get("pham_vi", "")

    if pham_vi == "toan_bo":
        return True

    if pham_vi == "hang_xe":
        if hang and km.get("pham_vi_id"):
            return hang.lower() == km["pham_vi_id"].lower()
        return False

    if pham_vi == "dong_xe":
        if dong_xe and km.get("pham_vi_id"):
            return dong_xe.lower() == km["pham_vi_id"].lower()
        return False

    if pham_vi == "ton_kho_lau":
        if not car_id:
            return False
        min_days = km.get("dieu_kien_ton_kho_ngay") or 0
        # Kiểm tra xe đã tồn kho bao lâu
        from src.modules.car import repository as car_repo
        car = car_repo.get_by_id(car_id)
        if not car:
            return False
        # Với xe mới nhập, so sánh số ngày tồn kho
        # Đơn giản: lấy ngày nhập kho gần nhất
        conn = car_repo.get_connection()
        try:
            cursor = conn.execute(
                """SELECT MIN(ngay_nhap) FROM stock_movements WHERE car_id = ?""",
                (car_id,),
            )
            row = cursor.fetchone()
            if row and row[0]:
                from datetime import datetime, timedelta
                first_import = row[0]
                if isinstance(first_import, str):
                    first_import = datetime.strptime(first_import, "%Y-%m-%d").date()
                days_in_stock = (datetime.strptime(ngay, "%Y-%m-%d").date() - first_import).days
                return days_in_stock >= min_days
            return False
        finally:
            conn.close()

    return False


def tinh_giam_gia(km: dict, gia_goc: float) -> float:
    """Tính số tiền giảm dựa trên khuyến mãi và giá gốc.

    Args:
        km: Khuyến mãi dict
        gia_goc: Giá gốc xe
    Returns:
        Số tiền được giảm
    """
    muc_giam = km.get("muc_giam", 0)
    kieu = km.get("kieu_giam", "co_dinh")

    if kieu == "phan_tram":
        return gia_goc * muc_giam / 100
    return muc_giam


def get_valid_promotions(
    car_id: str | None = None,
    hang: str | None = None,
    dong_xe: str | None = None,
    gia_xe: float = 0,
    ngay: str | None = None,
) -> list[dict]:
    """Trả danh sách KM khả dụng kèm số tiền giảm tính sẵn."""
    promos = tim_km_ap_dung(car_id, hang, dong_xe, ngay)
    result = []
    for km in promos:
        promo_copy = dict(km)
        promo_copy["so_tien_giam"] = tinh_giam_gia(km, gia_xe)
        result.append(promo_copy)
    return result