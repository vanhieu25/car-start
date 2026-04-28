"""Test cho inventory service."""
import pytest

from src.modules.inventory import service as inventory_service
from src.modules.car import service as car_service
from src.core.exceptions import ValidationError, NotFoundError


def test_nhap_kho_success(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=0)
    sid = inventory_service.nhap_kho("CAR1", None, so_luong=5, gia_nhap=700_000_000)
    assert sid > 0

    car = car_service.get_car("CAR1")
    assert car["ton_kho"] == 5
    assert car["trang_thai"] == "con_hang"


def test_nhap_kho_with_supplier(tmp_db):
    from src.modules.supplier import service as supplier_service
    sid = supplier_service.create_supplier(ten="Test Supplier")
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=0)

    mov_id = inventory_service.nhap_kho("CAR1", sid, so_luong=3, gia_nhap=700_000_000)
    assert mov_id > 0


def test_nhap_kho_invalid_quantity(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=0)
    with pytest.raises(ValidationError, match="Số lượng"):
        inventory_service.nhap_kho("CAR1", None, so_luong=0, gia_nhap=700_000_000)


def test_nhap_kho_invalid_price(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=0)
    with pytest.raises(ValidationError, match="không được âm"):
        inventory_service.nhap_kho("CAR1", None, so_luong=5, gia_nhap=-100)


def test_nhap_kho_car_not_found(tmp_db):
    with pytest.raises(NotFoundError):
        inventory_service.nhap_kho("NONEXISTENT", None, so_luong=5, gia_nhap=700_000_000)


def test_kiem_tra_canh_bao_returns_low_stock(tmp_db):
    """Xe có tồn kho thấp phải nằm trong danh sách cảnh báo."""
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=1)
    car_service.create_car("CAR2", "Honda", "Civic", 2024, gia_ban=700_000_000, ton_kho=5)

    warnings = inventory_service.kiem_tra_canh_bao()
    assert len(warnings) >= 1
    assert warnings[0]["ma_xe"] == "CAR1"
    assert "threshold" in warnings[0]


def test_kiem_tra_canh_bao_empty(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=10)
    warnings = inventory_service.kiem_tra_canh_bao()
    assert len(warnings) == 0


def test_lich_su_nhap_kho_all(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=0)
    car_service.create_car("CAR2", "Honda", "Civic", 2024, gia_ban=700_000_000, ton_kho=0)

    inventory_service.nhap_kho("CAR1", None, so_luong=5, gia_nhap=700_000_000)
    inventory_service.nhap_kho("CAR2", None, so_luong=3, gia_nhap=600_000_000)

    history = inventory_service.lich_su_nhap_kho()
    assert len(history) == 2


def test_lich_su_nhap_kho_filter_by_car(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=0)
    car_service.create_car("CAR2", "Honda", "Civic", 2024, gia_ban=700_000_000, ton_kho=0)

    inventory_service.nhap_kho("CAR1", None, so_luong=5, gia_nhap=700_000_000)
    inventory_service.nhap_kho("CAR2", None, so_luong=3, gia_nhap=600_000_000)

    history = inventory_service.lich_su_nhap_kho(car_id="CAR1")
    assert len(history) == 1
    assert history[0]["car_id"] == "CAR1"