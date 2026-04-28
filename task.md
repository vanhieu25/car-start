# DANH SÁCH TASK HOÀN THÀNH DỰ ÁN

**Phần mềm quản lý đại lý xe hơi** • Tham chiếu kế hoạch tổng: `plan.md`

## Quy ước

- **Flow chuẩn cho mỗi phase**: `[Xác định feature]` → `[Database]` → `[Backend Logic]` → `[UI Design]` → `[Testing]` → `[Git Commit]`.
- **Checkbox**: `[ ]` chưa làm, `[x]` đã xong.
- **Quy ước commit** (Conventional Commits):
  - `feat(<module>): ...` — thêm tính năng mới
  - `fix(<module>): ...` — sửa lỗi
  - `refactor(<module>): ...` — tái cấu trúc
  - `test(<module>): ...` — thêm/sửa test
  - `chore: ...` — cấu hình, build, không liên quan code nghiệp vụ
  - `docs: ...` — tài liệu
- **Quy tắc**: không chuyển sang phase kế tiếp khi `pytest` chưa xanh và chưa commit phase hiện tại.

---

# PHASE 0 — KHỞI TẠO PROJECT (≈ 0.5 ngày)

## 0.1. Xác định scope khởi tạo

- [x] Đọc lại `docs/TECH_STACK.md`, `docs/YEU_CAU_CHUC_NANG.md`, `docs/LIST_CHUC_NANG.md`.
- [x] Chốt phiên bản: Python 3.10+, PyQt6 ≥ 6.6, SQLite (stdlib), bcrypt ≥ 4.0, reportlab ≥ 4.0, pytest ≥ 8.0, pytest-qt, pyinstaller ≥ 6.0.
- [x] Chốt cấu trúc thư mục theo `plan.md` mục 2.

## 0.2. Database

- [x] Tạo `src/db/connection.py`: hàm `get_connection()` mở SQLite, bật `PRAGMA foreign_keys = ON`, `PRAGMA journal_mode = WAL`.
- [x] Tạo `src/db/schema.sql` chứa **tất cả** bảng cho 15 module (chưa cần đầy đủ logic, chỉ cần định nghĩa cột + FK + CHECK cơ bản).
- [x] Tạo `src/db/seed.sql`: 1 tài khoản `admin / admin123` (bcrypt hash), 1 employee admin mặc định.
- [x] Viết `src/db/init_db.py`: xóa DB cũ → chạy `schema.sql` → chạy `seed.sql`.

## 0.3. Backend Logic

- [x] Tạo `requirements.txt` theo danh sách ở 0.1.
- [x] Tạo `src/main.py`: khởi tạo `QApplication`, gọi `init_db` nếu DB chưa tồn tại, mở `MainWindow` rỗng.
- [x] Tạo skeleton package: `src/app/`, `src/core/`, `src/modules/<15_thư_mục>/`, `src/ui/` với `__init__.py` rỗng.
- [x] Tạo `src/config.ini` (đường dẫn DB, session timeout = 1800s, MIN_STOCK = 3).
- [x] Tạo `src/core/config_loader.py` đọc `config.ini`.

## 0.4. UI Design
- [x] `src/ui/main_window.py`: cửa sổ chính có sidebar trống + status bar (chưa cần tab nào).
- [x] Tạo `src/ui/styles.qss` rỗng (sẽ thêm style ở Phase 8).

## 0.5. Testing

- [x] Tạo `test/conftest.py`: fixture `tmp_db` cấp DB SQLite tạm cho mỗi test.
- [x] Tạo `test/test_smoke.py`: import `src.main`, kiểm tra `init_db` chạy không lỗi.
- [x] Chạy `pytest` — phải pass.

## 0.6. Git Commit

- [x] Tạo `.gitignore` (`__pycache__/`, `*.db`, `dist/`, `build/`, `*.spec`, `.venv/`).
- [ ] Commit: `chore: scaffold project structure, db schema, smoke test`.

---

# PHASE 1 — BẢO MẬT + NHÂN VIÊN (≈ 1.5 ngày) — Module 15 + 3

## 1.1. Xác định feature

- [ ] **15.1** Đăng nhập, **15.2** bcrypt, **15.3** activity log, **15.4** session timeout 30 phút.
- [ ] **3.1–3.5** CRUD nhân viên (admin only) + nhân viên tự xem thông tin + KPI (KPI tính ở Phase 4 sau khi có hợp đồng, ở đây chỉ chừa cột).

