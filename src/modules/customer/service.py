"""Service nghiệp vụ quản lý khách hàng."""
from src.modules.customer import repository as customer_repo
from src.core.exceptions import ValidationError, NotFoundError, BusinessError
from src.core.validators import validate_phone, validate_email, validate_required
from src.core import logger


# Ngưỡng phân loại khách hàng
_VANG_SO_HD = 3
_VANG_TONG_GT = 200_000_000
_BAC_SO_HD = 2
_BAC_TONG_GT = 50_000_000
_DONG_TONG_GT = 0


def list_customers() -> list[dict]:
    return customer_repo.list_all()


def get_customer(customer_id: int) -> dict:
    result = customer_repo.get_by_id(customer_id)
    if not result:
        raise NotFoundError(f"Không tìm thấy khách hàng id={customer_id}")
    return result


def create_customer(ho_ten: str, sdt: str | None = None, email: str | None = None,
                    dia_chi: str | None = None, ngay_sinh: str | None = None,
                    ghi_chu: str | None = None, current_user: dict | None = None) -> int:
    validate_required({"ho_ten": ho_ten})
    if sdt:
        validate_phone(sdt)
    if email:
        validate_email(email)

    hang = _phan_loai_tu_dong(None)
    customer_id = customer_repo.create(ho_ten, sdt, email, dia_chi, ngay_sinh, hang, ghi_chu)
    if current_user:
        logger.log(current_user.get("id"), "create", "customers", customer_id, f"Thêm khách hàng {ho_ten}")
    return customer_id


def update_customer(customer_id: int, current_user: dict | None = None, **kwargs) -> None:
    if kwargs.get("sdt"):
        validate_phone(kwargs["sdt"])
    if kwargs.get("email"):
        validate_email(kwargs["email"])

    customer_repo.update(customer_id, **kwargs)
    if current_user:
        logger.log(current_user.get("id"), "update", "customers", customer_id, f"Cập nhật khách hàng id={customer_id}")


def delete_customer(customer_id: int, current_user: dict | None = None) -> None:
    if customer_repo.has_contracts(customer_id):
        raise BusinessError("Khách hàng có hợp đồng, không thể xóa.")
    customer_repo.delete(customer_id)
    if current_user:
        logger.log(current_user.get("id"), "delete", "customers", customer_id, f"Xóa khách hàng id={customer_id}")


def search_customers(keyword: str) -> list[dict]:
    if not keyword or len(keyword.strip()) < 2:
        return customer_repo.list_all()
    return customer_repo.search(keyword.strip())


def phan_loai(customer_id: int) -> str:
    """Trả về hạng hiện tại của khách hàng."""
    stats = customer_repo.get_contract_stats(customer_id)
    return _phan_loai_tu_dong(stats)


def _phan_loai_tu_dong(stats: dict | None) -> str:
    so_hd = stats["so_hop_dong"] if stats else 0
    tong_gt = stats["tong_gia_tri"] if stats else 0.0

    if so_hd >= 5 or tong_gt >= 500_000_000:
        return "kim_cuong"
    if so_hd >= 3 or tong_gt >= _VANG_TONG_GT:
        return "vang"
    if so_hd >= 2 or tong_gt >= _BAC_TONG_GT:
        return "bac"
    return "dong"


def cap_nhat_phan_loai(customer_id: int) -> str:
    """Cập nhật lại hạng khách hàng dựa trên hợp đồng hiện tại."""
    stats = customer_repo.get_contract_stats(customer_id)
    hang = _phan_loai_tu_dong(stats)
    customer_repo.update(customer_id, hang_khach_hang=hang)
    return hang


def lay_lich_su(customer_id: int) -> list[dict]:
    """Lấy lịch sử giao dịch của khách hàng (hợp đồng + trả góp)."""
    from src.db.connection import get_connection
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT c.id, c.ma_hd, c.ngay_lap, c.gia_xe, c.tong_phu_kien,
                   c.tong_giam_gia, c.tong_thanh_toan, c.trang_thai,
                   car.hang, car.dong_xe, car.mau_sac,
                   e.ho_ten as nhan_vien
            FROM contracts c
            JOIN cars car ON c.car_id = car.ma_xe
            LEFT JOIN employees e ON c.employee_id = e.id
            WHERE c.customer_id = ?
            ORDER BY c.ngay_lap DESC
            """,
            (customer_id,),
        )
        contracts = [dict(row) for row in cursor.fetchall()]

        for contract in contracts:
            cursor2 = conn.execute(
                """
                SELECT ip.ky, ip.ngay_du_kien, ip.so_tien, ip.ngay_thuc_te, ip.trang_thai,
                       i.ngan_hang, i.so_tien_vay, i.lai_suat, i.so_thang
                FROM installment_payments ip
                JOIN installments i ON ip.contract_id = i.contract_id
                WHERE ip.contract_id = ?
                ORDER BY ip.ky
                """,
                (contract["id"],),
            )
            contract["tra_gop"] = [dict(row) for row in cursor2.fetchall()]
        return contracts
    finally:
        conn.close()