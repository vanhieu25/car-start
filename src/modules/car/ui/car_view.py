"""Danh sách xe với CRUD và tìm kiếm nâng cao."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QComboBox,
    QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from src.modules.car import service as car_service
from src.core.exceptions import BusinessError


class CarForm(QDialog):
    def __init__(self, car: dict | None = None, parent=None):
        super().__init__(parent)
        self._car = car
        self.setWindowTitle("Sửa xe" if car else "Thêm xe")
        self.setMinimumSize(450, 400)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_ma_xe = QLineEdit()
        self.txt_hang = QLineEdit()
        self.txt_dong_xe = QLineEdit()
        self.spin_nam_sx = QSpinBox()
        self.spin_nam_sx.setRange(1900, 2100)
        self.txt_mau_sac = QLineEdit()
        self.spin_gia_ban = QDoubleSpinBox()
        self.spin_gia_ban.setRange(0, 10_000_000_000)
        self.spin_gia_ban.setDecimals(0)
        self.spin_gia_ban.setSuffix(" VND")
        self.spin_ton_kho = QSpinBox()
        self.spin_ton_kho.setRange(0, 9999)
        self.cbo_trang_thai = QComboBox()
        self.cbo_trang_thai.addItems(["con_hang", "da_ban", "sap_ve"])

        form.addRow("Mã xe *:", self.txt_ma_xe)
        form.addRow("Hãng *:", self.txt_hang)
        form.addRow("Dòng xe *:", self.txt_dong_xe)
        form.addRow("Năm SX *:", self.spin_nam_sx)
        form.addRow("Màu sắc:", self.txt_mau_sac)
        form.addRow("Giá bán *:", self.spin_gia_ban)
        form.addRow("Tồn kho:", self.spin_ton_kho)
        form.addRow("Trạng thái:", self.cbo_trang_thai)

        layout.addLayout(form)

        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        if car:
            self._fill_data(car)
            self.txt_ma_xe.setEnabled(False)

    def _fill_data(self, car: dict):
        self.txt_ma_xe.setText(car.get("ma_xe", ""))
        self.txt_hang.setText(car.get("hang", ""))
        self.txt_dong_xe.setText(car.get("dong_xe", ""))
        self.spin_nam_sx.setValue(car.get("nam_sx", 2024))
        self.txt_mau_sac.setText(car.get("mau_sac") or "")
        self.spin_gia_ban.setValue(car.get("gia_ban", 0))
        self.spin_ton_kho.setValue(car.get("ton_kho", 0))
        idx = self.cbo_trang_thai.findText(car.get("trang_thai", "con_hang"))
        if idx >= 0:
            self.cbo_trang_thai.setCurrentIndex(idx)

    def _on_save(self):
        data = {
            "hang": self.txt_hang.text().strip(),
            "dong_xe": self.txt_dong_xe.text().strip(),
            "nam_sx": self.spin_nam_sx.value(),
            "mau_sac": self.txt_mau_sac.text().strip() or None,
            "gia_ban": self.spin_gia_ban.value(),
            "ton_kho": self.spin_ton_kho.value(),
            "trang_thai": self.cbo_trang_thai.currentText(),
        }
        try:
            if self._car:
                car_service.update_car(self._car["ma_xe"], **data)
            else:
                ma_xe = self.txt_ma_xe.text().strip()
                car_service.create_car(ma_xe, **data)
            self.accept()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


class CarSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tìm kiếm nâng cao")
        self.setMinimumSize(450, 350)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_hang = QLineEdit()
        self.txt_dong_xe = QLineEdit()
        self.spin_nam_sx = QSpinBox()
        self.spin_nam_sx.setRange(1900, 2100)
        self.spin_nam_sx.setSpecialValueText("...")
        self.spin_nam_sx.setValue(0)
        self.txt_mau_sac = QLineEdit()
        self.cbo_trang_thai = QComboBox()
        self.cbo_trang_thai.addItems(["", "con_hang", "da_ban", "sap_ve"])
        self.spin_min_gia = QDoubleSpinBox()
        self.spin_min_gia.setRange(0, 10_000_000_000)
        self.spin_min_gia.setDecimals(0)
        self.spin_min_gia.setPrefix("Từ ")
        self.spin_min_gia.setSuffix(" VND")
        self.spin_max_gia = QDoubleSpinBox()
        self.spin_max_gia.setRange(0, 10_000_000_000)
        self.spin_max_gia.setDecimals(0)
        self.spin_max_gia.setPrefix("Đến ")
        self.spin_max_gia.setSuffix(" VND")

        form.addRow("Hãng:", self.txt_hang)
        form.addRow("Dòng xe:", self.txt_dong_xe)
        form.addRow("Năm SX:", self.spin_nam_sx)
        form.addRow("Màu sắc:", self.txt_mau_sac)
        form.addRow("Trạng thái:", self.cbo_trang_thai)
        form.addRow("Giá từ:", self.spin_min_gia)
        form.addRow("Giá đến:", self.spin_max_gia)

        layout.addLayout(form)

        btn_search = QPushButton("Tìm kiếm")
        btn_search.clicked.connect(self._on_search)
        layout.addWidget(btn_search)

        self.filters = {}

    def _on_search(self):
        self.filters = {}
        if self.txt_hang.text().strip():
            self.filters["hang"] = self.txt_hang.text().strip()
        if self.txt_dong_xe.text().strip():
            self.filters["dong_xe"] = self.txt_dong_xe.text().strip()
        if self.spin_nam_sx.value() > 0:
            self.filters["nam_sx"] = self.spin_nam_sx.value()
        if self.txt_mau_sac.text().strip():
            self.filters["mau_sac"] = self.txt_mau_sac.text().strip()
        if self.cbo_trang_thai.currentText():
            self.filters["trang_thai"] = self.cbo_trang_thai.currentText()
        if self.spin_min_gia.value() > 0:
            self.filters["min_gia"] = self.spin_min_gia.value()
        if self.spin_max_gia.value() > 0:
            self.filters["max_gia"] = self.spin_max_gia.value()
        self.accept()

    def get_filters(self) -> dict:
        return self.filters


_TRANG_THAI_LABELS = {
    "con_hang": "Còn hàng",
    "da_ban": "Đã bán",
    "sap_ve": "Sắp về",
}


class CarView(QWidget):
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self._current_user = current_user
        self._is_admin = current_user.get("role") == "admin"

        layout = QVBoxLayout(self)

        # Filter bar
        filter_layout = QHBoxLayout()
        self.cbo_filter_status = QComboBox()
        self.cbo_filter_status.addItems(["Tất cả", "con_hang", "da_ban", "sap_ve"])
        self.cbo_filter_status.currentTextChanged.connect(self._on_filter_status)
        filter_layout.addWidget(QLabel("Lọc:"))
        filter_layout.addWidget(self.cbo_filter_status)
        filter_layout.addStretch()
        self.btn_search_advanced = QPushButton("Tìm kiếm nâng cao")
        self.btn_search_advanced.clicked.connect(self._on_search_advanced)
        filter_layout.addWidget(self.btn_search_advanced)
        layout.addLayout(filter_layout)

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

        if not self._is_admin:
            self.btn_add.setVisible(False)
            self.btn_delete.setVisible(False)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(
            ["Mã xe", "Hãng", "Dòng xe", "Năm SX", "Màu", "Giá bán", "Tồn kho", "Trạng thái"]
        )
        self.table.setModel(self._model)

        self._all_data = []
        self._load_data()

    def _load_data(self):
        self._all_data = car_service.list_cars()
        self._display_data(self._all_data)

    def _display_data(self, data: list):
        self._model.removeRows(0, self._model.rowCount())
        for car in data:
            trang_thai = _TRANG_THAI_LABELS.get(car.get("trang_thai", ""), car.get("trang_thai", ""))
            row = [
                QStandardItem(car["ma_xe"]),
                QStandardItem(car["hang"]),
                QStandardItem(car["dong_xe"]),
                QStandardItem(str(car["nam_sx"])),
                QStandardItem(car["mau_sac"] or ""),
                QStandardItem(f"{car['gia_ban']:,.0f}"),
                QStandardItem(str(car["ton_kho"])),
                QStandardItem(trang_thai),
            ]
            self._model.appendRow(row)

    def _on_filter_status(self, text: str):
        if text == "Tất cả":
            self._display_data(self._all_data)
        else:
            filtered = [c for c in self._all_data if c.get("trang_thai") == text]
            self._display_data(filtered)

    def _on_search_advanced(self):
        dlg = CarSearchDialog(self)
        if dlg.exec() == 1:
            filters = dlg.get_filters()
            if filters:
                results = car_service.search_cars(filters)
                self._display_data(results)
            else:
                self._display_data(self._all_data)

    def _get_selected_ma_xe(self) -> str | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        row = indexes[0].row()
        return self._model.item(row, 0).text()

    def _on_add(self):
        dlg = CarForm(parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_edit(self):
        ma_xe = self._get_selected_ma_xe()
        if ma_xe is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn xe.")
            return
        car = car_service.get_car(ma_xe)
        dlg = CarForm(car=car, parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_delete(self):
        ma_xe = self._get_selected_ma_xe()
        if ma_xe is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn xe.")
            return
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa xe này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                car_service.delete_car(ma_xe, self._current_user)
                self._load_data()
            except BusinessError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))