## 1.2. Database

- [ ] Bảng `users(id, username UNIQUE, password_hash, role, employee_id FK, is_active, created_at)`.
- [ ] Bảng `employees(id, ho_ten, sdt, email UNIQUE, ngay_vao_lam, trang_thai, ghi_chu)`.
- [ ] Bảng `activity_log(id, user_id, hanh_dong, bang, ban_ghi_id, thoi_gian, chi_tiet)`.
- [ ] Cập nhật `seed.sql`: gắn `employee_id` cho admin.

## 1.3. Backend Logic

- [ ] `src/modules/auth/repository.py`: `get_user_by_username`, `update_password`.
- [ ] `src/modules/auth/service.py`: `login(username, password)`, `change_password`, `hash_password`, `verify_password`.
- [ ] `src/app/session.py`: lớp `Session` lưu user hiện tại + `QTimer` đếm idle, signal `expired`.
- [ ] `src/app/permissions.py`: decorator `@require_role("admin")`, raise `PermissionDenied`.
- [ ] `src/core/logger.py`: hàm `log(action, table, record_id, detail)` ghi `activity_log`.
- [ ] `src/core/exceptions.py`: `BusinessError`, `PermissionDenied`, `ValidationError`.
- [ ] `src/core/validators.py`: `validate_email`, `validate_phone`, `validate_required`.
- [ ] `src/modules/employee/repository.py` + `service.py`: CRUD + `get_my_profile(user_id)`.

## 1.4. UI Design
- [ ] Đọc tài liệu thiết kế UI từ file `design/DESIGN-apple.md`.
- [ ] `src/ui/login_dialog.py`: form đăng nhập, hiển thị lỗi sai mật khẩu.
- [ ] Cập nhật `main_window.py`: kiểm tra session, nhận user sau login, hiển thị tên + role ở status bar.
- [ ] `src/modules/employee/ui/employee_view.py`: `QTableView` danh sách + nút Thêm/Sửa/Xóa (ẩn nếu không phải admin).
- [ ] `src/modules/employee/ui/employee_form.py`: dialog form thêm/sửa.
- [ ] Gắn timeout: khi `Session.expired` → đóng main, mở lại login.

## 1.5. Testing

- [ ] `test/test_auth_service.py`: login đúng, sai password, user bị disable.
- [ ] `test/test_password_hash.py`: bcrypt verify đúng.
- [ ] `test/test_employee_service.py`: CRUD + chặn nhân viên thường xóa nhân viên khác.
- [ ] `test/test_session_timeout.py`: simulate idle > timeout → `expired` được phát.
- [ ] `test/test_activity_log.py`: mọi hành động write đều ghi log.

## 1.6. Git Commit

- [ ] `feat(auth): login with bcrypt, session timeout, permission decorator`.
- [ ] `feat(employee): CRUD employees with admin-only guard`.
- [ ] `test(auth,employee): unit tests for auth, session, employee CRUD`.

---

# PHASE 2 — KHÁCH HÀNG + XE + KHO + NCC (≈ 2 ngày) — Module 1 + 2 + 5 + 10

## 2.1. Xác định feature

- [ ] **1.1–1.5** CRUD xe + tìm kiếm nâng cao + lọc trạng thái.
- [ ] **2.1–2.4** CRUD khách hàng + lịch sử (placeholder, sẽ điền ở Phase 4) + phân loại tự động.
- [ ] **5.1–5.3** Cập nhật tồn kho + cảnh báo + lịch sử nhập.
- [ ] **10.1–10.4** CRUD NCC + lịch sử nhập + đánh giá + đơn đặt hàng.

## 2.2. Database

- [ ] `customers(id, ho_ten, sdt, email, dia_chi, ngay_sinh, hang_khach_hang, ghi_chu)`.
- [ ] `cars(ma_xe PK, hang, dong_xe, nam_sx, mau_sac, gia_ban, ton_kho CHECK >= 0, trang_thai)`.
- [ ] `suppliers(id, ten, dia_chi, sdt, email, nguoi_lien_he)`.
- [ ] `supplier_ratings(id, supplier_id, chat_luong, thoi_gian_giao, gia_ca, ghi_chu, ngay_danh_gia)`.
- [ ] `stock_movements(id, car_id, supplier_id, so_luong, gia_nhap, ngay_nhap, ghi_chu)`.
- [ ] `purchase_orders(id, supplier_id, ngay_dat, trang_thai)` + `purchase_order_items(po_id, car_id|accessory_id, so_luong, gia)`.

