# KẾ HOẠCH HOÀN THÀNH DỰ ÁN

**Phần mềm quản lý đại lý xe hơi**
**Tech stack**: Python 3.10+ • PyQt6 • SQLite • bcrypt • pytest • PyInstaller
**Phạm vi**: 71 chức năng / 15 module (xem `docs/LIST_CHUC_NANG.md`)

---

## 1. NGUYÊN TẮC THỰC HIỆN

| Nguyên tắc                 | Diễn giải                                                                                                |
| -------------------------- | -------------------------------------------------------------------------------------------------------- |
| Kiến trúc phân lớp         | UI (PyQt6) → Service (nghiệp vụ) → Repository (truy vấn) → SQLite. Không gọi SQL trực tiếp từ UI.        |
| Mỗi module một thư mục     | `src/modules/<ten_module>/` chứa `model.py`, `repository.py`, `service.py`, `ui/`.                       |
| Tách giao diện và logic    | UI chỉ bind dữ liệu và gọi service; mọi tính toán/validate nằm ở service.                                |
| Test trước khi gắn UI      | Mỗi service phải có unit test pytest trước khi nối vào UI.                                               |
| Comment tiếng Việt         | Theo yêu cầu phi chức năng 2.5.                                                                          |
| Migration script duy nhất  | Toàn bộ schema SQLite định nghĩa trong `src/db/schema.sql`, seed data trong `src/db/seed.sql`.           |
| Không hard-code đường dẫn  | Dùng `pathlib` + file cấu hình `config.ini` (đường dẫn DB, timeout, mức cảnh báo tồn kho…).              |

---

## 2. KIẾN TRÚC THƯ MỤC ĐỀ XUẤT

```
Car-start/
├── src/
│   ├── main.py                     # Điểm vào ứng dụng, khởi tạo QApplication
│   ├── config.ini                  # Cấu hình (đường dẫn DB, session timeout…)
│   ├── app/
│   │   ├── application.py          # Khởi tạo cửa sổ chính, router module
│   │   ├── session.py              # Quản lý phiên đăng nhập + timeout 30 phút
│   │   └── permissions.py          # Phân quyền Admin / NhanVienBanHang
│   ├── db/
│   │   ├── connection.py           # Singleton kết nối SQLite (foreign_keys = ON)
│   │   ├── schema.sql              # DDL toàn bộ bảng
│   │   ├── seed.sql                # Dữ liệu mẫu (admin mặc định, hãng xe…)
│   │   └── migrations/             # Tùy chọn nếu schema thay đổi
│   ├── core/
│   │   ├── logger.py               # Ghi log hoạt động (bảng activity_log)
│   │   ├── validators.py           # Validate email, SĐT, số tiền…
│   │   ├── pdf_export.py           # Xuất PDF (reportlab) cho hợp đồng/phiếu BH
│   │   └── exceptions.py           # Lớp exception nghiệp vụ
│   ├── modules/
│   │   ├── auth/                   # 15. Bảo mật (login, bcrypt, log)
│   │   ├── employee/               # 3. Nhân viên + KPI
│   │   ├── customer/               # 2. Khách hàng + phân loại
│   │   ├── car/                    # 1. Xe
│   │   ├── inventory/              # 5. Kho xe
│   │   ├── supplier/               # 10. Nhà cung cấp
│   │   ├── accessory/              # 8. Phụ kiện + combo
│   │   ├── promotion/              # 7. Khuyến mãi
│   │   ├── contract/               # 4. Hợp đồng + PDF
│   │   ├── installment/            # 11. Trả góp
│   │   ├── warranty/               # 6. Bảo hành
│   │   ├── aftersales/             # 9. Hậu mãi
│   │   ├── marketing/              # 12. Marketing + Lead
│   │   ├── complaint/              # 13. Khiếu nại
│   │   └── report/                 # 14. Báo cáo thống kê
│   └── ui/
│       ├── main_window.py          # Sidebar + stacked widget các module
│       ├── login_dialog.py
│       ├── widgets/                # Bảng, form chung, date picker, money input
│       └── styles.qss              # Theme chung
├── test/
│   ├── conftest.py                 # Fixture DB tạm
│   ├── test_<module>_service.py    # Unit test cho từng service
│   └── test_integration_<flow>.py  # Test luồng (ví dụ: tạo HĐ → trừ kho → BH)
├── docs/                           # Đã có sẵn
├── plan.md                         # File này
├── README.md
├── requirements.txt                # PyQt6, bcrypt, reportlab, pytest, pyinstaller
└── .gitignore
```

