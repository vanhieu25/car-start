"""Form thêm/sửa nhân viên."""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QTextEdit, QPushButton, QMessageBox

from src.modules.employee import service as emp_service
from src.core.exceptions import ValidationError


class EmployeeForm(QDialog):
    """Dialog form thêm hoặc sửa nhân viên."""

    def __init__(self, employee: dict | None = None, parent=None):
        super().__init__(parent)
        self._employee = employee
        self.setWindowTitle("Sửa nhân viên" if employee else "Thêm nhân viên")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_ho_ten = QLineEdit()
        self.txt_sdt = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_ngay_vao_lam = QLineEdit()
        self.txt_ngay_vao_lam.setPlaceholderText("YYYY-MM-DD")
        self.cbo_trang_thai = QComboBox()
        self.cbo_trang_thai.addItems(["dang_lam", "da_nghi"])
        self.txt_ghi_chu = QTextEdit()
        self.txt_ghi_chu.setMaximumHeight(80)

        form.addRow("Họ tên *:", self.txt_ho_ten)
        form.addRow("SĐT:", self.txt_sdt)
        form.addRow("Email:", self.txt_email)
        form.addRow("Ngày vào làm:", self.txt_ngay_vao_lam)
        form.addRow("Trạng thái:", self.cbo_trang_thai)
        form.addRow("Ghi chú:", self.txt_ghi_chu)

        layout.addLayout(form)

        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        if employee:
            self._fill_data(employee)

    def _fill_data(self, emp: dict):
        self.txt_ho_ten.setText(emp.get("ho_ten", ""))
        self.txt_sdt.setText(emp.get("sdt") or "")
        self.txt_email.setText(emp.get("email") or "")
        self.txt_ngay_vao_lam.setText(emp.get("ngay_vao_lam") or "")
        idx = self.cbo_trang_thai.findText(emp.get("trang_thai", "dang_lam"))
        if idx >= 0:
            self.cbo_trang_thai.setCurrentIndex(idx)
        self.txt_ghi_chu.setPlainText(emp.get("ghi_chu") or "")

    def _on_save(self):
        data = {
            "ho_ten": self.txt_ho_ten.text().strip(),
            "sdt": self.txt_sdt.text().strip() or None,
            "email": self.txt_email.text().strip() or None,
            "ngay_vao_lam": self.txt_ngay_vao_lam.text().strip() or None,
            "trang_thai": self.cbo_trang_thai.currentText(),
            "ghi_chu": self.txt_ghi_chu.toPlainText().strip() or None,
        }

        try:
            if self._employee:
                # Sửa
                emp_service.update_employee(self._employee["id"], **data)
            else:
                # Thêm
                emp_service.create_employee(**data)
            self.accept()
        except ValidationError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
