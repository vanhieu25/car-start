"""Cửa sổ chính với sidebar + session + login."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar,
    QListWidget, QStackedWidget, QLabel
)
from PyQt6.QtCore import Qt

from src.app.session import Session
from src.ui.login_dialog import LoginDialog
from src.modules.employee.ui.employee_view import EmployeeView
from src.modules.customer.ui.customer_view import CustomerView
from src.modules.car.ui.car_view import CarView
from src.modules.supplier.ui.supplier_view import SupplierView
from src.modules.inventory.ui.stock_view import StockView
from src.modules.accessory.ui.accessory_view import AccessoryView
from src.modules.promotion.ui.promotion_view import PromotionView


class MainWindow(QMainWindow):
    """Cửa sổ chính với sidebar, session timeout, và các module view."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Đại Lý Xe Hơi")
        self.setMinimumSize(1024, 768)

        self._session = Session()
        self._session.expired.connect(self._on_session_expired)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.addItem("Nhân viên")
        self.sidebar.addItem("Khách hàng")
        self.sidebar.addItem("Xe")
        self.sidebar.addItem("Kho xe")
        self.sidebar.addItem("Nhà cung cấp")
        self.sidebar.addItem("Phụ kiện")
        self.sidebar.addItem("Khuyến mãi")
        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)
        main_layout.addWidget(self.sidebar)

        # Stack
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        # Placeholder
        self._placeholder = QLabel("Vui lòng đăng nhập để sử dụng ứng dụng")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("font-size: 18px; color: #666;")
        self.stack.addWidget(self._placeholder)

        # Module views (created after login)
        self._views = {}
        self._current_user = None

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Chưa đăng nhập")

        self._show_login()

    def _show_login(self):
        dlg = LoginDialog(self)
        if dlg.exec() != 1:
            self.close()
            return
        user = dlg.get_user()
        if user:
            self._session.login(user)
            self._current_user = user
            self._init_views()
            self._update_ui_after_login()

    def _init_views(self):
        user = self._current_user
        self._views = {
            "employee": EmployeeView(current_user=user),
            "customer": CustomerView(current_user=user),
            "car": CarView(current_user=user),
            "stock": StockView(current_user=user),
            "supplier": SupplierView(current_user=user),
            "accessory": AccessoryView(current_user=user),
            "promotion": PromotionView(current_user=user),
        }
        for view in self._views.values():
            self.stack.addWidget(view)

    def _update_ui_after_login(self):
        user = self._current_user
        role = user.get("role", "nhan_vien")
        self.status.showMessage(f"Đăng nhập: {user.get('username')} ({role})")
        self.stack.setCurrentIndex(1)

    def _on_sidebar_changed(self, index: int):
        if not self._session.is_logged_in():
            return
        names = ["employee", "customer", "car", "stock", "supplier", "accessory", "promotion"]
        if 0 <= index - 1 < len(names):
            view_name = names[index - 1]
            if view_name in self._views:
                self.stack.setCurrentWidget(self._views[view_name])

    def _on_session_expired(self):
        self.status.showMessage("Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.")
        self.stack.setCurrentIndex(0)
        self._views = {}
        self._current_user = None
        self._show_login()