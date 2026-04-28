-- Schema SQL cho phần mềm quản lý đại lý xe hơi
-- SQLite với foreign keys enabled

-- Bật ràng buộc khóa ngoại
PRAGMA foreign_keys = ON;

-- ============================================
-- MODULE 3: NHÂN VIÊN
-- ============================================
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten TEXT NOT NULL,
    sdt TEXT,
    email TEXT UNIQUE,
    ngay_vao_lam DATE DEFAULT CURRENT_DATE,
    trang_thai TEXT DEFAULT 'dang_lam' CHECK (trang_thai IN ('dang_lam', 'da_nghi')),
    ghi_chu TEXT
);

-- ============================================
-- MODULE 15: BẢO MẬT (users + activity_log)
-- ============================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'nhan_vien')),
    employee_id INTEGER,
    is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
);

CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    hanh_dong TEXT NOT NULL,
    bang TEXT,
    ban_ghi_id INTEGER,
    thoi_gian DATETIME DEFAULT CURRENT_TIMESTAMP,
    chi_tiet TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================
-- MODULE 2: KHÁCH HÀNG
-- ============================================
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten TEXT NOT NULL,
    sdt TEXT,
    email TEXT UNIQUE,
    dia_chi TEXT,
    ngay_sinh DATE,
    hang_khach_hang TEXT DEFAULT 'dong' CHECK (hang_khach_hang IN ('dong', 'bac', 'vang', 'kim_cuong')),
    ghi_chu TEXT
);

-- ============================================
-- MODULE 1: XE
-- ============================================
CREATE TABLE cars (
    ma_xe TEXT PRIMARY KEY,
    hang TEXT NOT NULL,
    dong_xe TEXT NOT NULL,
    nam_sx INTEGER NOT NULL,
    mau_sac TEXT,
    gia_ban REAL NOT NULL CHECK (gia_ban >= 0),
    ton_kho INTEGER DEFAULT 0 CHECK (ton_kho >= 0),
    trang_thai TEXT DEFAULT 'con_hang' CHECK (trang_thai IN ('con_hang', 'da_ban', 'sap_ve'))
);

-- ============================================
-- MODULE 10: NHÀ CUNG CẤP
-- ============================================
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL,
    dia_chi TEXT,
    sdt TEXT,
    email TEXT,
    nguoi_lien_he TEXT
);

CREATE TABLE supplier_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    chat_luong INTEGER CHECK (chat_luong BETWEEN 1 AND 5),
    thoi_gian_giao INTEGER CHECK (thoi_gian_giao BETWEEN 1 AND 5),
    gia_ca INTEGER CHECK (gia_ca BETWEEN 1 AND 5),
    ghi_chu TEXT,
    ngay_danh_gia DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);

-- ============================================
-- MODULE 8: PHỤ KIỆN (đặt trước MODULE 5 để purchase_order_items tham chiếu được)
-- ============================================
CREATE TABLE accessories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL,
    mo_ta TEXT,
    loai TEXT CHECK (loai IN ('noi_that', 'ngoai_that', 'dien_tu', 'bao_ve', 'trang_tri')),
    gia REAL NOT NULL CHECK (gia >= 0),
    ton_kho INTEGER DEFAULT 0 CHECK (ton_kho >= 0)
);

-- Combo phụ kiện
CREATE TABLE combo_accessories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL,
    gia_combo REAL NOT NULL CHECK (gia_combo >= 0),
    mo_ta TEXT
);

CREATE TABLE combo_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    combo_id INTEGER NOT NULL,
    accessory_id INTEGER NOT NULL,
    so_luong INTEGER NOT NULL CHECK (so_luong > 0),
    FOREIGN KEY (combo_id) REFERENCES combo_accessories(id) ON DELETE CASCADE,
    FOREIGN KEY (accessory_id) REFERENCES accessories(id) ON DELETE CASCADE
);

-- ============================================
-- MODULE 5: KHO XE (stock_movements + purchase orders)
-- ============================================
CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id TEXT NOT NULL,
    supplier_id INTEGER,
    so_luong INTEGER NOT NULL CHECK (so_luong > 0),
    gia_nhap REAL NOT NULL CHECK (gia_nhap >= 0),
    ngay_nhap DATE DEFAULT CURRENT_DATE,
    ghi_chu TEXT,
    FOREIGN KEY (car_id) REFERENCES cars(ma_xe) ON DELETE CASCADE,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
);