## 2.3. Backend Logic

- [ ] `customer/repository.py` + `service.py`: CRUD, tìm kiếm theo tên/SĐT/email, hàm `phan_loai(customer_id)` (Đồng/Bạc/Vàng/Kim cương dựa trên số HĐ + tổng giá trị — đặt ngưỡng trong `config.ini`).
- [ ] `car/repository.py` + `service.py`: CRUD, `tim_kiem(filters: dict)`, `xoa(ma_xe)` chặn nếu có hợp đồng (kiểm tra qua repository).
- [ ] `supplier/service.py`: CRUD + `them_danh_gia()`.
- [ ] `inventory/service.py`: `nhap_kho(car_id, supplier_id, so_luong, gia)`, `kiem_tra_canh_bao()` trả list xe có `ton_kho < MIN_STOCK`.
- [ ] Mọi hành động write đều gọi `core.logger.log`.

## 2.4. UI Design
- [ ] Đọc tài liệu thiết kế UI từ file `design/DESIGN-apple.md`.
- [ ] `customer/ui/customer_view.py` + `customer_form.py`.
- [ ] `car/ui/car_view.py` + `car_form.py` + `car_search_dialog.py` (tìm kiếm nâng cao theo nhiều tiêu chí).
- [ ] `supplier/ui/supplier_view.py` + form + tab "Đánh giá".
- [ ] `inventory/ui/stock_view.py`: bảng tồn kho + nút "Nhập kho" + bảng "Lịch sử nhập".
- [ ] Thêm 4 tab tương ứng vào sidebar `main_window.py`.

## 2.5. Testing

- [ ] `test_customer_service.py`: CRUD + phân loại đúng theo ngưỡng.
- [ ] `test_car_service.py`: CRUD, tìm kiếm nhiều tiêu chí, chặn xóa khi có HĐ (mock).
- [ ] `test_inventory_service.py`: nhập kho cộng đúng `ton_kho`, cảnh báo trả đúng list.
- [ ] `test_supplier_service.py`: CRUD + thêm đánh giá.

## 2.6. Git Commit

- [ ] `feat(customer): CRUD with auto classification`.
- [ ] `feat(car): CRUD with advanced search and delete guard`.
- [ ] `feat(supplier): CRUD and ratings`.
- [ ] `feat(inventory): stock movement and low-stock alert`.
- [ ] `test: services for customer, car, supplier, inventory`.

---

# PHASE 3 — PHỤ KIỆN + KHUYẾN MÃI (≈ 1.5 ngày) — Module 7 + 8

## 3.1. Xác định feature

- [ ] **8.1–8.5** Danh mục PK + phân loại + cảnh báo + combo + thêm vào HĐ (logic "thêm vào HĐ" sẽ dùng ở Phase 4).
- [ ] **7.1–7.7** CRUD khuyến mãi + loại KM + phạm vi áp dụng + tự áp dụng + dừng/tạm dừng.

## 3.2. Database

- [ ] `accessories(id, ten, mo_ta, loai, gia, ton_kho)`.
- [ ] `combo_accessories(id, ten, gia_combo, mo_ta)` + `combo_items(combo_id, accessory_id, so_luong)`.
- [ ] `promotions(id, ten, mo_ta, loai, kieu_giam, muc_giam, tu_ngay, den_ngay, pham_vi, pham_vi_id, dieu_kien_ton_kho_ngay, trang_thai)`.

## 3.3. Backend Logic

- [ ] `accessory/service.py`: CRUD + `kiem_tra_het_pk()` + CRUD combo.
- [ ] `promotion/service.py`:
  - CRUD + `tam_dung(id)` / `kich_hoat(id)`.
  - `tim_km_ap_dung(car, ngay)` trả list KM hợp lệ (theo phạm vi: toàn bộ / hãng / dòng / xe tồn kho > N ngày).
  - `tinh_giam_gia(km, gia_goc)` cho 2 kiểu: cố định / phần trăm.

