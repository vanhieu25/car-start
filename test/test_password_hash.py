"""Test bcrypt hash password."""
from src.modules.auth import service as auth_service


def test_bcrypt_hash_starts_with_dollar():
    """Hash bcrypt phải bắt đầu bằng $2b$."""
    hashed = auth_service.hash_password("password123")
    assert hashed.startswith("$2b$")


def test_bcrypt_verify_correct():
    """Verify đúng mật khẩu."""
    plain = "mypassword"
    hashed = auth_service.hash_password(plain)
    assert auth_service.verify_password(plain, hashed) is True


def test_bcrypt_verify_incorrect():
    """Verify sai mật khẩu."""
    plain = "mypassword"
    hashed = auth_service.hash_password(plain)
    assert auth_service.verify_password("wrongpassword", hashed) is False


def test_bcrypt_different_hashes_same_password():
    """Mỗi lần hash cùng mật khẩu cho kết quả khác nhau."""
    plain = "samepassword"
    hash1 = auth_service.hash_password(plain)
    hash2 = auth_service.hash_password(plain)
    assert hash1 != hash2
    assert auth_service.verify_password(plain, hash1)
    assert auth_service.verify_password(plain, hash2)
