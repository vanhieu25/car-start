"""Danh sách nhân viên với CRUD."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from src.modules.employee import service as emp_service
from src.modules.employee.ui.employee_form import EmployeeForm


class EmployeeView(QWidget):
    """Bảng danh sách nhân viên + nút Thêm/Sửa/Xóa."""

    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self._current_user = current_user
        self._is_admin = current_user.get("role") == "admin"

        layout = QVBoxLayout(self)

        # Bảng dữ liệu
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Nút thao tác
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Thêm")
        self.btn_edit = QPushButton("Sửa")
        self.btn_delete = QPushButton("Xóa")
        self.btn_refresh = QPushButton("Làm mới")

        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_refresh.clicked.connect(self._load_data)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        layout.addLayout(btn_layout)

        # Ẩn nút nếu không phải admin
        if not self._is_admin:
            self.btn_add.setVisible(False)
            self.btn_edit.setVisible(False)
            self.btn_delete.setVisible(False)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["ID", "Họ tên", "SĐT", "Email", "Ngày vào làm", "Trạng thái"])
        self.table.setModel(self._model)

        self._load_data()

    def _load_data(self):
        """Nạp dữ liệu từ service."""
        self._model.removeRows(0, self._model.rowCount())
        employees = emp_service.list_employees()
        for emp in employees:
            row = [
                QStandardItem(str(emp["id"])),
                QStandardItem(emp["ho_ten"]),
                QStandardItem(emp["sdt"] or ""),
                QStandardItem(emp["email"] or ""),
                QStandardItem(emp["ngay_vao_lam"] or ""),
                QStandardItem(emp["trang_thai"]),
            ]
            self._model.appendRow(row)

    def _get_selected_id(self) -> int | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        row = indexes[0].row()
        return int(self._model.item(row, 0).text())

    def _on_add(self):
        dlg = EmployeeForm(parent=self)
        if dlg.exec() == 1:  # Accepted
            self._load_data()

    def _on_edit(self):
        emp_id = self._get_selected_id()
        if emp_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhân viên.")
            return
        emp = emp_service.get_employee(emp_id)
        if emp is None:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy nhân viên.")
            return
        dlg = EmployeeForm(employee=emp, parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_delete(self):
        emp_id = self._get_selected_id()
        if emp_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhân viên.")
            return
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa nhân viên này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                emp_service.delete_employee(emp_id, self._current_user)
                self._load_data()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))
