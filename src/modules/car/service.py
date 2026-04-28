"""Service nghiệp vụ quản lý xe."""
from src.modules.car import repository as car_repo
from src.core.exceptions import ValidationError, NotFoundError, BusinessError
from src.core.validators import validate_required
from src.core import logger


def list_cars() -> list[dict]:
    return car_repo.list_all()


def get_car(ma_xe: str) -> dict:
    result = car_repo.get_by_id(ma_xe)
    if not result:
        raise NotFoundError(f"Không tìm thấy xe ma_xe={ma_xe}")
    return result


def create_car(ma_xe: str, hang: str, dong_xe: str, nam_sx: int,
               mau_sac: str | None = None, gia_ban: float = 0,
               ton_kho: int = 0, current_user: dict | None = None) -> int:
    validate_required({"ma_xe": ma_xe, "hang": hang, "dong_xe": dong_xe, "nam_sx": str(nam_sx), "gia_ban": str(gia_ban)})
    if gia_ban < 0:
        raise ValidationError("Giá bán không được âm.")
    if nam_sx < 1900 or nam_sx > 2100:
        raise ValidationError("Năm sản xuất không hợp lệ.")
    if ton_kho < 0:
        raise ValidationError("Tồn kho không được âm.")

    if car_repo.get_by_id(ma_xe):
        raise BusinessError(f"Mã xe {ma_xe} đã tồn tại.")

    car_repo.create(ma_xe, hang, dong_xe, nam_sx, mau_sac, gia_ban, ton_kho)
    if current_user:
        logger.log(current_user.get("id"), "create", "cars", None, f"Thêm xe {ma_xe}")
    return ma_xe


def update_car(ma_xe: str, current_user: dict | None = None, **kwargs) -> None:
    if "gia_ban" in kwargs and kwargs["gia_ban"] < 0:
        raise ValidationError("Giá bán không được âm.")
    if "nam_sx" in kwargs and (kwargs["nam_sx"] < 1900 or kwargs["nam_sx"] > 2100):
        raise ValidationError("Năm sản xuất không hợp lệ.")
    if "ton_kho" in kwargs and kwargs["ton_kho"] < 0:
        raise ValidationError("Tồn kho không được âm.")

    car_repo.update(ma_xe, **kwargs)
    if current_user:
        logger.log(current_user.get("id"), "update", "cars", None, f"Cập nhật xe {ma_xe}")


def delete_car(ma_xe: str, current_user: dict | None = None) -> None:
    if car_repo.has_contracts(ma_xe):
        raise BusinessError("Xe đã có hợp đồng, không thể xóa.")
    car_repo.delete(ma_xe)
    if current_user:
        logger.log(current_user.get("id"), "delete", "cars", None, f"Xóa xe {ma_xe}")


def search_cars(filters: dict) -> list[dict]:
    return car_repo.search(filters)


def update_ton_kho(ma_xe: str, delta: int) -> None:
    car_repo.update_ton_kho(ma_xe, delta)


def kiem_tra_canh_bao() -> list[dict]:
    from src.core.config_loader import get_config
    cfg = get_config()
    threshold = cfg.getint("stock", "min_stock", fallback=3)
    return car_repo.get_low_stock(threshold)