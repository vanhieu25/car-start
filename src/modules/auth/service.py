"""Service xử lý nghiệp vụ đăng nhập, mật khẩu."""
import bcrypt

from src.modules.auth import repository as auth_repo
from src.core.exceptions import ValidationError, NotFoundError, BusinessError


def hash_password(plain: str) -> str:
    """Băm mật khẩu bằng bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Kiểm tra mật khẩu có khớp với hash không."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def login(username: str, password: str) -> dict:
    """Đăng nhập, trả về thông tin user nếu thành công.

    Returns:
        Dict user (không chứa password_hash).

    Raises:
        ValidationError: Sai tài khoản/mật khẩu hoặc bị vô hiệu hóa.
    """
    user = auth_repo.get_user_by_username(username)
    if user is None:
        raise ValidationError("Sai tên đăng nhập hoặc mật khẩu.")

    if not user["is_active"]:
        raise ValidationError("Tài khoản đã bị vô hiệu hóa.")

    if not verify_password(password, user["password_hash"]):
        raise ValidationError("Sai tên đăng nhập hoặc mật khẩu.")

    # Xóa password_hash trước khi trả về
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return safe_user


def change_password(user_id: int, old_password: str, new_password: str) -> None:
    """Đổi mật khẩu.

    Raises:
        ValidationError: Mật khẩu cũ sai hoặc mật khẩu mới quá ngắn.
    """
    if len(new_password) < 6:
        raise ValidationError("Mật khẩu mới phải có ít nhất 6 ký tự.")

    user = auth_repo.get_user_by_username(
        auth_repo.get_user_by_username.__code__.co_varnames[0]
    )

    conn = None
    # Để lấy user theo ID, cần query trực tiếp
    from src.db.connection import get_connection

    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT password_hash FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise NotFoundError(f"Không tìm thấy user id={user_id}")
        if not verify_password(old_password, row["password_hash"]):
            raise ValidationError("Mật khẩu cũ không đúng.")

        new_hash = hash_password(new_password)
        auth_repo.update_password(user_id, new_hash)
    finally:
        if conn:
            conn.close()
