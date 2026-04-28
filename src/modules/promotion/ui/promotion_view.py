"""Danh sách khuyến mãi với CRUD + scope filter."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QAbstractItemView, QLabel, QDialog, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QRadioButton, QButtonGroup,
    QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from src.modules.promotion import service as promo_service
from src.core.exceptions import BusinessError

_LOAI_KM_LABELS = {
    "giam_tien": "Giảm tiền",
    "tang_pk": "Tặng phụ kiện",
    "giam_lai": "Giảm lãi",
    "combo": "Combo",
}

_PHAM_VI_LABELS = {
    "toan_bo": "Toàn bộ",
    "hang_xe": "Hãng xe",
    "dong_xe": "Dòng xe",
    "ton_kho_lau": "Tồn kho lâu",
}

_TRANG_THAI_LABELS = {
    "dang_chay": "Đang chạy",
    "tam_dung": "Tạm dừng",
    "da_ket_thuc": "Đã kết thúc",
}


class PromotionForm(QDialog):
    def __init__(self, promotion: dict | None = None, parent=None):
        super().__init__(parent)
        self._promo = promotion
        self.setWindowTitle("Sửa khuyến mãi" if promotion else "Thêm khuyến mãi")
        self.setMinimumSize(480, 500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_ten = QLineEdit()
        self.txt_mo_ta = QTextEdit()
        self.txt_mo_ta.setMaximumHeight(60)

        self.cbo_loai = QComboBox()
        self.cbo_loai.addItems(list(_LOAI_KM_LABELS.keys()))

        # Kiểu giảm: cố định hoặc phần trăm
        self.radio_co_dinh = QRadioButton("Cố định (VND)")
        self.radio_phan_tram = QRadioButton("Phần trăm (%)")
        self.radio_co_dinh.setChecked(True)
        kieu_layout = QHBoxLayout()
        kieu_layout.addWidget(self.radio_co_dinh)
        kieu_layout.addWidget(self.radio_phan_tram)

        self.spin_muc_giam = QSpinBox()
        self.spin_muc_giam.setRange(0, 10_000_000_000)

        self.date_tu_ngay = QDateEdit()
        self.date_tu_ngay.setCalendarPopup(True)
        self.date_tu_ngay.setDate(QDate.currentDate())

        self.date_den_ngay = QDateEdit()
        self.date_den_ngay.setCalendarPopup(True)
        self.date_den_ngay.setDate(QDate.currentDate().addMonths(1))

        self.cbo_pham_vi = QComboBox()
        self.cbo_pham_vi.addItems(list(_PHAM_VI_LABELS.keys()))
        self.cbo_pham_vi.currentTextChanged.connect(self._on_pham_vi_changed)

        self.txt_pham_vi_id = QLineEdit()
        self.txt_pham_vi_id.setPlaceholderText("VD: Toyota, Camry, ...")

        self.spin_ton_kho_ngay = QSpinBox()
        self.spin_ton_kho_ngay.setRange(0, 999)
        self.spin_ton_kho_ngay.setPrefix("Tồn kho > ")
        self.spin_ton_kho_ngay.setSuffix(" ngày")
        self.spin_ton_kho_ngay.setValue(30)

        self.cbo_trang_thai = QComboBox()
        self.cbo_trang_thai.addItems(["dang_chay", "tam_dung", "da_ket_thuc"])

        form.addRow("Tên *:", self.txt_ten)
        form.addRow("Mô tả:", self.txt_mo_ta)
        form.addRow("Loại:", self.cbo_loai)
        form.addRow("Kiểu giảm:", kieu_layout)
        form.addRow("Mức giảm *:", self.spin_muc_giam)
        form.addRow("Từ ngày:", self.date_tu_ngay)
        form.addRow("Đến ngày:", self.date_den_ngay)
        form.addRow("Phạm vi:", self.cbo_pham_vi)
        form.addRow("ID phạm vi:", self.txt_pham_vi_id)
        form.addRow("Điều kiện tồn kho:", self.spin_ton_kho_ngay)
        form.addRow("Trạng thái:", self.cbo_trang_thai)

        layout.addLayout(form)

        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        if promotion:
            self._fill_data(promotion)

        self._on_pham_vi_changed(self.cbo_pham_vi.currentText())

    def _on_pham_vi_changed(self, text: str):
        self.txt_pham_vi_id.setVisible(text in ("hang_xe", "dong_xe"))
        self.spin_ton_kho_ngay.setVisible(text == "ton_kho_lau")

    def _fill_data(self, promo: dict):
        self.txt_ten.setText(promo.get("ten", ""))
        self.txt_mo_ta.setPlainText(promo.get("mo_ta") or "")
        idx = self.cbo_loai.findText(promo.get("loai", ""))
        if idx >= 0:
            self.cbo_loai.setCurrentIndex(idx)

        if promo.get("kieu_giam") == "phan_tram":
            self.radio_phan_tram.setChecked(True)
        else:
            self.radio_co_dinh.setChecked(True)

        self.spin_muc_giam.setValue(int(promo.get("muc_giam", 0)))

        if promo.get("tu_ngay"):
            self.date_tu_ngay.setDate(QDate.fromString(promo["tu_ngay"], Qt.DateFormat.ISODate))
        if promo.get("den_ngay"):
            self.date_den_ngay.setDate(QDate.fromString(promo["den_ngay"], Qt.DateFormat.ISODate))

        idx = self.cbo_pham_vi.findText(promo.get("pham_vi", ""))
        if idx >= 0:
            self.cbo_pham_vi.setCurrentIndex(idx)

        self.txt_pham_vi_id.setText(promo.get("pham_vi_id") or "")
        self.spin_ton_kho_ngay.setValue(promo.get("dieu_kien_ton_kho_ngay") or 0)

        idx = self.cbo_trang_thai.findText(promo.get("trang_thai", "dang_chay"))
        if idx >= 0:
            self.cbo_trang_thai.setCurrentIndex(idx)

    def _on_save(self):
        kieu_giam = "phan_tram" if self.radio_phan_tram.isChecked() else "co_dinh"
        data = {
            "ten": self.txt_ten.text().strip(),
            "mo_ta": self.txt_mo_ta.toPlainText().strip() or None,
            "loai": self.cbo_loai.currentText(),
            "kieu_giam": kieu_giam,
            "muc_giam": self.spin_muc_giam.value(),
            "tu_ngay": self.date_tu_ngay.date().toString(Qt.DateFormat.ISODate),
            "den_ngay": self.date_den_ngay.date().toString(Qt.DateFormat.ISODate),
            "pham_vi": self.cbo_pham_vi.currentText(),
            "pham_vi_id": self.txt_pham_vi_id.text().strip() or None,
            "dieu_kien_ton_kho_ngay": self.spin_ton_kho_ngay.value() if self.cbo_pham_vi.currentText() == "ton_kho_lau" else None,
            "trang_thai": self.cbo_trang_thai.currentText(),
        }
        try:
            if self._promo:
                promo_service.update_promotion(self._promo["id"], **data)
            else:
                promo_service.create_promotion(**data)
            self.accept()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


class PromotionView(QWidget):
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self._current_user = current_user
        self._is_admin = current_user.get("role") == "admin"

        layout = QVBoxLayout(self)

        # Filter bar
        filter_layout = QHBoxLayout()
        self.cbo_filter_status = QComboBox()
        self.cbo_filter_status.addItems(["Tất cả", "dang_chay", "tam_dung", "da_ket_thuc"])
        self.cbo_filter_status.currentTextChanged.connect(self._on_filter)
        filter_layout.addWidget(QLabel("Trạng thái:"))
        filter_layout.addWidget(self.cbo_filter_status)
        filter_layout.addStretch()
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
        self.btn_tam_dung = QPushButton("Tạm dừng")
        self.btn_kich_hoat = QPushButton("Kích hoạt")
        self.btn_refresh = QPushButton("Làm mới")

        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_tam_dung.clicked.connect(self._on_tam_dung)
        self.btn_kich_hoat.clicked.connect(self._on_kich_hoat)
        self.btn_refresh.clicked.connect(self._load_data)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_tam_dung)
        btn_layout.addWidget(self.btn_kich_hoat)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        layout.addLayout(btn_layout)

        if not self._is_admin:
            self.btn_add.setVisible(False)
            self.btn_delete.setVisible(False)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(
            ["ID", "Tên", "Loại", "Kiểu", "Mức giảm", "Từ ngày", "Đến ngày", "Phạm vi", "Trạng thái"]
        )
        self.table.setModel(self._model)

        self._all_data = []
        self._load_data()

    def _load_data(self):
        self._all_data = promo_service.list_promotions()
        self._display_data(self._all_data)

    def _display_data(self, data: list):
        self._model.removeRows(0, self._model.rowCount())
        for promo in data:
            loai = _LOAI_KM_LABELS.get(promo.get("loai", ""), promo.get("loai", ""))
            kieu = "Phần trăm" if promo.get("kieu_giam") == "phan_tram" else "Cố định"
            pham_vi = _PHAM_VI_LABELS.get(promo.get("pham_vi", ""), promo.get("pham_vi", ""))
            trang_thai = _TRANG_THAI_LABELS.get(promo.get("trang_thai", ""), promo.get("trang_thai", ""))

            row = [
                QStandardItem(str(promo["id"])),
                QStandardItem(promo["ten"]),
                QStandardItem(loai),
                QStandardItem(kieu),
                QStandardItem(f"{promo['muc_giam']:,.0f}"),
                QStandardItem(promo.get("tu_ngay") or ""),
                QStandardItem(promo.get("den_ngay") or ""),
                QStandardItem(pham_vi),
                QStandardItem(trang_thai),
            ]
            self._model.appendRow(row)

    def _on_filter(self, text: str):
        if text == "Tất cả":
            self._display_data(self._all_data)
        else:
            filtered = [p for p in self._all_data if p.get("trang_thai") == text]
            self._display_data(filtered)

    def _get_selected_id(self) -> int | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        row = indexes[0].row()
        return int(self._model.item(row, 0).text())

    def _on_add(self):
        dlg = PromotionForm(parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_edit(self):
        promo_id = self._get_selected_id()
        if promo_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khuyến mãi.")
            return
        promo = promo_service.get_promotion(promo_id)
        dlg = PromotionForm(promotion=promo, parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_delete(self):
        promo_id = self._get_selected_id()
        if promo_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khuyến mãi.")
            return
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa khuyến mãi này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                promo_service.delete_promotion(promo_id, self._current_user)
                self._load_data()
            except BusinessError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _on_tam_dung(self):
        promo_id = self._get_selected_id()
        if promo_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khuyến mãi.")
            return
        try:
            promo_service.tam_dung(promo_id, self._current_user)
            self._load_data()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _on_kich_hoat(self):
        promo_id = self._get_selected_id()
        if promo_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khuyến mãi.")
            return
        try:
            promo_service.kich_hoat(promo_id, self._current_user)
            self._load_data()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))