---

## 3. THIẾT KẾ CƠ SỞ DỮ LIỆU (TÓM TẮT)

Toàn bộ bảng tạo trong `src/db/schema.sql`. Dùng SQLite với `PRAGMA foreign_keys = ON;`.

| Nhóm bảng       | Bảng chính                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------------- |
| Người dùng      | `users` (id, username, password_hash, role, employee_id), `activity_log`                                      |
| Nhân viên       | `employees` (id, ho_ten, sdt, email, ngay_vao_lam, trang_thai)                                                |
| Khách hàng      | `customers` (id, ho_ten, sdt, email, dia_chi, hang_khach_hang)                                                |
| Xe              | `cars` (ma_xe PK, hang, dong_xe, nam_sx, mau_sac, gia_ban, ton_kho, trang_thai)                               |
| Kho             | `stock_movements` (id, car_id, supplier_id, so_luong, gia_nhap, ngay)                                         |
| Nhà cung cấp    | `suppliers`, `supplier_ratings`, `purchase_orders`, `purchase_order_items`                                    |
| Phụ kiện        | `accessories` (id, ten, loai, gia, ton_kho), `combo_accessories`, `combo_items`                               |
| Khuyến mãi      | `promotions` (id, ten, loai, muc_giam, kieu_giam, tu_ngay, den_ngay, pham_vi, trang_thai)                     |
| Hợp đồng        | `contracts`, `contract_accessories`, `contract_promotions`                                                    |
| Trả góp         | `installments` (contract_id, ngan_hang, so_tien_vay, lai_suat, so_thang), `installment_payments`              |
| Bảo hành        | `warranties` (contract_id, thoi_han_thang, pham_vi, ngay_bat_dau), `warranty_requests`                        |
| Hậu mãi         | `maintenance_schedules`, `maintenance_history`, `roadside_assistance`                                         |
| Marketing       | `campaigns`, `events`, `leads`                                                                                |
| Khiếu nại       | `complaints` (id, customer_id, noi_dung, muc_do, trang_thai, nhan_vien_xu_ly, danh_gia)                       |

Ràng buộc trọng yếu:

- `cars.ton_kho >= 0` (CHECK).
- Không cho `DELETE` trên `cars` nếu tồn tại `contracts.car_id` tương ứng (xử lý ở service, không dùng cascade).
- Mỗi `contract` có đúng 0 hoặc 1 `warranty`, 0 hoặc 1 `installment`.

---

## 4. CÁC GIAI ĐOẠN PHÁT TRIỂN

> Mỗi giai đoạn = 1 sprint. Kết thúc sprint phải có **bản chạy được** + **test xanh**.

### Giai đoạn 0 — Khởi tạo dự án (0.5 ngày)

- [ ] Tạo `requirements.txt` (PyQt6, bcrypt, reportlab, pytest, pytest-qt, pyinstaller).
- [ ] Tạo `.gitignore` (ẩn `*.db`, `__pycache__`, `dist/`, `build/`).
- [ ] Tạo cấu trúc thư mục như mục 2.
- [ ] Viết `src/main.py` "Hello PyQt6" để xác nhận môi trường.
- [ ] Viết `src/db/connection.py` mở SQLite, bật foreign keys.
- [ ] Viết `src/db/schema.sql` cho **toàn bộ** bảng (kể cả module sẽ làm sau).
- [ ] Viết `src/db/seed.sql`: tạo tài khoản `admin / admin123` (đã bcrypt).
- [ ] Viết `test/conftest.py` cấp fixture `tmp_db`.

**Tiêu chí xong**: chạy `python src/main.py` mở cửa sổ trống; `pytest` chạy được dù chưa có test.

### Giai đoạn 1 — Bảo mật & Nhân viên (1.5 ngày) — Module 15 + 3

