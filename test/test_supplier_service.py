"""Test cho supplier service."""
import pytest

from src.modules.supplier import service as supplier_service
from src.core.exceptions import ValidationError, NotFoundError, BusinessError


def test_create_supplier_success(tmp_db):
    sid = supplier_service.create_supplier(
        ten="Toyota Vietnam",
        dia_chi="HCM",
        sdt="0123456789",
        email="contact@toyota.vn",
        nguoi_lien_he="Mr. ABC",
    )
    assert sid > 0
    sup = supplier_service.get_supplier(sid)
    assert sup["ten"] == "Toyota Vietnam"


def test_create_supplier_missing_name(tmp_db):
    with pytest.raises(ValidationError, match="ten"):
        supplier_service.create_supplier(ten="")


def test_update_supplier(tmp_db):
    sid = supplier_service.create_supplier(ten="Test Supplier")
    supplier_service.update_supplier(sid, dia_chi="Hanoi", sdt="0987654321")
    sup = supplier_service.get_supplier(sid)
    assert sup["dia_chi"] == "Hanoi"
    assert sup["sdt"] == "0987654321"


def test_delete_supplier(tmp_db):
    sid = supplier_service.create_supplier(ten="ToDelete")
    supplier_service.delete_supplier(sid)
    with pytest.raises(NotFoundError):
        supplier_service.get_supplier(sid)


def test_add_rating_success(tmp_db):
    sid = supplier_service.create_supplier(ten="Test Supplier")
    rating_id = supplier_service.add_rating(sid, chat_luong=5, thoi_gian_giao=4, gia_ca=4)
    assert rating_id > 0

    ratings = supplier_service.get_ratings(sid)
    assert len(ratings) == 1
    assert ratings[0]["chat_luong"] == 5


def test_add_rating_invalid_score(tmp_db):
    sid = supplier_service.create_supplier(ten="Test Supplier")
    with pytest.raises(ValidationError, match="1 đến 5"):
        supplier_service.add_rating(sid, chat_luong=6, thoi_gian_giao=4, gia_ca=4)


def test_get_average_rating(tmp_db):
    sid = supplier_service.create_supplier(ten="Test Supplier")
    supplier_service.add_rating(sid, 5, 4, 4)
    supplier_service.add_rating(sid, 3, 3, 3)

    avg = supplier_service.get_average_rating(sid)
    assert avg["so_danh_gia"] == 2
    assert 3.5 <= avg["avg_chat_luong"] <= 4.5


def test_get_import_history(tmp_db):
    sid = supplier_service.create_supplier(ten="Test Supplier")
    # Tạo xe và nhập kho
    tmp_db.execute(
        "INSERT INTO cars (ma_xe, hang, dong_xe, nam_sx, gia_ban) VALUES ('CAR1', 'Toyota', 'Camry', 2024, 800000000)"
    )
    tmp_db.execute(
        """
        INSERT INTO stock_movements (car_id, supplier_id, so_luong, gia_nhap)
        VALUES ('CAR1', ?, 5, 700000000)
        """,
        (sid,),
    )
    tmp_db.commit()

    history = supplier_service.get_import_history(sid)
    assert len(history) >= 1
    assert history[0]["so_luong"] == 5


def test_list_suppliers(tmp_db):
    supplier_service.create_supplier(ten="Supplier A")
    supplier_service.create_supplier(ten="Supplier B")
    suppliers = supplier_service.list_suppliers()
    assert len(suppliers) >= 2
    names = [s["ten"] for s in suppliers]
    assert "Supplier A" in names
    assert "Supplier B" in names