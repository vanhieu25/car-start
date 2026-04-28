"""Danh sách phụ kiện với CRUD + combo."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QAbstractItemView, QLabel, QComboBox, QDialog,
    QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QTabWidget,
    QListWidget, QTableWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from src.modules.accessory import service as acc_service
from src.core.exceptions import BusinessError

_LOAI_LABELS = {
    "noi_that": "Nội thất",
    "ngoai_that": "Ngoại thất",
    "dien_tu": "Điện tử",
    "bao_ve": "Bảo vệ",
    "trang_tri": "Trang trí",
}


class AccessoryForm(QDialog):
    def __init__(self, accessory: dict | None = None, parent=None):
        super().__init__(parent)
        self._acc = accessory
        self.setWindowTitle("Sửa phụ kiện" if accessory else "Thêm phụ kiện")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_ten = QLineEdit()
        self.txt_mo_ta = QLineEdit()
        self.cbo_loai = QComboBox()
        self.cbo_loai.addItems(list(_LOAI_LABELS.keys()))
        self.spin_gia = QDoubleSpinBox()
        self.spin_gia.setRange(0, 10_000_000_000)
        self.spin_gia.setDecimals(0)
        self.spin_gia.setPrefix("VND ")
        self.spin_ton_kho = QSpinBox()
        self.spin_ton_kho.setRange(0, 9999)

        form.addRow("Tên *:", self.txt_ten)
        form.addRow("Mô tả:", self.txt_mo_ta)
        form.addRow("Loại *:", self.cbo_loai)
        form.addRow("Giá *:", self.spin_gia)
        form.addRow("Tồn kho:", self.spin_ton_kho)

        layout.addLayout(form)

        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        if accessory:
            self._fill_data(accessory)

    def _fill_data(self, acc: dict):
        self.txt_ten.setText(acc.get("ten", ""))
        self.txt_mo_ta.setText(acc.get("mo_ta") or "")
        idx = self.cbo_loai.findText(acc.get("loai", ""))
        if idx >= 0:
            self.cbo_loai.setCurrentIndex(idx)
        self.spin_gia.setValue(acc.get("gia", 0))
        self.spin_ton_kho.setValue(acc.get("ton_kho", 0))

    def _on_save(self):
        data = {
            "ten": self.txt_ten.text().strip(),
            "mo_ta": self.txt_mo_ta.text().strip() or None,
            "loai": self.cbo_loai.currentText(),
            "gia": self.spin_gia.value(),
            "ton_kho": self.spin_ton_kho.value(),
        }
        try:
            if self._acc:
                acc_service.update_accessory(self._acc["id"], **data)
            else:
                acc_service.create_accessory(**data)
            self.accept()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


class ComboForm(QDialog):
    def __init__(self, combo: dict | None = None, parent=None):
        super().__init__(parent)
        self._combo = combo
        self.setWindowTitle("Sửa combo" if combo else "Thêm combo")
        self.setMinimumSize(500, 350)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_ten = QLineEdit()
        self.spin_gia = QDoubleSpinBox()
        self.spin_gia.setRange(0, 10_000_000_000)
        self.spin_gia.setDecimals(0)
        self.spin_gia.setPrefix("VND ")
        self.txt_mo_ta = QLineEdit()

        form.addRow("Tên *:", self.txt_ten)
        form.addRow("Giá combo *:", self.spin_gia)
        form.addRow("Mô tả:", self.txt_mo_ta)

        layout.addLayout(form)

        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["Phụ kiện", "Số lượng", "Xóa"])
        layout.addWidget(QLabel("Các phụ kiện trong combo:"))
        layout.addWidget(self.items_table)

        self._load_accessories()

        btn_add_item = QPushButton("Thêm phụ kiện")
        btn_add_item.clicked.connect(self._add_item_row)
        layout.addWidget(btn_add_item)

        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        if combo:
            self._fill_data(combo)

    def _load_accessories(self):
        self._accessories = acc_service.list_accessories()

    def _add_item_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        combo_acc = QComboBox()
        for acc in self._accessories:
            combo_acc.addItem(f"{acc['ten']} - {acc['gia']:,.0f} VND", acc["id"])
        self.items_table.setCellWidget(row, 0, combo_acc)

        spin = QSpinBox()
        spin.setRange(1, 99)
        spin.setValue(1)
        self.items_table.setCellWidget(row, 1, spin)

        btn_del = QPushButton("X")
        btn_del.clicked.connect(lambda: self._delete_row(row))
        self.items_table.setCellWidget(row, 2, btn_del)

    def _delete_row(self, row: int):
        self.items_table.removeRow(row)

    def _fill_data(self, combo: dict):
        self.txt_ten.setText(combo.get("ten", ""))
        self.spin_gia.setValue(combo.get("gia_combo", 0))
        self.txt_mo_ta.setText(combo.get("mo_ta") or "")

        items = acc_service.get_combo_items(combo["id"])
        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            combo_acc = QComboBox()
            for acc in self._accessories:
                combo_acc.addItem(f"{acc['ten']} - {acc['gia']:,.0f} VND", acc["id"])
            idx = combo_acc.findData(item["accessory_id"])
            if idx >= 0:
                combo_acc.setCurrentIndex(idx)
            self.items_table.setCellWidget(row, 0, combo_acc)

            spin = QSpinBox()
            spin.setRange(1, 99)
            spin.setValue(item["so_luong"])
            self.items_table.setCellWidget(row, 1, spin)

            btn_del = QPushButton("X")
            btn_del.clicked.connect(lambda _, r=row: self._delete_row(r))
            self.items_table.setCellWidget(row, 2, btn_del)

    def _on_save(self):
        data = {
            "ten": self.txt_ten.text().strip(),
            "gia_combo": self.spin_gia.value(),
            "mo_ta": self.txt_mo_ta.text().strip() or None,
        }
        items = []
        for row in range(self.items_table.rowCount()):
            combo_acc = self.items_table.cellWidget(row, 0)
            spin = self.items_table.cellWidget(row, 1)
            if combo_acc and spin:
                items.append({
                    "accessory_id": combo_acc.currentData(),
                    "so_luong": spin.value(),
                })
        try:
            if self._combo:
                acc_service.update_combo(self._combo["id"], **data)
                acc_service.update_combo_items(self._combo["id"], items)
            else:
                acc_service.create_combo(**data, items=items)
            self.accept()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


class AccessoryView(QWidget):
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self._current_user = current_user
        self._is_admin = current_user.get("role") == "admin"

        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # Tab: Phụ kiện
        acc_tab = QWidget()
        acc_layout = QVBoxLayout(acc_tab)

        # Filter bar
        filter_layout = QHBoxLayout()
        self.cbo_filter_loai = QComboBox()
        self.cbo_filter_loai.addItems(["Tất cả"] + list(_LOAI_LABELS.keys()))
        self.cbo_filter_loai.currentTextChanged.connect(self._on_filter)
        filter_layout.addWidget(QLabel("Loại:"))
        filter_layout.addWidget(self.cbo_filter_loai)
        filter_layout.addStretch()
        acc_layout.addLayout(filter_layout)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        acc_layout.addWidget(self.table)

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
        acc_layout.addLayout(btn_layout)

        self.lbl_warning = QLabel()
        self.lbl_warning.setStyleSheet("color: #c0392b; font-weight: bold;")
        acc_layout.addWidget(self.lbl_warning)

        tabs.addTab(acc_tab, "Phụ kiện")

        # Tab: Combo
        combo_tab = QWidget()
        combo_layout = QVBoxLayout(combo_tab)

        self.combo_table = QTableView()
        self.combo_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.combo_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        combo_layout.addWidget(self.combo_table)

        combo_btn_layout = QHBoxLayout()
        self.btn_add_combo = QPushButton("Thêm combo")
        self.btn_edit_combo = QPushButton("Sửa combo")
        self.btn_delete_combo = QPushButton("Xóa combo")
        self.btn_refresh_combo = QPushButton("Làm mới")

        self.btn_add_combo.clicked.connect(self._on_add_combo)
        self.btn_edit_combo.clicked.connect(self._on_edit_combo)
        self.btn_delete_combo.clicked.connect(self._on_delete_combo)
        self.btn_refresh_combo.clicked.connect(self._load_combos)

        combo_btn_layout.addWidget(self.btn_add_combo)
        combo_btn_layout.addWidget(self.btn_edit_combo)
        combo_btn_layout.addWidget(self.btn_delete_combo)
        combo_btn_layout.addStretch()
        combo_btn_layout.addWidget(self.btn_refresh_combo)
        combo_layout.addLayout(combo_btn_layout)

        tabs.addTab(combo_tab, "Combo")

        layout.addWidget(tabs)

        # Models
        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["ID", "Tên", "Mô tả", "Loại", "Giá", "Tồn kho"])
        self.table.setModel(self._model)

        self._combo_model = QStandardItemModel()
        self._combo_model.setHorizontalHeaderLabels(["ID", "Tên", "Giá combo", "Mô tả"])
        self.combo_table.setModel(self._combo_model)

        if not self._is_admin:
            self.btn_add.setVisible(False)
            self.btn_delete.setVisible(False)
            self.btn_add_combo.setVisible(False)
            self.btn_delete_combo.setVisible(False)

        self._all_data = []
        self._load_data()
        self._load_combos()

    def _load_data(self):
        self._all_data = acc_service.list_accessories()
        self._display_data(self._all_data)

        # Low stock warning
        warnings = acc_service.kiem_tra_canh_bao_pk()
        if warnings:
            self.lbl_warning.setText(f"Cảnh báo: {len(warnings)} phụ kiện có tồn kho thấp")
        else:
            self.lbl_warning.setText("")

    def _display_data(self, data: list):
        self._model.removeRows(0, self._model.rowCount())
        for acc in data:
            loai = _LOAI_LABELS.get(acc.get("loai", ""), acc.get("loai", ""))
            row = [
                QStandardItem(str(acc["id"])),
                QStandardItem(acc["ten"]),
                QStandardItem(acc.get("mo_ta") or ""),
                QStandardItem(loai),
                QStandardItem(f"{acc['gia']:,.0f}"),
                QStandardItem(str(acc["ton_kho"])),
            ]
            self._model.appendRow(row)

    def _load_combos(self):
        self._combo_model.removeRows(0, self._combo_model.rowCount())
        for combo in acc_service.list_combos():
            row = [
                QStandardItem(str(combo["id"])),
                QStandardItem(combo["ten"]),
                QStandardItem(f"{combo['gia_combo']:,.0f}"),
                QStandardItem(combo.get("mo_ta") or ""),
            ]
            self._combo_model.appendRow(row)

    def _on_filter(self, text: str):
        if text == "Tất cả":
            self._display_data(self._all_data)
        else:
            filtered = [a for a in self._all_data if a.get("loai") == text]
            self._display_data(filtered)

    def _get_selected_id(self) -> int | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        row = indexes[0].row()
        return int(self._model.item(row, 0).text())

    def _get_selected_combo_id(self) -> int | None:
        indexes = self.combo_table.selectionModel().selectedRows()
        if not indexes:
            return None
        row = indexes[0].row()
        return int(self._combo_model.item(row, 0).text())

    def _on_add(self):
        dlg = AccessoryForm(parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_edit(self):
        acc_id = self._get_selected_id()
        if acc_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn phụ kiện.")
            return
        acc = acc_service.get_accessory(acc_id)
        dlg = AccessoryForm(accessory=acc, parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_delete(self):
        acc_id = self._get_selected_id()
        if acc_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn phụ kiện.")
            return
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa phụ kiện này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                acc_service.delete_accessory(acc_id, self._current_user)
                self._load_data()
            except BusinessError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _on_add_combo(self):
        dlg = ComboForm(parent=self)
        if dlg.exec() == 1:
            self._load_combos()

    def _on_edit_combo(self):
        combo_id = self._get_selected_combo_id()
        if combo_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn combo.")
            return
        combo = acc_service.get_combo(combo_id)
        dlg = ComboForm(combo=combo, parent=self)
        if dlg.exec() == 1:
            self._load_combos()

    def _on_delete_combo(self):
        combo_id = self._get_selected_combo_id()
        if combo_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn combo.")
            return
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa combo này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                acc_service.delete_combo(combo_id, self._current_user)
                self._load_combos()
            except BusinessError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))