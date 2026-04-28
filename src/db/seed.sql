-- Dữ liệu seed mặc định cho hệ thống

-- Nhân viên admin mặc định
INSERT INTO employees (ho_ten, sdt, email, ngay_vao_lam, trang_thai, ghi_chu)
VALUES ('Administrator', '0000000000', 'admin@car.local', DATE('now'), 'dang_lam', 'Tài khoản quản trị mặc định');

-- Tài khoản admin (bcrypt hash của "admin123")
INSERT INTO users (username, password_hash, role, employee_id, is_active, created_at)
VALUES (
    'admin',
    '$2b$12$igQag66.M6hurnDxg0eXoeghFzwn3vHDGDUTdQTa/cLS1xQBU3ws2',
    'admin',
    (SELECT id FROM employees WHERE email = 'admin@car.local'),
    1,
    DATETIME('now')
);
