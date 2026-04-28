"""Service nghiệp vụ quản lý nhà cung cấp."""
from src.modules.supplier import repository as supplier_repo
from src.core.exceptions import ValidationError, NotFoundError, BusinessError
from src.core.validators import validate_phone, validate_email, validate_required
from src.core import logger


def list_suppliers() -> list[dict]:
    return supplier_repo.list_all()


def get_supplier(supplier_id: int) -> dict:
    result = supplier_repo.get_by_id(supplier_id)
    if not result:
        raise NotFoundError(f"Không tìm thấy nhà cung cấp id={supplier_id}")
    return result


def create_supplier(ten: str, dia_chi: str | None = None, sdt: str | None = None,
                    email: str | None = None, nguoi_lien_he: str | None = None,
                    current_user: dict | None = None) -> int:
    validate_required({"ten": ten})
    if sdt:
        validate_phone(sdt)
    if email:
        validate_email(email)

    supplier_id = supplier_repo.create(ten, dia_chi, sdt, email, nguoi_lien_he)
    if current_user:
        logger.log(current_user.get("id"), "create", "suppliers", supplier_id, f"Thêm NCC {ten}")
    return supplier_id


def update_supplier(supplier_id: int, current_user: dict | None = None, **kwargs) -> None:
    if kwargs.get("sdt"):
        validate_phone(kwargs["sdt"])
    if kwargs.get("email"):
        validate_email(kwargs["email"])

    supplier_repo.update(supplier_id, **kwargs)
    if current_user:
        logger.log(current_user.get("id"), "update", "suppliers", supplier_id, f"Cập nhật NCC id={supplier_id}")


def delete_supplier(supplier_id: int, current_user: dict | None = None) -> None:
    supplier_repo.delete(supplier_id)
    if current_user:
        logger.log(current_user.get("id"), "delete", "suppliers", supplier_id, f"Xóa NCC id={supplier_id}")


def add_rating(supplier_id: int, chat_luong: int, thoi_gian_giao: int,
               gia_ca: int, ghi_chu: str | None = None, current_user: dict | None = None) -> int:
    for v, name in [(chat_luong, "chất lượng"), (thoi_gian_giao, "thời gian giao"), (gia_ca, "giá cả")]:
        if not (1 <= v <= 5):
            raise ValidationError(f"Điểm {name} phải từ 1 đến 5.")

    rating_id = supplier_repo.add_rating(supplier_id, chat_luong, thoi_gian_giao, gia_ca, ghi_chu)
    if current_user:
        logger.log(current_user.get("id"), "create", "supplier_ratings", rating_id, f"Đánh giá NCC id={supplier_id}")
    return rating_id


def get_ratings(supplier_id: int) -> list[dict]:
    return supplier_repo.get_ratings(supplier_id)


def get_average_rating(supplier_id: int) -> dict | None:
    return supplier_repo.get_average_rating(supplier_id)


def get_import_history(supplier_id: int) -> list[dict]:
    return supplier_repo.get_import_history(supplier_id)