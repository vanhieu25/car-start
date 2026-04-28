"""Quản lý kho xe: tồn kho + nhập kho + lịch sử."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QAbstractItemView, QLabel, QComboBox, QDialog,
    QFormLayout, QSpinBox, QDoubleSpinBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from src.modules.inventory import service as inventory_service
from src.modules.supplier import service as supplier_service
from src.modules.car import service as car_service
from src.core.exceptions import BusinessError


class ImportStockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nhập kho")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.cbo_car = QComboBox()
        self.cbo_supplier = QComboBox()
        self.spin_so_luong = QSpinBox()
        self.spin_so_luong.setRange(1, 999)
        self.spin_gia_nhap = QDoubleSpinBox()
        self.spin_gia_nhap.setRange(0, 10_000_000_000)
        self.spin_gia_nhap.setDecimals(0)
        self.spin_gia_nhap.setPrefix("VND ")
        self.spin_gia_nhap.setSuffix(" / xe")
        self.txt_ghi_chu = QLineEdit()

        form.addRow("Xe *:", self.cbo_car)
        form.addRow("Nhà cung cấp:", self.cbo_supplier)
        form.addRow("Số lượng *:", self.spin_so_luong)
        form.addRow("Giá nhập *:", self.spin_gia_nhap)
        form.addRow("Ghi chú:", self.txt_ghi_chu)

        layout.addLayout(form)

        btn_save = QPushButton("Nhập kho")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        self._load_combos()

    def _load_combos(self):
        for car in car_service.list_cars():
            self.cbo_car.addItem(f"{car['ma_xe']} - {car['hang']} {car['dong_xe']}", car["ma_xe"])

        self.cbo_supplier.addItem("- Không chọn -", None)
        for sup in supplier_service.list_suppliers():
            self.cbo_supplier.addItem(sup["ten"], sup["id"])

    def _on_save(self):
        ma_xe = self.cbo_car.currentData()
        supplier_id = self.cbo_supplier.currentData()
        so_luong = self.spin_so_luong.value()
        gia_nhap = self.spin_gia_nhap.value()
        ghi_chu = self.txt_ghi_chu.text().strip() or None

        try:
            inventory_service.nhap_kho(ma_xe, supplier_id, so_luong, gia_nhap, ghi_chu)
            self.accept()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


_STOCK_STATUS_LABELS = {
    "con_hang": "Còn hàng",
    "da_ban": "Đã bán",
    "sap_ve": "Sắp về",
}


class StockView(QWidget):
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self._current_user = current_user
        self._is_admin = current_user.get("role") == "admin"

        layout = QVBoxLayout(self)

        # Tabs: Tồn kho + Lịch sử nhập
        tabs = QWidget()
        tabs_layout = QVBoxLayout(tabs)

        self.stock_table = QTableView()
        self.stock_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.stock_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabs_layout.addWidget(QLabel("TỒN KHO XE"))
        tabs_layout.addWidget(self.stock_table)

        self._stock_model = QStandardItemModel()
        self._stock_model.setHorizontalHeaderLabels(
            ["Mã xe", "Hãng", "Dòng xe", "Màu", "Giá bán", "Tồn kho", "Trạng thái"]
        )
        self.stock_table.setModel(self._stock_model)

        btn_layout = QHBoxLayout()
        self.btn_import = QPushButton("Nhập kho")
        self.btn_refresh = QPushButton("Làm mới")
        self.btn_import.clicked.connect(self._on_import)
        self.btn_refresh.clicked.connect(self._load_stock)
        btn_layout.addWidget(self.btn_import)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        tabs_layout.addLayout(btn_layout)

        if not self._is_admin:
            self.btn_import.setVisible(False)

        # Low stock warning label
        self.lbl_warning = QLabel()
        self.lbl_warning.setStyleSheet("color: #c0392b; font-weight: bold;")
        tabs_layout.addWidget(self.lbl_warning)

        layout.addWidget(tabs)

        self._load_stock()

    def _load_stock(self):
        self._stock_model.removeRows(0, self._stock_model.rowCount())
        for car in car_service.list_cars():
            status = _STOCK_STATUS_LABELS.get(car.get("trang_thai", ""), car.get("trang_thai", ""))
            row = [
                QStandardItem(car["ma_xe"]),
                QStandardItem(car["hang"]),
                QStandardItem(car["dong_xe"]),
                QStandardItem(car["mau_sac"] or ""),
                QStandardItem(f"{car['gia_ban']:,.0f}"),
                QStandardItem(str(car["ton_kho"])),
                QStandardItem(status),
            ]
            self._stock_model.appendRow(row)

        # Low stock warning
        warnings = inventory_service.kiem_tra_canh_bao()
        if warnings:
            threshold = warnings[0].get("threshold", 3)
            self.lbl_warning.setText(
                f"Cảnh báo: {len(warnings)} xe có tồn kho thấp hơn ngưỡng ({threshold})"
            )
        else:
            self.lbl_warning.setText("")

    def _on_import(self):
        dlg = ImportStockDialog(self)
        if dlg.exec() == 1:
            self._load_stock()