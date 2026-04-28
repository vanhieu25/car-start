"""Quản lý phiên đăng nhập + timeout idle."""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.core.config_loader import get_config


class Session(QObject):
    """Lưu user hiện tại và đếm thời gian idle.

    Signals:
        expired: Phát khi session timeout.
    """

    expired = pyqtSignal()

    def __init__(self, timeout_seconds: int | None = None):
        super().__init__()
        self._user: dict | None = None

        if timeout_seconds is None:
            cfg = get_config()
            timeout_seconds = cfg.getint("session", "timeout", fallback=1800)
        self._timeout_ms = timeout_seconds * 1000

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

    @property
    def user(self) -> dict | None:
        return self._user

    def login(self, user: dict) -> None:
        """Đăng nhập user và bắt đầu đếm timeout."""
        self._user = user
        self.reset_idle()

    def logout(self) -> None:
        """Đăng xuất và dừng timer."""
        self._user = None
        self._timer.stop()

    def reset_idle(self) -> None:
        """Reset bộ đếm idle."""
        if self._user is not None:
            self._timer.stop()
            self._timer.start(self._timeout_ms)

    def _on_timeout(self) -> None:
        self._user = None
        self.expired.emit()

    def is_logged_in(self) -> bool:
        return self._user is not None

    def is_admin(self) -> bool:
        return self._user is not None and self._user.get("role") == "admin"