-- Đơn đặt hàng từ nhà cung cấp
CREATE TABLE purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    ngay_dat DATE DEFAULT CURRENT_DATE,
    trang_thai TEXT DEFAULT 'cho_duyet' CHECK (trang_thai IN ('cho_duyet', 'da_duyet', 'da_nhan', 'da_huy')),
    ghi_chu TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);

CREATE TABLE purchase_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id INTEGER NOT NULL,
    car_id TEXT,
    accessory_id INTEGER,
    so_luong INTEGER NOT NULL CHECK (so_luong > 0),
    gia REAL NOT NULL CHECK (gia >= 0),
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (car_id) REFERENCES cars(ma_xe) ON DELETE SET NULL,
    FOREIGN KEY (accessory_id) REFERENCES accessories(id) ON DELETE SET NULL,
    CHECK ((car_id IS NOT NULL) OR (accessory_id IS NOT NULL))
);

-- ============================================
-- MODULE 7: KHUYẾN MÃI
-- ============================================
CREATE TABLE promotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL,
    mo_ta TEXT,
    loai TEXT CHECK (loai IN ('giam_tien', 'tang_pk', 'giam_lai', 'combo')),
    kieu_giam TEXT CHECK (kieu_giam IN ('co_dinh', 'phan_tram')),
    muc_giam REAL CHECK (muc_giam >= 0),
    tu_ngay DATE,
    den_ngay DATE,
    pham_vi TEXT CHECK (pham_vi IN ('toan_bo', 'hang_xe', 'dong_xe', 'ton_kho_lau')),
    pham_vi_id TEXT, -- ma hang xe hoac dong xe neu pham_vi = hang_xe/dong_xe
    dieu_kien_ton_kho_ngay INTEGER, -- so ngay ton kho toi thieu neu pham_vi = ton_kho_lau
    trang_thai TEXT DEFAULT 'dang_chay' CHECK (trang_thai IN ('dang_chay', 'tam_dung', 'da_ket_thuc'))
);

-- ============================================
-- MODULE 4: HỢP ĐỒNG
-- ============================================
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_hd TEXT UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    car_id TEXT NOT NULL,
    employee_id INTEGER,
    ngay_lap DATE DEFAULT CURRENT_DATE,
    gia_xe REAL NOT NULL CHECK (gia_xe >= 0),
    tong_phu_kien REAL DEFAULT 0 CHECK (tong_phu_kien >= 0),
    tong_giam_gia REAL DEFAULT 0 CHECK (tong_giam_gia >= 0),
    tong_thanh_toan REAL NOT NULL CHECK (tong_thanh_toan >= 0),
    trang_thai TEXT DEFAULT 'moi_tao' CHECK (trang_thai IN ('moi_tao', 'da_thanh_toan', 'da_giao_xe', 'da_huy')),
    ghi_chu TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
    FOREIGN KEY (car_id) REFERENCES cars(ma_xe) ON DELETE RESTRICT,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
);

-- Phụ kiện trong hợp đồng
CREATE TABLE contract_accessories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    accessory_id INTEGER NOT NULL,
    so_luong INTEGER NOT NULL CHECK (so_luong > 0),
    gia REAL NOT NULL CHECK (gia >= 0),
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
    FOREIGN KEY (accessory_id) REFERENCES accessories(id) ON DELETE RESTRICT
);

-- Khuyến mãi áp dụng cho hợp đồng
CREATE TABLE contract_promotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    promotion_id INTEGER NOT NULL,
    so_tien_giam REAL NOT NULL CHECK (so_tien_giam >= 0),
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
    FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE RESTRICT
);

