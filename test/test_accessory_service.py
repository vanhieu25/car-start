"""Test cho accessory service."""
import pytest

from src.modules.accessory import service as acc_service
from src.modules.accessory import repository as acc_repo
from src.core.exceptions import ValidationError, NotFoundError, BusinessError


def test_create_accessory_success(tmp_db):
    acc_id = acc_service.create_accessory(
        ten="Camera lùi",
        loai="dien_tu",
        gia=1500000,
        mo_ta="Camera lùi cao cấp",
        ton_kho=10,
    )
    assert acc_id > 0
    acc = acc_service.get_accessory(acc_id)
    assert acc["ten"] == "Camera lùi"
    assert acc["loai"] == "dien_tu"
    assert acc["gia"] == 1500000


def test_create_accessory_invalid_loai(tmp_db):
    with pytest.raises(ValidationError, match="Loại"):
        acc_service.create_accessory(ten="Test", loai="invalid", gia=1000)


def test_create_accessory_negative_price(tmp_db):
    with pytest.raises(ValidationError, match="không được âm"):
        acc_service.create_accessory(ten="Test", loai="dien_tu", gia=-100)


def test_update_accessory(tmp_db):
    acc_id = acc_service.create_accessory(ten="Test", loai="dien_tu", gia=1000, ton_kho=5)
    acc_service.update_accessory(acc_id, gia=2000, ton_kho=3)
    acc = acc_service.get_accessory(acc_id)
    assert acc["gia"] == 2000
    assert acc["ton_kho"] == 3


def test_delete_accessory_no_contracts(tmp_db):
    acc_id = acc_service.create_accessory(ten="ToDelete", loai="dien_tu", gia=1000)
    acc_service.delete_accessory(acc_id)
    with pytest.raises(NotFoundError):
        acc_service.get_accessory(acc_id)


def test_delete_accessory_has_contracts(tmp_db):
    acc_id = acc_service.create_accessory(ten="HasContract", loai="dien_tu", gia=1000)
    # Tạo customer + contract để FK không lỗi
    tmp_db.execute("INSERT INTO customers (ho_ten, sdt) VALUES ('Test', '0123456789')")
    tmp_db.execute(
        "INSERT INTO cars (ma_xe, hang, dong_xe, nam_sx, gia_ban) VALUES ('CAR1', 'T', 'D', 2024, 800000000)"
    )
    tmp_db.execute(
        "INSERT INTO contracts (ma_hd, customer_id, car_id, gia_xe, tong_thanh_toan) VALUES ('HD001', 1, 'CAR1', 800000000, 800000000)"
    )
    tmp_db.execute(
        "INSERT INTO contract_accessories (contract_id, accessory_id, so_luong, gia) VALUES (1, ?, 1, 1000)",
        (acc_id,),
    )
    tmp_db.commit()

    with pytest.raises(BusinessError, match="hợp đồng"):
        acc_service.delete_accessory(acc_id)


def test_search_accessories_by_loai(tmp_db):
    acc_service.create_accessory(ten="Camera", loai="dien_tu", gia=1000)
    acc_service.create_accessory(ten="Thảm", loai="noi_that", gia=500)
    acc_service.create_accessory(ten="Đèn", loai="dien_tu", gia=800)

    results = acc_service.search_accessories({"loai": "dien_tu"})
    assert all(r["loai"] == "dien_tu" for r in results)


def test_kiem_tra_het_pk(tmp_db):
    acc_service.create_accessory(ten="Hết 1", loai="dien_tu", gia=1000, ton_kho=0)
    acc_service.create_accessory(ten="Hết 2", loai="dien_tu", gia=1000, ton_kho=0)
    acc_service.create_accessory(ten="Còn", loai="dien_tu", gia=1000, ton_kho=5)

    out = acc_service.kiem_tra_het_pk()
    assert len(out) == 2


def test_kiem_tra_canh_bao_pk(tmp_db):
    acc_service.create_accessory(ten="Thấp 1", loai="dien_tu", gia=1000, ton_kho=1)
    acc_service.create_accessory(ten="Thấp 2", loai="dien_tu", gia=1000, ton_kho=2)
    acc_service.create_accessory(ten="OK", loai="dien_tu", gia=1000, ton_kho=5)

    warnings = acc_service.kiem_tra_canh_bao_pk()
    assert len(warnings) == 2


# --- Combo ---
def test_create_combo_success(tmp_db):
    acc1_id = acc_service.create_accessory(ten="Acc1", loai="dien_tu", gia=1000)
    acc2_id = acc_service.create_accessory(ten="Acc2", loai="dien_tu", gia=2000)

    combo_id = acc_service.create_combo(
        ten="Combo 1",
        gia_combo=2500,
        items=[{"accessory_id": acc1_id, "so_luong": 1}, {"accessory_id": acc2_id, "so_luong": 2}],
    )
    assert combo_id > 0
    combo = acc_service.get_combo(combo_id)
    assert combo["ten"] == "Combo 1"
    assert combo["gia_combo"] == 2500

    items = acc_service.get_combo_items(combo_id)
    assert len(items) == 2


def test_create_combo_without_items(tmp_db):
    combo_id = acc_service.create_combo(ten="Empty Combo", gia_combo=1000)
    assert combo_id > 0


def test_update_combo(tmp_db):
    combo_id = acc_service.create_combo(ten="Original", gia_combo=1000)
    acc_service.update_combo(combo_id, ten="Updated", gia_combo=1500)
    combo = acc_service.get_combo(combo_id)
    assert combo["ten"] == "Updated"
    assert combo["gia_combo"] == 1500


def test_update_combo_items(tmp_db):
    acc1_id = acc_service.create_accessory(ten="Acc1", loai="dien_tu", gia=1000)
    acc2_id = acc_service.create_accessory(ten="Acc2", loai="dien_tu", gia=2000)

    combo_id = acc_service.create_combo(ten="Test Combo", gia_combo=1000)
    acc_service.update_combo_items(combo_id, [{"accessory_id": acc1_id, "so_luong": 1}])

    items = acc_service.get_combo_items(combo_id)
    assert len(items) == 1

    acc_service.update_combo_items(combo_id, [
        {"accessory_id": acc1_id, "so_luong": 1},
        {"accessory_id": acc2_id, "so_luong": 2},
    ])
    items = acc_service.get_combo_items(combo_id)
    assert len(items) == 2


def test_delete_combo(tmp_db):
    combo_id = acc_service.create_combo(ten="ToDelete", gia_combo=1000)
    acc_service.delete_combo(combo_id)
    with pytest.raises(NotFoundError):
        acc_service.get_combo(combo_id)


def test_list_combos(tmp_db):
    acc_service.create_combo(ten="Combo A", gia_combo=1000)
    acc_service.create_combo(ten="Combo B", gia_combo=2000)
    combos = acc_service.list_combos()
    assert len(combos) == 2
    names = [c["ten"] for c in combos]
    assert "Combo A" in names
    assert "Combo B" in names