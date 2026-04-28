"""Phân quyền cho ứng dụng."""
from src.core.exceptions import PermissionDenied
from src.app.session import Session


def require_role(*roles: str):
    """Decorator kiểm tra role user.

    Args:
        *roles: Các role được phép (VD: 'admin', 'nhan_vien').

    Raises:
        PermissionDenied: Nếu user không có role phù hợp hoặc chưa đăng nhập.
    """
    def decorator(func):
        def wrapper(session: Session, *args, **kwargs):
            if not session.is_logged_in():
                raise PermissionDenied("Bạn chưa đăng nhập.")
            user_role = session.user.get("role")
            if user_role not in roles:
                raise PermissionDenied(f"Yêu cầu quyền: {', '.join(roles)}.")
            return func(session, *args, **kwargs)
        return wrapper
    return decorator
