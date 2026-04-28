"""Cửa sổ chính với sidebar + session + login."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar,
    QListWidget, QStackedWidget, QLabel
)
from PyQt6.QtCore import Qt

from src.app.session import Session
from src.ui.login_dialog import LoginDialog
from src.modules.employee.ui.employee_view import EmployeeView


class MainWindow(QMainWindow):
    """Cửa sổ chính với sidebar, session timeout, và các module view."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Đại Lý Xe Hơi")
        self.setMinimumSize(1024, 768)

        self._session = Session()
        self._session.expired.connect(self._on_session_expired)

        # Layout chính
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.addItem("Nhân viên")
        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)
        main_layout.addWidget(self.sidebar)

        # Stacked widget cho các view
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        # Placeholder khi chưa đăng nhập
        self._placeholder = QLabel("Vui lòng đăng nhập để sử dụng ứng dụng")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("font-size: 18px; color: #666;")
        self.stack.addWidget(self._placeholder)

        # Employee view
        self._employee_view = None

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Chưa đăng nhập")

        # Hiển thị login dialog
        self._show_login()

    def _show_login(self):
        dlg = LoginDialog(self)
        if dlg.exec() != 1:
            self.close()
            return
        user = dlg.get_user()
        if user:
            self._session.login(user)
            self._update_ui_after_login()

    def _update_ui_after_login(self):
        user = self._session.user
        role = user.get("role", "nhan_vien")
        self.status.showMessage(f"Đăng nhập: {user.get('username')} ({role})")

        # Khởi tạo employee view
        self._employee_view = EmployeeView(current_user=user)
        self.stack.addWidget(self._employee_view)
        self.stack.setCurrentIndex(1)

    def _on_sidebar_changed(self, index: int):
        if not self._session.is_logged_in():
            return
        if index == 0:  # Nhân viên
            self.stack.setCurrentIndex(1 if self._employee_view else 0)

    def _on_session_expired(self):
        self.status.showMessage("Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.")
        self.stack.setCurrentIndex(0)
        self._employee_view = None
        self._show_login()