## 3.4. UI Design
- [ ] Đọc tài liệu thiết kế UI từ file `design/DESIGN-apple.md`.
- [ ] `accessory/ui/accessory_view.py` + `accessory_form.py` + tab "Combo".
- [ ] `promotion/ui/promotion_view.py` + `promotion_form.py` (combobox phạm vi, datepicker, radio kiểu giảm).
- [ ] Thêm 2 tab vào sidebar.

## 3.5. Testing

- [ ] `test_accessory_service.py`: CRUD, combo, cảnh báo hết.
- [ ] `test_promotion_service.py`: tìm KM theo từng phạm vi, KM hết hạn không trả về, KM tạm dừng không trả về.
- [ ] `test_promotion_calc.py`: tính giảm giá cố định + phần trăm + nhiều KM cộng dồn (theo quy tắc đã chốt).

## 3.6. Git Commit

- [ ] `feat(accessory): CRUD, categories, combo, low-stock alert`.
- [ ] `feat(promotion): CRUD, scope filtering, calculation engine`.
- [ ] `test: accessory and promotion services`.

---

# PHASE 4 — HỢP ĐỒNG + TRẢ GÓP + PDF (≈ 2.5 ngày) — Module 4 + 11 (lõi nghiệp vụ)

## 4.1. Xác định feature

- [ ] **4.1–4.6** Tạo HĐ + tự tính giá + thêm PK + tự áp KM + cập nhật trạng thái + in PDF.
- [ ] **11.1–11.4** Trả góp: thông tin + tính tiền tháng + tiến độ + cảnh báo chậm.
- [ ] Cập nhật KPI nhân viên (3.5) và lịch sử khách hàng (2.3) sau khi có HĐ.

## 4.2. Database

- [ ] `contracts(id, ma_hd UNIQUE, customer_id, car_id, employee_id, ngay_lap, gia_xe, tong_phu_kien, tong_giam_gia, tong_thanh_toan, trang_thai, ghi_chu)`.
- [ ] `contract_accessories(contract_id, accessory_id, so_luong, gia)`.
- [ ] `contract_promotions(contract_id, promotion_id, so_tien_giam)`.
- [ ] `installments(contract_id PK, ngan_hang, so_tien_vay, lai_suat, so_thang, kieu_tinh, ngay_bat_dau)`.
- [ ] `installment_payments(id, contract_id, ky, ngay_du_kien, so_tien, ngay_thuc_te, trang_thai)`.

## 4.3. Backend Logic

- [ ] `contract/service.py`:
  - `tao_hop_dong(...)` chạy trong transaction `with conn:`:
    1. Validate (KH, xe tồn kho ≥ 1, PK đủ tồn kho).
    2. Insert `contracts`, `contract_accessories`.
    3. Gọi `promotion.tim_km_ap_dung`, tính `contract_promotions`.
    4. Trừ `cars.ton_kho`, trừ `accessories.ton_kho`.
    5. Tính `tong_thanh_toan`.
    6. Log activity.
  - `cap_nhat_trang_thai(id, status)`: chuyển trạng thái có ràng buộc; nếu hủy → hoàn kho.
  - `tinh_tong(contract)`.
  - `lay_lich_su_kh(customer_id)`.
  - `kpi_nhan_vien(employee_id, tu, den)`.
- [ ] `installment/service.py`:
  - `tao_tra_gop(contract_id, ngan_hang, so_tien, lai, thang, kieu)`.
  - `tinh_lich_tra(...)` cho 2 kiểu: dư nợ giảm dần + trả đều.
  - `ghi_nhan_thanh_toan(payment_id, ngay)`.
  - `canh_bao_cham_tra()` trả list payment quá hạn.
- [ ] `core/pdf_export.py`:
  - Hàm `xuat_hop_dong_pdf(contract_id, output_path)` dùng reportlab, nhúng font Unicode (DejaVuSans).
  - Layout: header đại lý → thông tin KH/xe → bảng PK → bảng KM → tổng → chữ ký.

## 4.4. UI Design
- [ ] Đọc tài liệu thiết kế UI từ file `design/DESIGN-apple.md`.
- [ ] `contract/ui/contract_view.py`: bảng HĐ + filter trạng thái + nút In PDF + nút đổi trạng thái.
- [ ] `contract/ui/contract_wizard.py` (QWizard 4 trang): KH → Xe → Phụ kiện → Xác nhận (hiển thị KM tự áp + tổng).
- [ ] `installment/ui/installment_view.py`: bảng HĐ trả góp + bảng kỳ + đánh dấu đã trả.
- [ ] Cập nhật `customer_view`: tab "Lịch sử giao dịch".
- [ ] Cập nhật `employee_view`: cột "KPI" (số HĐ, doanh thu).

