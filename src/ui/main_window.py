"""Cửa sổ chính với sidebar trống + status bar."""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStatusBar, QLabel


class MainWindow(QMainWindow):
    """Cửa sổ chính ứng dụng (phase 0: skeleton)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Đại Lý Xe Hơi")
        self.setMinimumSize(1024, 768)

        # Central widget rỗng
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        label = QLabel("Ứng dụng Quản lý Đại lý Xe Hơi\n(Phase 0 - Khởi tạo project)")
        label.setStyleSheet("font-size: 18px; color: #666;")
        layout.addWidget(label)

        # Status bar
        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Sẵn sàng | Chưa đăng nhập")
