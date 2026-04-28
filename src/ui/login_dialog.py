"""Dialog đăng nhập."""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

from src.modules.auth import service as auth_service
from src.core.exceptions import ValidationError


class LoginDialog(QDialog):
    """Form đăng nhập với username/password."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Đăng nhập")
        self.setFixedSize(300, 150)
        self._user = None

        layout = QVBoxLayout(self)

        self.lbl_username = QLabel("Tên đăng nhập:")
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("admin")

        self.lbl_password = QLabel("Mật khẩu:")
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("admin123")

        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.clicked.connect(self._on_login)

        layout.addWidget(self.lbl_username)
        layout.addWidget(self.txt_username)
        layout.addWidget(self.lbl_password)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.btn_login)

    def _on_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        try:
            self._user = auth_service.login(username, password)
            self.accept()
        except ValidationError as e:
            QMessageBox.warning(self, "Lỗi đăng nhập", str(e))

    def get_user(self) -> dict | None:
        return self._user