## 4.5. Testing

- [ ] `test_contract_create.py`: tạo HĐ trừ kho đúng, áp đúng KM, log đầy đủ.
- [ ] `test_contract_rollback.py`: nếu insert PK lỗi → kho xe không bị trừ (rollback).
- [ ] `test_contract_status.py`: hủy HĐ → hoàn kho.
- [ ] `test_installment_calc.py`: 2 kiểu tính ra đúng số tiền (so với công thức tay).
- [ ] `test_pdf_export.py`: file PDF được tạo, dung lượng > 0, mở được (kiểm tra magic bytes `%PDF`).
- [ ] `test_kpi.py`: KPI nhân viên đúng theo HĐ test.

## 4.6. Git Commit

- [ ] `feat(contract): create with transaction, auto promotion, status flow`.
- [ ] `feat(contract): PDF export with Unicode font`.
- [ ] `feat(installment): payment schedule and overdue alert`.
- [ ] `feat(employee): KPI from contracts`.
- [ ] `test: contract transaction, rollback, installment, pdf export`.

---

# PHASE 5 — BẢO HÀNH + HẬU MÃI (≈ 1.5 ngày) — Module 6 + 9

## 5.1. Xác định feature

- [ ] **6.1–6.7** BH: ghi nhận khi giao xe + theo dõi + cảnh báo trước 30 ngày + tiếp nhận yêu cầu + phân loại + in phiếu PDF + thống kê.
- [ ] **9.1–9.4** Hậu mãi: lịch bảo dưỡng + lịch sử + cứu hộ + chăm sóc KH (sinh nhật, tri ân).

## 5.2. Database

- [ ] `warranties(contract_id PK, thoi_han_thang, pham_vi, ngay_bat_dau, ngay_ket_thuc)`.
- [ ] `warranty_requests(id, warranty_id, ngay_den, noi_dung, loai, chi_phi, nhan_vien_id)`.
- [ ] `maintenance_schedules(id, contract_id, kieu_nhac, gia_tri, ngay_du_kien, da_thuc_hien)`.
- [ ] `maintenance_history(id, contract_id, ngay, noi_dung, chi_phi)`.
- [ ] `roadside_assistance(id, contract_id, ngay, noi_dung, phan_hoi, chi_phi)`.

## 5.3. Backend Logic

- [ ] `warranty/service.py`:
  - Hook: khi `contract.cap_nhat_trang_thai → "đã giao xe"` → tự tạo `warranties` (mặc định 36 tháng — đọc config).
  - `canh_bao_sap_het(today)` trả list BH có `ngay_ket_thuc - today <= 30`.
  - `tiep_nhan_yeu_cau(...)`, `thong_ke_chi_phi(tu, den)`.
- [ ] `aftersales/service.py`:
  - Tạo lịch bảo dưỡng theo km hoặc tháng.
  - `nhac_lich(today)` trả list lịch tới hạn.
  - `khach_sinh_nhat_thang(month)` để gửi thiệp.
- [ ] `core/pdf_export.py`: thêm `xuat_phieu_bao_hanh_pdf(request_id, output)`.
- [ ] Tạo `notification/service.py` gom 3 nguồn cảnh báo: BH sắp hết + bảo dưỡng tới hạn + tồn kho thấp.

## 5.4. UI Design
- [ ] Đọc tài liệu thiết kế UI từ file `design/DESIGN-apple.md`.
- [ ] `warranty/ui/warranty_view.py` + tab "Yêu cầu BH" + nút In phiếu.
- [ ] `aftersales/ui/maintenance_view.py` + `roadside_view.py` + `birthday_view.py`.
- [ ] `src/ui/dashboard.py`: trang "Cảnh báo" hiển thị từ `notification.service` (badge số lượng trên sidebar).

## 5.5. Testing

- [ ] `test_warranty_auto_create.py`: chuyển HĐ "đã giao xe" → tự tạo BH.
- [ ] `test_warranty_alert.py`: cảnh báo trả đúng list trong 30 ngày.
- [ ] `test_maintenance_schedule.py`: lịch sinh ra đúng theo km/tháng.
- [ ] `test_notification_service.py`: gom đủ 3 loại cảnh báo.

## 5.6. Git Commit