- [ ] `auth/service.py`: `login(username, password)` dùng bcrypt; `change_password`.
- [ ] `app/session.py`: lưu user hiện tại, đếm idle time, phát signal hết hạn 30 phút.
- [ ] `app/permissions.py`: decorator `@require_role("admin")`.
- [ ] `core/logger.py`: ghi `activity_log` (user, hành động, bảng, id, thời gian).
- [ ] `employee/`: CRUD nhân viên (chỉ admin); nhân viên thường chỉ xem chính mình.
- [ ] UI: `login_dialog.py`, `main_window.py` với sidebar (chưa active các tab khác).
- [ ] Test: `test_auth_service.py`, `test_employee_service.py`, `test_session_timeout.py`.

**Tiêu chí xong**: đăng nhập admin, đổi mật khẩu, thêm/sửa/xóa nhân viên, log ghi đủ.

### Giai đoạn 2 — Khách hàng & Xe & Kho (2 ngày) — Module 1 + 2 + 5 + 10

- [ ] `customer/service.py`: CRUD + tìm kiếm; hàm `phan_loai(customer_id)` chạy lại khi có hợp đồng mới.
- [ ] `car/service.py`: CRUD; chặn xóa nếu có hợp đồng; tìm kiếm nâng cao (hãng, dòng, năm, giá min/max, trạng thái).
- [ ] `supplier/service.py`: CRUD NCC + đánh giá.
- [ ] `inventory/service.py`: hàm `nhap_kho(car_id, supplier_id, so_luong, gia)` ghi `stock_movements` và cộng `cars.ton_kho`. Cảnh báo khi `ton_kho <= MIN` (đọc từ `config.ini`).
- [ ] UI: 4 tab tương ứng, dùng `QTableView` + `QSortFilterProxyModel`.
- [ ] Test cho từng service, đặc biệt edge case xóa xe có hợp đồng.

**Tiêu chí xong**: nhập kho 10 xe Toyota Vios, sửa giá, tìm kiếm nâng cao trả đúng kết quả.

### Giai đoạn 3 — Phụ kiện & Khuyến mãi (1.5 ngày) — Module 7 + 8

- [ ] `accessory/service.py`: CRUD, phân loại, cảnh báo hết tồn, combo (header + items).
- [ ] `promotion/service.py`: CRUD; hàm `tim_km_ap_dung(car, ngay)` trả về list KM hợp lệ.
- [ ] Hàm `tinh_giam_gia(km, gia_goc)` cho 2 kiểu: số tiền cố định / phần trăm.
- [ ] UI khuyến mãi: phạm vi áp dụng (toàn bộ / hãng / dòng / xe tồn kho > N ngày).
- [ ] Test: `test_promotion_apply.py` với nhiều kịch bản (KM hết hạn, KM bị tạm dừng…).

**Tiêu chí xong**: tạo KM "Giảm 5% cho Toyota tháng 5" và service trả đúng cho xe Toyota.

### Giai đoạn 4 — Hợp đồng + Trả góp + PDF (2.5 ngày) — Module 4 + 11

- [ ] `contract/service.py`:
  - `tao_hop_dong(customer, car, accessories[], promotions[], nhan_vien)` dùng **transaction**: ghi hợp đồng → trừ kho xe → trừ kho phụ kiện → tự áp KM đủ điều kiện.
  - `tinh_tong(contract)` = giá xe + Σ phụ kiện − Σ giảm giá.
  - `cap_nhat_trang_thai(contract_id, status)`: mới tạo → đã thanh toán → đã giao xe → đã hủy. Khi hủy, hoàn kho.
- [ ] `installment/service.py`: tính trả góp theo dư nợ giảm dần hoặc đều; sinh lịch trả; cảnh báo chậm.
- [ ] `core/pdf_export.py`: in hợp đồng PDF (reportlab) — header đại lý, bảng phụ kiện, KM, tổng, chữ ký.
- [ ] UI: wizard tạo hợp đồng (chọn KH → chọn xe → thêm PK → KM tự động → xác nhận).
- [ ] Test: `test_contract_create.py` (kiểm tra trừ kho, áp KM, transaction rollback khi lỗi).