-- ============================================
-- MODULE 11: TRẢ GÓP
-- ============================================
CREATE TABLE installments (
    contract_id INTEGER PRIMARY KEY,
    ngan_hang TEXT NOT NULL,
    so_tien_vay REAL NOT NULL CHECK (so_tien_vay >= 0),
    lai_suat REAL NOT NULL CHECK (lai_suat >= 0),
    so_thang INTEGER NOT NULL CHECK (so_thang > 0),
    kieu_tinh TEXT NOT NULL CHECK (kieu_tinh IN ('du_no_giam_dan', 'tra_deu')),
    ngay_bat_dau DATE NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE TABLE installment_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    ky INTEGER NOT NULL,
    ngay_du_kien DATE NOT NULL,
    so_tien REAL NOT NULL CHECK (so_tien >= 0),
    ngay_thuc_te DATE,
    trang_thai TEXT DEFAULT 'chua_tra' CHECK (trang_thai IN ('chua_tra', 'da_tra', 'cham_tra')),
    FOREIGN KEY (contract_id) REFERENCES installments(contract_id) ON DELETE CASCADE,
    UNIQUE (contract_id, ky)
);

-- ============================================
-- MODULE 6: BẢO HÀNH
-- ============================================
CREATE TABLE warranties (
    contract_id INTEGER PRIMARY KEY,
    thoi_han_thang INTEGER NOT NULL CHECK (thoi_han_thang > 0),
    pham_vi TEXT NOT NULL,
    ngay_bat_dau DATE DEFAULT CURRENT_DATE,
    ngay_ket_thuc DATE NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE TABLE warranty_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warranty_id INTEGER NOT NULL,
    ngay_den DATE DEFAULT CURRENT_DATE,
    noi_dung TEXT NOT NULL,
    loai TEXT CHECK (loai IN ('mien_phi', 'tinh_phi')),
    chi_phi REAL DEFAULT 0 CHECK (chi_phi >= 0),
    nhan_vien_id INTEGER,
    FOREIGN KEY (warranty_id) REFERENCES warranties(contract_id) ON DELETE CASCADE,
    FOREIGN KEY (nhan_vien_id) REFERENCES employees(id) ON DELETE SET NULL
);

-- ============================================
-- MODULE 9: HẬU MÃI
-- ============================================
CREATE TABLE maintenance_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    kieu_nhac TEXT CHECK (kieu_nhac IN ('theo_km', 'theo_thang')),
    gia_tri INTEGER, -- so km hoac so thang
    ngay_du_kien DATE,
    da_thuc_hien INTEGER DEFAULT 0 CHECK (da_thuc_hien IN (0, 1)),
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE TABLE maintenance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    ngay DATE DEFAULT CURRENT_DATE,
    noi_dung TEXT NOT NULL,
    chi_phi REAL DEFAULT 0 CHECK (chi_phi >= 0),
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE TABLE roadside_assistance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    ngay DATE DEFAULT CURRENT_DATE,
    noi_dung TEXT NOT NULL,
    phan_hoi TEXT,
    chi_phi REAL DEFAULT 0 CHECK (chi_phi >= 0),
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

-- ============================================
-- MODULE 12: MARKETING
-- ============================================
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL,
    ngan_sach REAL CHECK (ngan_sach >= 0),
    tu_ngay DATE,
    den_ngay DATE,
    kenh TEXT,
    ghi_chu TEXT
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL,
    kieu TEXT CHECK (kieu IN ('lai_thu', 'trien_lam', 'khac')),
    ngay DATE,
    dia_diem TEXT,
    campaign_id INTEGER,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
);

CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ho_ten TEXT NOT NULL,
    sdt TEXT,
    email TEXT,
    nguon TEXT,
    campaign_id INTEGER,
    trang_thai TEXT DEFAULT 'moi' CHECK (trang_thai IN ('moi', 'dang_lien_he', 'da_chuyen_kh', 'khong_quan_tam')),
    customer_id INTEGER,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

-- ============================================
-- MODULE 13: KHIẾU NẠI
-- ============================================
CREATE TABLE complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    noi_dung TEXT NOT NULL,
    muc_do TEXT CHECK (muc_do IN ('thap', 'trung_binh', 'cao')),
    ngay DATE DEFAULT CURRENT_DATE,
    nhan_vien_xu_ly_id INTEGER,
    trang_thai TEXT DEFAULT 'dang_xu_ly' CHECK (trang_thai IN ('dang_xu_ly', 'da_giai_quyet', 'da_dong')),
    danh_gia INTEGER CHECK (danh_gia BETWEEN 1 AND 5),
    ghi_chu TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (nhan_vien_xu_ly_id) REFERENCES employees(id) ON DELETE SET NULL
);