- [ ] `feat(warranty): auto-create on delivery, alert, request, PDF voucher`.
- [ ] `feat(aftersales): maintenance, roadside, birthday care`.
- [ ] `feat(notification): unified dashboard alerts`.
- [ ] `test: warranty auto-create, alert, maintenance scheduling`.

---

# PHASE 6 — MARKETING + KHIẾU NẠI (≈ 1 ngày) — Module 12 + 13

## 6.1. Xác định feature

- [ ] **12.1–12.4** Chiến dịch + theo dõi hiệu quả + sự kiện + lead → KH.
- [ ] **13.1–13.5** Ghi nhận + phân công + theo dõi + đánh giá + báo cáo khiếu nại.

## 6.2. Database

- [ ] `campaigns(id, ten, ngan_sach, tu_ngay, den_ngay, kenh, ghi_chu)`.
- [ ] `events(id, ten, kieu, ngay, dia_diem, campaign_id)`.
- [ ] `leads(id, ho_ten, sdt, email, nguon, campaign_id, trang_thai, customer_id)`.
- [ ] `complaints(id, customer_id, noi_dung, muc_do, ngay, nhan_vien_xu_ly_id, trang_thai, danh_gia, ghi_chu)`.

## 6.3. Backend Logic

- [ ] `marketing/service.py`: CRUD chiến dịch, sự kiện, lead; `chuyen_lead_thanh_kh(lead_id)` insert customer + cập nhật lead; `hieu_qua_chien_dich(id)` trả số lead, số chuyển đổi.
- [ ] `complaint/service.py`: CRUD + `phan_cong(id, employee_id)` + `cap_nhat_trang_thai` + `bao_cao(tu, den, theo)`.

## 6.4. UI Design
- [ ] Đọc tài liệu thiết kế UI từ file `design/DESIGN-apple.md`.
- [ ] `marketing/ui/campaign_view.py` + `event_view.py` + `lead_view.py` (với nút "Chuyển thành KH").
- [ ] `complaint/ui/complaint_view.py` + form + bảng báo cáo.

## 6.5. Testing

- [ ] `test_marketing_service.py`: chuyển lead → kiểm tra customer mới + lead cập nhật.
- [ ] `test_campaign_effectiveness.py`: số liệu hiệu quả đúng.
- [ ] `test_complaint_service.py`: phân công + chuyển trạng thái + báo cáo nhóm theo mức độ.

## 6.6. Git Commit

- [ ] `feat(marketing): campaigns, events, leads, lead-to-customer`.
- [ ] `feat(complaint): record, assign, track, report`.
- [ ] `test: marketing and complaint services`.

---

# PHASE 7 — BÁO CÁO THỐNG KÊ (≈ 1 ngày) — Module 14

## 7.1. Xác định feature

- [ ] **14.1** Doanh thu theo ngày/tháng/năm.
- [ ] **14.2** Top 10 xe bán chạy.
- [ ] **14.3** Hiệu suất nhân viên (KPI).
- [ ] **14.4** Khách hàng VIP theo tổng giá trị.

## 7.2. Database

- [ ] Không thêm bảng. Tạo VIEW (tùy chọn): `v_revenue_daily`, `v_top_cars`, `v_employee_kpi`, `v_vip_customers` để tăng tốc query.

## 7.3. Backend Logic

- [ ] `report/service.py`:
  - `doanh_thu(tu, den, group_by)` (`day` | `month` | `year`) — dùng `strftime`.
  - `top_xe_ban_chay(n=10, tu, den)`.
  - `kpi_nhan_vien(tu, den)` — sắp xếp giảm dần doanh thu.
  - `khach_hang_vip(n=10)`.
- [ ] `core/csv_export.py`: hàm `export_csv(rows, headers, path)`.

## 7.4. UI Design
- [ ] Đọc tài liệu thiết kế UI từ file `design/DESIGN-apple.md`.
- [ ] `report/ui/report_view.py`: combobox loại báo cáo + datepicker từ/đến + nút "Xuất CSV" + nút "Xuất PDF".
- [ ] Tích hợp `QtCharts`: bar chart doanh thu, pie chart top xe.

## 7.5. Testing

- [ ] `test_report_revenue.py`: nhập dữ liệu fixture, doanh thu group by `day/month/year` đúng.
- [ ] `test_report_top.py`: top xe và VIP đúng thứ tự.
- [ ] `test_csv_export.py`: file CSV đúng số dòng + header.