**Tiêu chí xong**: tạo hợp đồng đầy đủ, in PDF mở được; tồn kho và doanh thu cập nhật chính xác.

### Giai đoạn 5 — Bảo hành & Hậu mãi (1.5 ngày) — Module 6 + 9

- [ ] `warranty/service.py`: tự tạo bản ghi BH khi hợp đồng chuyển "đã giao xe"; cảnh báo BH sắp hết (so sánh với `date.today() + 30`).
- [ ] Yêu cầu BH: ghi nhận, phân loại miễn phí/tính phí, in phiếu PDF.
- [ ] `aftersales/service.py`: lịch bảo dưỡng (theo km hoặc tháng), cứu hộ, sinh nhật KH.
- [ ] UI: dashboard "Cảnh báo" hiển thị BH sắp hết, lịch bảo dưỡng tới hạn, tồn kho thấp.

**Tiêu chí xong**: cảnh báo trên dashboard chạy đúng; in phiếu BH PDF.

### Giai đoạn 6 — Marketing & Khiếu nại (1 ngày) — Module 12 + 13

- [ ] `marketing/service.py`: chiến dịch, sự kiện, lead → chuyển lead thành customer.
- [ ] `complaint/service.py`: ghi nhận, phân công, theo dõi trạng thái, đánh giá.
- [ ] UI: dashboard hiệu quả chiến dịch (lead → khách thực) và bảng khiếu nại theo mức độ.

**Tiêu chí xong**: tạo chiến dịch + 3 lead, chuyển 1 lead thành KH, ghi nhận và đóng 1 khiếu nại.

### Giai đoạn 7 — Báo cáo thống kê (1 ngày) — Module 14

- [ ] `report/service.py`:
  - Doanh thu theo ngày/tháng/năm (group by `strftime`).
  - Top 10 xe bán chạy.
  - KPI nhân viên (số HĐ, tổng doanh thu).
  - Top khách hàng VIP theo tổng giá trị.
- [ ] UI: bộ lọc thời gian + biểu đồ (PyQt6 `QtCharts`) + nút xuất CSV/PDF.

**Tiêu chí xong**: 4 báo cáo hiển thị đúng dữ liệu seed.

### Giai đoạn 8 — Hoàn thiện & Đóng gói (1 ngày)

- [ ] Backup tự động: copy `*.db` sang `backups/YYYY-MM-DD.db` mỗi lần khởi động.
- [ ] Áp dụng `styles.qss` cho UI nhất quán.
- [ ] Hướng dẫn sử dụng tích hợp (menu Help → mở `docs/HUONG_DAN.md` trong `QTextBrowser`).
- [ ] Đóng gói PyInstaller: `pyinstaller --noconfirm --windowed --name "QuanLyDaiLyXe" src/main.py`.
- [ ] Cập nhật `README.md` (cách cài, chạy, đóng gói, tài khoản mặc định).
- [ ] Chạy toàn bộ `pytest`, đảm bảo coverage tối thiểu cho service ≥ 70%.

**Tiêu chí xong**: file `dist/QuanLyDaiLyXe.exe` chạy độc lập trên Windows sạch.

---

## 5. CHIẾN LƯỢC KIỂM THỬ

| Loại test       | Phạm vi                                              | Công cụ            |
| --------------- | ---------------------------------------------------- | ------------------ |
| Unit            | Hàm validate, hàm tính giá, hàm phân loại KH         | pytest             |
| Repository      | Truy vấn CRUD trên DB tạm                            | pytest + tmp_path  |
| Service tích hợp| Tạo hợp đồng → trừ kho → áp KM → tạo BH              | pytest             |
| UI smoke (tùy)  | Đăng nhập, mở từng tab không crash                   | pytest-qt          |

Quy tắc: mỗi PR phải kèm test cho hàm mới; không xóa/làm yếu test cũ.

---

## 6. PHỤ THUỘC GIỮA CÁC MODULE

```
auth ─┬─► employee ──┐
      │              ├─► contract ─┬─► warranty
      │  customer ──┤              ├─► installment
      │  car ───────┤              ├─► report
      │  supplier ─►│              └─► aftersales
      │  inventory ►│
      │  accessory ►│
      │  promotion ►┘
      └─► (mọi module ghi log qua core/logger)

marketing ─► customer (lead → customer)
complaint ─► customer + employee
```

