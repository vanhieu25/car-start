"""Test cho car service."""
import pytest

from src.modules.car import service as car_service
from src.core.exceptions import ValidationError, NotFoundError, BusinessError


def test_create_car_success(tmp_db):
    ma_xe = car_service.create_car(
        ma_xe="TOYOTA-CAMRY-2024",
        hang="Toyota",
        dong_xe="Camry",
        nam_sx=2024,
        mau_sac="Đen",
        gia_ban=800_000_000,
        ton_kho=5,
    )
    assert ma_xe == "TOYOTA-CAMRY-2024"
    car = car_service.get_car(ma_xe)
    assert car["hang"] == "Toyota"
    assert car["ton_kho"] == 5


def test_create_car_duplicate_id(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000)
    with pytest.raises(BusinessError, match="đã tồn tại"):
        car_service.create_car("CAR1", "Honda", "Civic", 2024, gia_ban=700_000_000)


def test_create_car_invalid_year(tmp_db):
    with pytest.raises(ValidationError, match="Năm"):
        car_service.create_car("CAR2", "Toyota", "Camry", 1800, gia_ban=800_000_000)


def test_create_car_negative_price(tmp_db):
    with pytest.raises(ValidationError, match="không được âm"):
        car_service.create_car("CAR2", "Toyota", "Camry", 2024, gia_ban=-100)


def test_update_car(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000)
    car_service.update_car("CAR1", gia_ban=850_000_000, mau_sac="Trắng")
    car = car_service.get_car("CAR1")
    assert car["gia_ban"] == 850_000_000
    assert car["mau_sac"] == "Trắng"


def test_delete_car_no_contracts(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000)
    car_service.delete_car("CAR1")
    with pytest.raises(NotFoundError):
        car_service.get_car("CAR1")


def test_delete_car_has_contracts(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000)
    # Tạo customer để FK không lỗi
    tmp_db.execute(
        "INSERT INTO customers (ho_ten, sdt) VALUES ('TestCust', '0123456789')"
    )
    tmp_db.execute(
        "INSERT INTO contracts (ma_hd, customer_id, car_id, gia_xe, tong_thanh_toan) VALUES ('HD001', 1, 'CAR1', 800000000, 800000000)"
    )
    tmp_db.commit()

    with pytest.raises(BusinessError, match="hợp đồng"):
        car_service.delete_car("CAR1")


def test_search_cars_by_hang(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000)
    car_service.create_car("CAR2", "Honda", "Civic", 2024, gia_ban=700_000_000)
    car_service.create_car("CAR3", "Toyota", "Vios", 2023, gia_ban=600_000_000)

    results = car_service.search_cars({"hang": "Toyota"})
    assert len(results) == 2


def test_search_cars_multi_criteria(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, mau_sac="Đen")
    car_service.create_car("CAR2", "Toyota", "Camry", 2024, gia_ban=800_000_000, mau_sac="Trắng")
    car_service.create_car("CAR3", "Toyota", "Vios", 2023, gia_ban=600_000_000)

    results = car_service.search_cars({"hang": "Toyota", "nam_sx": 2024, "mau_sac": "Đen"})
    assert len(results) == 1
    assert results[0]["ma_xe"] == "CAR1"


def test_search_cars_by_price_range(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000)
    car_service.create_car("CAR2", "Toyota", "Vios", 2023, gia_ban=500_000_000)

    results = car_service.search_cars({"min_gia": 600_000_000})
    assert all(r["gia_ban"] >= 600_000_000 for r in results)


def test_search_cars_by_status(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000)  # default trang_thai=con_hang
    car_service.create_car("CAR2", "Honda", "Civic", 2024, gia_ban=700_000_000)
    car_service.update_car("CAR2", trang_thai="da_ban")

    results = car_service.search_cars({"trang_thai": "con_hang"})
    assert all(r["trang_thai"] == "con_hang" for r in results)


def test_update_ton_kho(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=5)
    car_service.update_ton_kho("CAR1", 3)  # Nhập thêm 3
    car = car_service.get_car("CAR1")
    assert car["ton_kho"] == 8

    car_service.update_ton_kho("CAR1", -2)  # Bán 2
    car = car_service.get_car("CAR1")
    assert car["ton_kho"] == 6


def test_kiem_tra_canh_bao_low_stock(tmp_db):
    """Xe có tồn kho < MIN_STOCK (3) phải được cảnh báo."""
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=1)
    car_service.create_car("CAR2", "Honda", "Civic", 2024, gia_ban=700_000_000, ton_kho=2)
    car_service.create_car("CAR3", "Mazda", "3", 2024, gia_ban=600_000_000, ton_kho=5)

    warnings = car_service.kiem_tra_canh_bao()
    assert len(warnings) == 2
    assert all(w["ton_kho"] < 3 for w in warnings)


def test_kiem_tra_canh_bao_no_warning(tmp_db):
    car_service.create_car("CAR1", "Toyota", "Camry", 2024, gia_ban=800_000_000, ton_kho=5)
    warnings = car_service.kiem_tra_canh_bao()
    assert len(warnings) == 0