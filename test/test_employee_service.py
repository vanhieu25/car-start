"""Test employee service."""
import pytest

from src.modules.employee import service as emp_service
from src.core.exceptions import ValidationError, NotFoundError


def test_create_employee_success(tmp_db):
    """Test tạo nhân viên thành công."""
    emp_id = emp_service.create_employee(
        ho_ten="Nguyễn Văn A",
        sdt="0987654321",
        email="nva@example.com"
    )
    assert emp_id > 0

    emp = emp_service.get_employee(emp_id)
    assert emp["ho_ten"] == "Nguyễn Văn A"
    assert emp["sdt"] == "0987654321"


def test_create_employee_missing_name(tmp_db):
    """Test tạo nhân viên thiếu tên."""
    with pytest.raises(ValidationError, match="không được để trống"):
        emp_service.create_employee(ho_ten="")


def test_create_employee_invalid_phone(tmp_db):
    """Test tạo nhân viên SĐT không hợp lệ."""
    with pytest.raises(ValidationError, match="10-11 chữ số"):
        emp_service.create_employee(ho_ten="Test", sdt="123")


def test_update_employee(tmp_db):
    """Test cập nhật nhân viên."""
    emp_id = emp_service.create_employee(ho_ten="Old Name")
    emp_service.update_employee(emp_id, ho_ten="New Name")

    emp = emp_service.get_employee(emp_id)
    assert emp["ho_ten"] == "New Name"


def test_delete_employee(tmp_db):
    """Test xóa nhân viên."""
    emp_id = emp_service.create_employee(ho_ten="To Delete")
    emp_service.delete_employee(emp_id)

    emp = emp_service.get_employee(emp_id)
    assert emp is None


def test_delete_nonexistent_employee(tmp_db):
    """Test xóa nhân viên không tồn tại."""
    with pytest.raises(NotFoundError):
        emp_service.delete_employee(99999)


def test_list_employees(tmp_db):
    """Test liệt kê nhân viên."""
    emp_service.create_employee(ho_ten="Emp 1")
    emp_service.create_employee(ho_ten="Emp 2")

    employees = emp_service.list_employees()
    assert len(employees) >= 2
