"""Các hàm validate dữ liệu đầu vào."""
import re

from src.core.exceptions import ValidationError


def validate_email(email: str) -> None:
    """Kiểm tra email hợp lệ.

    Raises:
        ValidationError: Nếu email không đúng định dạng.
    """
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    if not email or not re.match(pattern, email):
        raise ValidationError("Email không hợp lệ.")


def validate_phone(phone: str) -> None:
    """Kiểm tra số điện thoại hợp lệ (10-11 chữ số).

    Raises:
        ValidationError: Nếu SĐT không hợp lệ.
    """
    if not phone or not re.match(r"^\d{10,11}$", phone):
        raise ValidationError("Số điện thoại phải có 10-11 chữ số.")


def validate_required(fields: dict[str, str]) -> None:
    """Kiểm tra các trường bắt buộc không rỗng.

    Args:
        fields: Dict tên trường -> giá trị.

    Raises:
        ValidationError: Nếu có trường rỗng.
    """
    for name, value in fields.items():
        if not value or (isinstance(value, str) and value.strip() == ""):
            raise ValidationError(f"Trường '{name}' không được để trống.")
