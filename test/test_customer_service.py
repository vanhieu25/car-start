"""Test cho customer service."""
import pytest

from src.modules.customer import service as customer_service
from src.core.exceptions import ValidationError, NotFoundError, BusinessError


def test_create_customer_success(tmp_db):
    """Tạo khách hàng thành công."""
    customer_id = customer_service.create_customer(
        ho_ten="Nguyễn Văn A",
        sdt="0123456789",
        email="test@example.com",
    )
    assert customer_id > 0

    cust = customer_service.get_customer(customer_id)
    assert cust["ho_ten"] == "Nguyễn Văn A"
    assert cust["sdt"] == "0123456789"
    assert cust["hang_khach_hang"] == "dong"


def test_create_customer_missing_name(tmp_db):
    with pytest.raises(ValidationError, match="ho_ten"):
        customer_service.create_customer(ho_ten="")


def test_create_customer_invalid_phone(tmp_db):
    with pytest.raises(ValidationError, match="10-11"):
        customer_service.create_customer(ho_ten="Test", sdt="abc123")


def test_update_customer(tmp_db):
    cid = customer_service.create_customer(ho_ten="Test", sdt="0123456789")
    customer_service.update_customer(cid, ho_ten="Updated Name", dia_chi="HCM")
    cust = customer_service.get_customer(cid)
    assert cust["ho_ten"] == "Updated Name"
    assert cust["dia_chi"] == "HCM"


def test_delete_customer_no_contracts(tmp_db):
    cid = customer_service.create_customer(ho_ten="ToDelete")
    customer_service.delete_customer(cid)
    with pytest.raises(NotFoundError):
        customer_service.get_customer(cid)


def test_delete_customer_has_contracts(tmp_db):
    cid = customer_service.create_customer(ho_ten="HasContract")
    # Tạo xe trước để FK không lỗi
    tmp_db.execute(
        "INSERT INTO cars (ma_xe, hang, dong_xe, nam_sx, gia_ban) VALUES ('CAR1', 'Toyota', 'Camry', 2024, 800000000)"
    )
    # Tạo hợp đồng giả
    tmp_db.execute(
        """
        INSERT INTO contracts (ma_hd, customer_id, car_id, gia_xe, tong_thanh_toan)
        VALUES ('HD001', ?, 'CAR1', 500000000, 500000000)
        """,
        (cid,),
    )
    tmp_db.commit()

    with pytest.raises(BusinessError, match="hợp đồng"):
        customer_service.delete_customer(cid)


def test_search_customers(tmp_db):
    customer_service.create_customer(ho_ten="Nguyễn Văn A", sdt="0123456789")
    customer_service.create_customer(ho_ten="Trần Văn B", sdt="0987654321")

    results = customer_service.search_customers("Nguyễn")
    assert len(results) >= 1
    assert any(r["ho_ten"] == "Nguyễn Văn A" for r in results)


def test_phan_loai_dong(tmp_db):
    """Khách chưa có HĐ → Đồng."""
    cid = customer_service.create_customer(ho_ten="NewCust")
    hang = customer_service.phan_loai(cid)
    assert hang == "dong"


def test_phan_loai_bac(tmp_db):
    """1 HĐ và tổng >= 50M → Bạc."""
    cid = customer_service.create_customer(ho_ten="BacCust")
    tmp_db.execute(
        "INSERT INTO cars (ma_xe, hang, dong_xe, nam_sx, gia_ban) VALUES ('CAR1', 'Toyota', 'Camry', 2024, 800000000)"
    )
    tmp_db.execute(
        """
        INSERT INTO contracts (ma_hd, customer_id, car_id, gia_xe, tong_thanh_toan, trang_thai)
        VALUES ('HD001', ?, 'CAR1', 60000000, 60000000, 'moi_tao')
        """,
        (cid,),
    )
    tmp_db.commit()

    hang = customer_service.phan_loai(cid)
    assert hang == "bac"


def test_phan_loai_vang(tmp_db):
    """3 HĐ và tổng >= 200M → Vàng."""
    cid = customer_service.create_customer(ho_ten="VangCust")
    tmp_db.execute(
        "INSERT INTO cars (ma_xe, hang, dong_xe, nam_sx, gia_ban) VALUES ('CAR1', 'Toyota', 'Camry', 2024, 800000000)"
    )
    for i in range(3):
        tmp_db.execute(
            """
            INSERT INTO contracts (ma_hd, customer_id, car_id, gia_xe, tong_thanh_toan, trang_thai)
            VALUES (?, ?, 'CAR1', 80000000, 80000000, 'moi_tao')
            """,
            (f"HD00{i}", cid),
        )
    tmp_db.commit()

    hang = customer_service.phan_loai(cid)
    assert hang == "vang"


def test_phan_loai_kim_cuong(tmp_db):
    """5+ HĐ và tổng >= 500M → Kim cương."""
    cid = customer_service.create_customer(ho_ten="KCCust")
    tmp_db.execute(
        "INSERT INTO cars (ma_xe, hang, dong_xe, nam_sx, gia_ban) VALUES ('CAR1', 'Toyota', 'Camry', 2024, 800000000)"
    )
    for i in range(5):
        tmp_db.execute(
            """
            INSERT INTO contracts (ma_hd, customer_id, car_id, gia_xe, tong_thanh_toan, trang_thai)
            VALUES (?, ?, 'CAR1', 100000000, 100000000, 'moi_tao')
            """,
            (f"HD00{i}", cid),
        )
    tmp_db.commit()

    hang = customer_service.phan_loai(cid)
    assert hang == "kim_cuong"


def test_lay_lich_su(tmp_db):
    cid = customer_service.create_customer(ho_ten="LichSuCust")
    # Tạo xe và hợp đồng
    tmp_db.execute(
        "INSERT INTO cars (ma_xe, hang, dong_xe, nam_sx, gia_ban) VALUES ('CAR1', 'Toyota', 'Camry', 2024, 800000000)"
    )
    tmp_db.execute(
        """
        INSERT INTO contracts (ma_hd, customer_id, car_id, gia_xe, tong_thanh_toan, trang_thai)
        VALUES ('HD001', ?, 'CAR1', 800000000, 800000000, 'da_giao_xe')
        """,
        (cid,),
    )
    tmp_db.commit()

    history = customer_service.lay_lich_su(cid)
    assert len(history) >= 1
    assert history[0]["ma_hd"] == "HD001"