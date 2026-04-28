"""Lớp exception nghiệp vụ cho ứng dụng."""


class BusinessError(Exception):
    """Lỗi nghiệp vụ chung."""
    pass


class PermissionDenied(BusinessError):
    """Người dùng không có quyền thực hiện hành động."""
    pass


class ValidationError(BusinessError):
    """Dữ liệu không hợp lệ."""
    pass


class NotFoundError(BusinessError):
    """Không tìm thấy bản ghi."""
    pass
