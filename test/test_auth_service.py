"""Test cho auth service."""
import pytest

from src.modules.auth import service as auth_service
from src.core.exceptions import ValidationError


def test_hash_and_verify_password():
    """Test bcrypt hash và verify."""
    plain = "mysecret123"
    hashed = auth_service.hash_password(plain)
    assert auth_service.verify_password(plain, hashed)
    assert not auth_service.verify_password("wrong", hashed)


def test_login_success(tmp_db):
    """Test đăng nhập thành công."""
    # Tạo user test
    tmp_db.execute(
        """
        INSERT INTO users (username, password_hash, role, is_active)
        VALUES (?, ?, ?, 1)
        """,
        ("testuser", auth_service.hash_password("testpass"), "nhan_vien")
    )
    tmp_db.commit()

    user = auth_service.login("testuser", "testpass")
    assert user["username"] == "testuser"
    assert user["role"] == "nhan_vien"
    assert "password_hash" not in user


def test_login_wrong_password(tmp_db):
    """Test đăng nhập sai mật khẩu."""
    tmp_db.execute(
        "INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, 1)",
        ("testuser", auth_service.hash_password("testpass"), "nhan_vien")
    )
    tmp_db.commit()

    with pytest.raises(ValidationError, match="Sai"):
        auth_service.login("testuser", "wrongpass")


def test_login_inactive_user(tmp_db):
    """Test đăng nhập user bị vô hiệu hóa."""
    tmp_db.execute(
        "INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, 0)",
        ("testuser", auth_service.hash_password("testpass"), "nhan_vien")
    )
    tmp_db.commit()

    with pytest.raises(ValidationError, match="vô hiệu hóa"):
        auth_service.login("testuser", "testpass")
