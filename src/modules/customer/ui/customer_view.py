"""Danh sách khách hàng với CRUD."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QComboBox,
    QDialog, QFormLayout, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from src.modules.customer import service as customer_service
from src.core.exceptions import BusinessError


class CustomerForm(QDialog):
    def __init__(self, customer: dict | None = None, parent=None):
        super().__init__(parent)
        self._customer = customer
        self.setWindowTitle("Sửa khách hàng" if customer else "Thêm khách hàng")
        self.setMinimumSize(400, 350)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_ho_ten = QLineEdit()
        self.txt_sdt = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_dia_chi = QLineEdit()
        self.date_ngay_sinh = QDateEdit()
        self.date_ngay_sinh.setCalendarPopup(True)
        self.date_ngay_sinh.setDate(QDate.currentDate())
        self.cbo_hang = QComboBox()
        self.cbo_hang.addItems(["dong", "bac", "vang", "kim_cuong"])
        self.txt_ghi_chu = QLineEdit()

        form.addRow("Họ tên *:", self.txt_ho_ten)
        form.addRow("SĐT:", self.txt_sdt)
        form.addRow("Email:", self.txt_email)
        form.addRow("Địa chỉ:", self.txt_dia_chi)
        form.addRow("Ngày sinh:", self.date_ngay_sinh)
        form.addRow("Hạng:", self.cbo_hang)
        form.addRow("Ghi chú:", self.txt_ghi_chu)

        layout.addLayout(form)

        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        if customer:
            self._fill_data(customer)

    def _fill_data(self, cust: dict):
        self.txt_ho_ten.setText(cust.get("ho_ten", ""))
        self.txt_sdt.setText(cust.get("sdt") or "")
        self.txt_email.setText(cust.get("email") or "")
        self.txt_dia_chi.setText(cust.get("dia_chi") or "")
        if cust.get("ngay_sinh"):
            self.date_ngay_sinh.setDate(QDate.fromString(cust["ngay_sinh"], Qt.DateFormat.ISODate))
        idx = self.cbo_hang.findText(cust.get("hang_khach_hang", "dong"))
        if idx >= 0:
            self.cbo_hang.setCurrentIndex(idx)
        self.txt_ghi_chu.setText(cust.get("ghi_chu") or "")

    def _on_save(self):
        data = {
            "ho_ten": self.txt_ho_ten.text().strip(),
            "sdt": self.txt_sdt.text().strip() or None,
            "email": self.txt_email.text().strip() or None,
            "dia_chi": self.txt_dia_chi.text().strip() or None,
            "ngay_sinh": self.date_ngay_sinh.date().toString(Qt.DateFormat.ISODate),
            "hang_khach_hang": self.cbo_hang.currentText(),
            "ghi_chu": self.txt_ghi_chu.text().strip() or None,
        }
        try:
            if self._customer:
                customer_service.update_customer(self._customer["id"], **data)
            else:
                customer_service.create_customer(**data)
            self.accept()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


class CustomerHistoryDialog(QDialog):
    def __init__(self, customer_id: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lịch sử giao dịch")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)
        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(
            ["Mã HĐ", "Ngày", "Xe", "Giá xe", "Phụ kiện", "Giảm giá", "Tổng", "Trạng thái", "NV"]
        )
        self.table.setModel(self._model)

        history = customer_service.lay_lich_su(customer_id)
        for h in history:
            row = [
                QStandardItem(h["ma_hd"]),
                QStandardItem(str(h["ngay_lap"])),
                QStandardItem(f"{h['hang']} {h['dong_xe']}"),
                QStandardItem(f"{h['gia_xe']:,.0f}"),
                QStandardItem(f"{h['tong_phu_kien']:,.0f}"),
                QStandardItem(f"{h['tong_giam_gia']:,.0f}"),
                QStandardItem(f"{h['tong_thanh_toan']:,.0f}"),
                QStandardItem(h["trang_thai"]),
                QStandardItem(h.get("nhan_vien") or ""),
            ]
            self._model.appendRow(row)


_HANG_LABELS = {"dong": "Đồng", "bac": "Bạc", "vang": "Vàng", "kim_cuong": "Kim cương"}


class CustomerView(QWidget):
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self._current_user = current_user
        self._is_admin = current_user.get("role") == "admin"

        layout = QVBoxLayout(self)

        # Search bar
        search_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tìm kiếm theo tên, SĐT, email...")
        self.txt_search.textChanged.connect(self._on_search)
        search_layout.addWidget(self.txt_search)
        layout.addLayout(search_layout)

        # Table
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Thêm")
        self.btn_edit = QPushButton("Sửa")
        self.btn_delete = QPushButton("Xóa")
        self.btn_history = QPushButton("Lịch sử")
        self.btn_refresh = QPushButton("Làm mới")

        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_history.clicked.connect(self._on_history)
        self.btn_refresh.clicked.connect(self._load_data)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_history)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        layout.addLayout(btn_layout)

        if not self._is_admin:
            self.btn_add.setVisible(False)
            self.btn_edit.setVisible(False)
            self.btn_delete.setVisible(False)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["ID", "Họ tên", "SĐT", "Email", "Địa chỉ", "Ngày sinh", "Hạng", "Ghi chú"])
        self.table.setModel(self._model)

        self._all_data = []
        self._load_data()

    def _load_data(self):
        self._all_data = customer_service.list_customers()
        self._display_data(self._all_data)

    def _display_data(self, data: list):
        self._model.removeRows(0, self._model.rowCount())
        for c in data:
            hang = _HANG_LABELS.get(c.get("hang_khach_hang", "dong"), c.get("hang_khach_hang", "dong"))
            row = [
                QStandardItem(str(c["id"])),
                QStandardItem(c["ho_ten"]),
                QStandardItem(c["sdt"] or ""),
                QStandardItem(c["email"] or ""),
                QStandardItem(c["dia_chi"] or ""),
                QStandardItem(c["ngay_sinh"] or ""),
                QStandardItem(hang),
                QStandardItem(c["ghi_chu"] or ""),
            ]
            self._model.appendRow(row)

    def _on_search(self, text: str):
        if len(text.strip()) < 2:
            self._display_data(self._all_data)
        else:
            results = customer_service.search_customers(text)
            self._display_data(results)

    def _get_selected_id(self) -> int | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        row = indexes[0].row()
        return int(self._model.item(row, 0).text())

    def _on_add(self):
        dlg = CustomerForm(parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_edit(self):
        cust_id = self._get_selected_id()
        if cust_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khách hàng.")
            return
        cust = customer_service.get_customer(cust_id)
        dlg = CustomerForm(customer=cust, parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_delete(self):
        cust_id = self._get_selected_id()
        if cust_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khách hàng.")
            return
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa khách hàng này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                customer_service.delete_customer(cust_id, self._current_user)
                self._load_data()
            except BusinessError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _on_history(self):
        cust_id = self._get_selected_id()
        if cust_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khách hàng.")
            return
        dlg = CustomerHistoryDialog(cust_id, self)
        dlg.exec()