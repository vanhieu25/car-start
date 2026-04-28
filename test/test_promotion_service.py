"""Test cho promotion service."""
import pytest
from datetime import date, timedelta

from src.modules.promotion import service as promo_service
from src.modules.promotion import repository as promo_repo
from src.core.exceptions import ValidationError, NotFoundError

_TODAY = str(date.today())


def test_create_promotion_success(tmp_db):
    promo_id = promo_service.create_promotion(
        ten="Khuyến mãi 1",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=10_000_000,
        pham_vi="toan_bo",
    )
    assert promo_id > 0
    promo = promo_service.get_promotion(promo_id)
    assert promo["ten"] == "Khuyến mãi 1"
    assert promo["trang_thai"] == "dang_chay"


def test_create_promotion_invalid_loai(tmp_db):
    with pytest.raises(ValidationError, match="Loại"):
        promo_service.create_promotion(
            ten="Test", loai="invalid", kieu_giam="co_dinh", muc_giam=1000, pham_vi="toan_bo"
        )


def test_create_promotion_invalid_kieu_giam(tmp_db):
    with pytest.raises(ValidationError, match="Kiểu giảm"):
        promo_service.create_promotion(
            ten="Test", loai="giam_tien", kieu_giam="invalid", muc_giam=1000, pham_vi="toan_bo"
        )


def test_create_promotion_invalid_pham_vi(tmp_db):
    with pytest.raises(ValidationError, match="Phạm vi"):
        promo_service.create_promotion(
            ten="Test", loai="giam_tien", kieu_giam="co_dinh", muc_giam=1000, pham_vi="invalid"
        )


def test_update_promotion(tmp_db):
    promo_id = promo_service.create_promotion(
        ten="Original", loai="giam_tien", kieu_giam="co_dinh", muc_giam=1000, pham_vi="toan_bo"
    )
    promo_service.update_promotion(promo_id, ten="Updated", muc_giam=2000)
    promo = promo_service.get_promotion(promo_id)
    assert promo["ten"] == "Updated"
    assert promo["muc_giam"] == 2000


def test_delete_promotion(tmp_db):
    promo_id = promo_service.create_promotion(
        ten="ToDelete", loai="giam_tien", kieu_giam="co_dinh", muc_giam=1000, pham_vi="toan_bo"
    )
    promo_service.delete_promotion(promo_id)
    with pytest.raises(NotFoundError):
        promo_service.get_promotion(promo_id)


def test_tam_dung_promotion(tmp_db):
    promo_id = promo_service.create_promotion(
        ten="Test", loai="giam_tien", kieu_giam="co_dinh", muc_giam=1000, pham_vi="toan_bo"
    )
    promo_service.tam_dung(promo_id)
    promo = promo_service.get_promotion(promo_id)
    assert promo["trang_thai"] == "tam_dung"


def test_kich_hoat_promotion(tmp_db):
    promo_id = promo_service.create_promotion(
        ten="Test", loai="giam_tien", kieu_giam="co_dinh", muc_giam=1000, pham_vi="toan_bo"
    )
    promo_service.tam_dung(promo_id)
    promo_service.kich_hoat(promo_id)
    promo = promo_service.get_promotion(promo_id)
    assert promo["trang_thai"] == "dang_chay"


def test_find_active_returns_valid(tmp_db):
    promo_service.create_promotion(
        ten="Active Promo",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=1000,
        pham_vi="toan_bo",
        tu_ngay=_TODAY,
        den_ngay=str(date.today() + timedelta(days=30)),
    )
    # Tạo KM đã hết hạn
    promo_service.create_promotion(
        ten="Expired Promo",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=1000,
        pham_vi="toan_bo",
        tu_ngay="2020-01-01",
        den_ngay="2020-01-31",
    )

    active = promo_repo.find_active(_TODAY)
    assert any(p["ten"] == "Active Promo" for p in active)
    assert not any(p["ten"] == "Expired Promo" for p in active)


def test_find_active_excludes_tam_dung(tmp_db):
    promo_id = promo_service.create_promotion(
        ten="TamDungPromo",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=1000,
        pham_vi="toan_bo",
    )
    promo_service.tam_dung(promo_id)

    active = promo_repo.find_active(_TODAY)
    assert not any(p["ten"] == "TamDungPromo" for p in active)


def test_tim_km_ap_dung_toan_bo(tmp_db):
    promo_id = promo_service.create_promotion(
        ten="All Cars",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=10_000_000,
        pham_vi="toan_bo",
    )
    results = promo_service.tim_km_ap_dung(hang="Toyota", dong_xe="Camry")
    assert any(p["id"] == promo_id for p in results)


def test_tim_km_ap_dung_hang_xe(tmp_db):
    promo_service.create_promotion(
        ten="Toyota Only",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=10_000_000,
        pham_vi="hang_xe",
        pham_vi_id="Toyota",
    )
    promo_service.create_promotion(
        ten="Honda Only",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=5_000_000,
        pham_vi="hang_xe",
        pham_vi_id="Honda",
    )

    results = promo_service.tim_km_ap_dung(hang="Toyota", dong_xe="Camry")
    assert any(p["ten"] == "Toyota Only" for p in results)
    assert not any(p["ten"] == "Honda Only" for p in results)


def test_tinh_giam_gia_co_dinh(tmp_db):
    km = {"kieu_giam": "co_dinh", "muc_giam": 10_000_000}
    assert promo_service.tinh_giam_gia(km, 800_000_000) == 10_000_000


def test_tinh_giam_gia_phan_tram(tmp_db):
    km = {"kieu_giam": "phan_tram", "muc_giam": 10}  # 10%
    assert promo_service.tinh_giam_gia(km, 800_000_000) == 80_000_000


def test_get_valid_promotions_with_discount_amount(tmp_db):
    promo_service.create_promotion(
        ten="Test 10%",
        loai="giam_tien",
        kieu_giam="phan_tram",
        muc_giam=10,
        pham_vi="toan_bo",
    )

    results = promo_service.get_valid_promotions(hang="Toyota", dong_xe="Camry", gia_xe=800_000_000)
    assert len(results) >= 1
    promo = next(p for p in results if p["ten"] == "Test 10%")
    assert promo["so_tien_giam"] == 80_000_000


def test_promotion_with_future_start_date(tmp_db):
    future_date = str(date.today() + timedelta(days=7))
    promo_id = promo_service.create_promotion(
        ten="Future Promo",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=1000,
        pham_vi="toan_bo",
        tu_ngay=future_date,
        den_ngay=str(date.today() + timedelta(days=30)),
    )
    # Hôm nay: không nên thấy
    active = promo_repo.find_active(_TODAY)
    assert not any(p["id"] == promo_id for p in active)


def test_promotion_delete(tmp_db):
    promo_id = promo_service.create_promotion(
        ten="Delete Me",
        loai="giam_tien",
        kieu_giam="co_dinh",
        muc_giam=1000,
        pham_vi="toan_bo",
    )
    promo_service.delete_promotion(promo_id)
    promos = promo_service.list_promotions()
    assert not any(p["id"] == promo_id for p in promos)