## 7.6. Git Commit

- [ ] `feat(report): revenue, top cars, employee KPI, VIP customers`.
- [ ] `feat(report): chart visualization and CSV export`.
- [ ] `test: report aggregations and CSV export`.

---

# PHASE 8 — HOÀN THIỆN + ĐÓNG GÓI (≈ 1 ngày)

## 8.1. Xác định scope hoàn thiện

- [ ] Đối chiếu `docs/LIST_CHUC_NANG.md`: tick đủ 71/71 chức năng trong `plan.md` mục 8.
- [ ] Rà UX: phím tắt cơ bản (Ctrl+N thêm mới, Ctrl+S lưu, Esc đóng dialog, F5 reload bảng).
- [ ] Rà phi chức năng: backup, hướng dẫn, tài khoản mặc định.

## 8.2. Database

- [ ] Cơ chế backup: khi khởi động copy `app.db` → `backups/YYYY-MM-DD_HHmmss.db`, giữ lại 14 bản gần nhất.
- [ ] Tạo script `tools/reset_db.py` để dev reset DB nhanh.

## 8.3. Backend Logic

- [ ] `core/backup.py`: hàm `backup_now()` + dọn bản cũ.
- [ ] Tích hợp gọi `backup_now()` ở `main.py` trước khi `init_db`.
- [ ] Kiểm tra mọi service đều `try/except` → hiển thị `QMessageBox` thân thiện thay vì crash.

## 8.4. UI Design
- [ ] Đọc tài liệu thiết kế UI từ file `design/DESIGN-apple.md`.
- [ ] Hoàn thiện `src/ui/styles.qss`: theme sáng đồng bộ, padding, font Segoe UI 10pt.
- [ ] Menu **Help → Hướng dẫn sử dụng** mở `docs/HUONG_DAN.md` trong `QTextBrowser`.
- [ ] Menu **Help → Giới thiệu** hiển thị version + tác giả.
- [ ] Tạo `docs/HUONG_DAN.md` mô tả cách sử dụng từng module (theo flow đăng nhập → tạo HĐ).

## 8.5. Testing

- [ ] Chạy lại **toàn bộ** `pytest`, đảm bảo xanh.
- [ ] Đo coverage `pytest --cov=src`, đảm bảo service ≥ 70%.
- [ ] Test thủ công theo checklist 71 chức năng.
- [ ] Đóng gói thử: `pyinstaller --noconfirm --windowed --name "QuanLyDaiLyXe" --add-data "src/db/schema.sql;db" --add-data "src/db/seed.sql;db" --add-data "src/config.ini;." src/main.py`.
- [ ] Chạy file `dist/QuanLyDaiLyXe/QuanLyDaiLyXe.exe` trên Windows sạch (hoặc máy ảo) — login + tạo HĐ test thành công.

## 8.6. Git Commit

- [ ] `feat(core): auto backup on startup`.
- [ ] `feat(ui): help menu, user guide, theme polish`.
- [ ] `docs: user guide`.
- [ ] `chore(release): pyinstaller spec and packaging`.
- [ ] Tag phiên bản: `git tag -a v1.0.0 -m "Release 1.0.0"`.

---

# TỔNG KẾT TIẾN ĐỘ

| Phase | Module                          | Trạng thái  |
| ----- | ------------------------------- | ----------- |
| 0     | Khởi tạo                        | ☑ Hoàn thành |
| 1     | Bảo mật + Nhân viên             | ☐ Chưa bắt đầu |
| 2     | KH + Xe + Kho + NCC             | ☐ Chưa bắt đầu |
| 3     | Phụ kiện + Khuyến mãi           | ☐ Chưa bắt đầu |
| 4     | Hợp đồng + Trả góp + PDF        | ☐ Chưa bắt đầu |
| 5     | Bảo hành + Hậu mãi              | ☐ Chưa bắt đầu |
| 6     | Marketing + Khiếu nại           | ☐ Chưa bắt đầu |
| 7     | Báo cáo                         | ☐ Chưa bắt đầu |
| 8     | Hoàn thiện + Đóng gói           | ☐ Chưa bắt đầu |

**Quy ước cập nhật**: sau mỗi phase, đổi `☐ Chưa bắt đầu` → `☑ Hoàn thành` và update checklist 71 chức năng trong `plan.md`.