Thứ tự triển khai trong mục 4 đã tôn trọng phụ thuộc này.

---

## 7. RỦI RO & GIẢM THIỂU

| Rủi ro                                       | Giảm thiểu                                                              |
| -------------------------------------------- | ----------------------------------------------------------------------- |
| Transaction tạo hợp đồng phức tạp, dễ lỗi    | Bọc trong `with conn: ...`; viết test rollback trước.                   |
| PDF tiếng Việt lỗi font                      | Nhúng font Unicode (DejaVu/Arial) trong `pdf_export.py`.                |
| UI PyQt6 chậm khi bảng > 10k bản ghi         | Dùng `QSqlTableModel` hoặc paging; lazy load.                           |
| Cảnh báo (BH, tồn kho) tản mác               | Tập trung vào 1 service `notification/service.py` gom tất cả về dashboard. |
| 71 chức năng dễ sót                          | Sau mỗi giai đoạn, đối chiếu lại `docs/LIST_CHUC_NANG.md` và tick.       |

---

## 8. CHECKLIST ĐỐI CHIẾU 71 CHỨC NĂNG

Sử dụng làm danh sách nghiệm thu cuối dự án — đánh dấu khi hoàn thành.

- [ ] **Module 1 — Xe (5)**: 1.1 → 1.5
- [ ] **Module 2 — Khách hàng (4)**: 2.1 → 2.4
- [ ] **Module 3 — Nhân viên (5)**: 3.1 → 3.5
- [ ] **Module 4 — Hợp đồng (6)**: 4.1 → 4.6
- [ ] **Module 5 — Kho xe (3)**: 5.1 → 5.3
- [ ] **Module 6 — Bảo hành (7)**: 6.1 → 6.7
- [ ] **Module 7 — Khuyến mãi (7)**: 7.1 → 7.7
- [ ] **Module 8 — Phụ kiện (5)**: 8.1 → 8.5
- [ ] **Module 9 — Hậu mãi (4)**: 9.1 → 9.4
- [ ] **Module 10 — NCC (4)**: 10.1 → 10.4
- [ ] **Module 11 — Trả góp (4)**: 11.1 → 11.4
- [ ] **Module 12 — Marketing (4)**: 12.1 → 12.4
- [ ] **Module 13 — Khiếu nại (5)**: 13.1 → 13.5
- [ ] **Module 14 — Báo cáo (4)**: 14.1 → 14.4
- [ ] **Module 15 — Bảo mật (4)**: 15.1 → 15.4

**Tổng: 0 / 71** → cập nhật sau mỗi giai đoạn.

---

## 9. ƯỚC LƯỢNG THỜI GIAN

| Giai đoạn | Mô tả                       | Thời gian   |
| --------- | --------------------------- | ----------- |
| 0         | Khởi tạo                    | 0.5 ngày    |
| 1         | Bảo mật + Nhân viên         | 1.5 ngày    |
| 2         | KH + Xe + Kho + NCC         | 2.0 ngày    |
| 3         | Phụ kiện + Khuyến mãi       | 1.5 ngày    |
| 4         | Hợp đồng + Trả góp + PDF    | 2.5 ngày    |
| 5         | Bảo hành + Hậu mãi          | 1.5 ngày    |
| 6         | Marketing + Khiếu nại       | 1.0 ngày    |
| 7         | Báo cáo                     | 1.0 ngày    |
| 8         | Hoàn thiện + đóng gói       | 1.0 ngày    |
| **Tổng**  |                             | **≈ 12.5 ngày làm việc** |

---

## 10. BƯỚC TIẾP THEO NGAY

1. Duyệt kế hoạch này.
2. Bắt đầu **Giai đoạn 0**: tạo `requirements.txt`, cấu trúc thư mục, `schema.sql`, `main.py` rỗng.
3. Sau khi xong giai đoạn 0, chuyển sang **Giai đoạn 1 (Bảo mật + Nhân viên)** vì mọi module khác phụ thuộc vào đăng nhập + log.
