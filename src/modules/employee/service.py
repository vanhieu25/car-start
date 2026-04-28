"""Service nghiệp vụ quản lý nhân viên."""
from src.modules.employee import repository as emp_repo
from src.core.exceptions import ValidationError, NotFoundError, PermissionDenied
from src.core.validators import validate_phone, validate_email, validate_required
from src.core import logger


def list_employees() -> list[dict]:
    """Danh sách tất cả nhân viên."""
    return emp_repo.list_all()


def get_employee(employee_id: int) -> dict | None:
    """Lấy thông tin nhân viên."""
    return emp_repo.get_by_id(employee_id)


def create_employee(ho_ten: str, sdt: str | None = None, email: str | None = None,
                    ngay_vao_lam: str | None = None, trang_thai: str = "dang_lam",
                    ghi_chu: str | None = None, current_user: dict | None = None) -> int:
    """Tạo nhân viên mới (chỉ admin).

    Raises:
        ValidationError: Dữ liệu không hợp lệ.
        PermissionDenied: Nếu không phải admin.
    """
    validate_required({"ho_ten": ho_ten})
    if sdt:
        validate_phone(sdt)
    if email:
        validate_email(email)

    emp_id = emp_repo.create(ho_ten, sdt, email, ngay_vao_lam, trang_thai, ghi_chu)
    if current_user:
        logger.log(current_user.get("id"), "create", "employees", emp_id, f"Thêm nhân viên {ho_ten}")
    return emp_id


def update_employee(employee_id: int, current_user: dict | None = None, **kwargs) -> None:
    """Cập nhật nhân viên.

    Raises:
        NotFoundError: Không tìm thấy.
    """
    if kwargs.get("sdt"):
        validate_phone(kwargs["sdt"])
    if kwargs.get("email"):
        validate_email(kwargs["email"])

    emp_repo.update(employee_id, **kwargs)
    if current_user:
        logger.log(current_user.get("id"), "update", "employees", employee_id, f"Cập nhật nhân viên id={employee_id}")


def delete_employee(employee_id: int, current_user: dict | None = None) -> None:
    """Xóa nhân viên.

    Raises:
        NotFoundError: Không tìm thấy.
    """
    emp_repo.delete(employee_id)
    if current_user:
        logger.log(current_user.get("id"), "delete", "employees", employee_id, f"Xóa nhân viên id={employee_id}")


def get_my_profile(user: dict) -> dict | None:
    """Nhân viên xem thông tin cá nhân."""
    return emp_repo.get_my_profile(user)
