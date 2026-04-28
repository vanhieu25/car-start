"""Danh sách nhà cung cấp với CRUD + đánh giá."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QMessageBox, QAbstractItemView, QLabel, QDialog, QFormLayout,
    QLineEdit, QSpinBox, QTextEdit, QComboBox, QTabWidget, QTableWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from src.modules.supplier import service as supplier_service
from src.core.exceptions import BusinessError


class SupplierForm(QDialog):
    def __init__(self, supplier: dict | None = None, parent=None):
        super().__init__(parent)
        self._supplier = supplier
        self.setWindowTitle("Sửa nhà cung cấp" if supplier else "Thêm nhà cung cấp")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_ten = QLineEdit()
        self.txt_dia_chi = QLineEdit()
        self.txt_sdt = QLineEdit()
        self.txt_email = QLineEdit()
        self.txt_nguoi_lien_he = QLineEdit()

        form.addRow("Tên *:", self.txt_ten)
        form.addRow("Địa chỉ:", self.txt_dia_chi)
        form.addRow("SĐT:", self.txt_sdt)
        form.addRow("Email:", self.txt_email)
        form.addRow("Người liên hệ:", self.txt_nguoi_lien_he)

        layout.addLayout(form)

        btn_save = QPushButton("Lưu")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

        if supplier:
            self._fill_data(supplier)

    def _fill_data(self, sup: dict):
        self.txt_ten.setText(sup.get("ten", ""))
        self.txt_dia_chi.setText(sup.get("dia_chi") or "")
        self.txt_sdt.setText(sup.get("sdt") or "")
        self.txt_email.setText(sup.get("email") or "")
        self.txt_nguoi_lien_he.setText(sup.get("nguoi_lien_he") or "")

    def _on_save(self):
        data = {
            "ten": self.txt_ten.text().strip(),
            "dia_chi": self.txt_dia_chi.text().strip() or None,
            "sdt": self.txt_sdt.text().strip() or None,
            "email": self.txt_email.text().strip() or None,
            "nguoi_lien_he": self.txt_nguoi_lien_he.text().strip() or None,
        }
        try:
            if self._supplier:
                supplier_service.update_supplier(self._supplier["id"], **data)
            else:
                supplier_service.create_supplier(**data)
            self.accept()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


class SupplierRatingDialog(QDialog):
    def __init__(self, supplier_id: int, parent=None):
        super().__init__(parent)
        self._supplier_id = supplier_id
        self.setWindowTitle("Đánh giá nhà cung cấp")
        self.setMinimumSize(350, 300)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.spin_chat_luong = QSpinBox()
        self.spin_chat_luong.setRange(1, 5)
        self.spin_thoi_gian_giao = QSpinBox()
        self.spin_thoi_gian_giao.setRange(1, 5)
        self.spin_gia_ca = QSpinBox()
        self.spin_gia_ca.setRange(1, 5)
        self.txt_ghi_chu = QTextEdit()

        form.addRow("Chất lượng (1-5):", self.spin_chat_luong)
        form.addRow("Thời gian giao (1-5):", self.spin_thoi_gian_giao)
        form.addRow("Giá cả (1-5):", self.spin_gia_ca)
        form.addRow("Ghi chú:", self.txt_ghi_chu)

        layout.addLayout(form)

        btn_save = QPushButton("Lưu đánh giá")
        btn_save.clicked.connect(self._on_save)
        layout.addWidget(btn_save)

    def _on_save(self):
        try:
            supplier_service.add_rating(
                self._supplier_id,
                self.spin_chat_luong.value(),
                self.spin_thoi_gian_giao.value(),
                self.spin_gia_ca.value(),
                self.txt_ghi_chu.toPlainText().strip() or None,
            )
            self.accept()
        except BusinessError as e:
            QMessageBox.warning(self, "Lỗi", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))


class SupplierDetailDialog(QDialog):
    def __init__(self, supplier_id: int, parent=None):
        super().__init__(parent)
        self._supplier_id = supplier_id
        self.setWindowTitle("Chi tiết nhà cung cấp")
        self.setMinimumSize(700, 450)

        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # Tab: Thông tin
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        info = supplier_service.get_supplier(supplier_id)
        info_layout.addWidget(QLabel(f"Tên: {info['ten']}"))
        info_layout.addWidget(QLabel(f"Địa chỉ: {info.get('dia_chi') or '-'}"))
        info_layout.addWidget(QLabel(f"SĐT: {info.get('sdt') or '-'}"))
        info_layout.addWidget(QLabel(f"Email: {info.get('email') or '-'}"))
        info_layout.addWidget(QLabel(f"Người liên hệ: {info.get('nguoi_lien_he') or '-'}"))
        info_layout.addStretch()
        tabs.addTab(info_tab, "Thông tin")

        # Tab: Đánh giá
        ratings_tab = QWidget()
        ratings_layout = QVBoxLayout(ratings_tab)
        ratings_table = QTableView()
        ratings_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        ratings_layout.addWidget(ratings_table)

        avg = supplier_service.get_average_rating(supplier_id)
        if avg and avg["so_danh_gia"] > 0:
            ratings_layout.addWidget(QLabel(
                f"Trung bình: Chất lượng {avg['avg_chat_luong']:.1f} | "
                f"Giao hàng {avg['avg_thoi_gian_giao']:.1f} | "
                f"Giá {avg['avg_gia_ca']:.1f} ({avg['so_danh_gia']} đánh giá)"
            ))

        btn_add_rating = QPushButton("Thêm đánh giá")
        btn_add_rating.clicked.connect(lambda: self._add_rating(ratings_table))
        ratings_layout.addWidget(btn_add_rating)

        ratings_model = QStandardItemModel()
        ratings_model.setHorizontalHeaderLabels(["ID", "Chất lượng", "Giao hàng", "Giá", "Ngày", "Ghi chú"])
        ratings_table.setModel(ratings_model)
        for r in supplier_service.get_ratings(supplier_id):
            row = [
                QStandardItem(str(r["id"])),
                QStandardItem(str(r["chat_luong"])),
                QStandardItem(str(r["thoi_gian_giao"])),
                QStandardItem(str(r["gia_ca"])),
                QStandardItem(str(r["ngay_danh_gia"])),
                QStandardItem(r["ghi_chu"] or ""),
            ]
            ratings_model.appendRow(row)
        tabs.addTab(ratings_tab, "Đánh giá")

        # Tab: Lịch sử nhập hàng
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        history_table = QTableView()
        history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        history_layout.addWidget(history_table)

        history_model = QStandardItemModel()
        history_model.setHorizontalHeaderLabels(["ID", "Xe", "Số lượng", "Giá nhập", "Ngày", "Ghi chú"])
        history_table.setModel(history_model)
        for h in supplier_service.get_import_history(supplier_id):
            row = [
                QStandardItem(str(h["id"])),
                QStandardItem(f"{h['hang']} {h['dong_xe']}"),
                QStandardItem(str(h["so_luong"])),
                QStandardItem(f"{h['gia_nhap']:,.0f}"),
                QStandardItem(str(h["ngay_nhap"])),
                QStandardItem(h["ghi_chu"] or ""),
            ]
            history_model.appendRow(row)
        tabs.addTab(history_tab, "Lịch sử nhập hàng")

        layout.addWidget(tabs)

        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _add_rating(self, table: QTableView):
        dlg = SupplierRatingDialog(self._supplier_id, self)
        if dlg.exec() == 1:
            model = table.model()
            model.removeRows(0, model.rowCount())
            for r in supplier_service.get_ratings(self._supplier_id):
                row = [
                    QStandardItem(str(r["id"])),
                    QStandardItem(str(r["chat_luong"])),
                    QStandardItem(str(r["thoi_gian_giao"])),
                    QStandardItem(str(r["gia_ca"])),
                    QStandardItem(str(r["ngay_danh_gia"])),
                    QStandardItem(r["ghi_chu"] or ""),
                ]
                model.appendRow(row)


class SupplierView(QWidget):
    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self._current_user = current_user
        self._is_admin = current_user.get("role") == "admin"

        layout = QVBoxLayout(self)

        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Thêm")
        self.btn_edit = QPushButton("Sửa")
        self.btn_delete = QPushButton("Xóa")
        self.btn_rating = QPushButton("Đánh giá")
        self.btn_refresh = QPushButton("Làm mới")

        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_rating.clicked.connect(self._on_rating)
        self.btn_refresh.clicked.connect(self._load_data)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_rating)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_refresh)
        layout.addLayout(btn_layout)

        if not self._is_admin:
            self.btn_add.setVisible(False)
            self.btn_delete.setVisible(False)

        self._model = QStandardItemModel()
        self._model.setHorizontalHeaderLabels(["ID", "Tên", "Địa chỉ", "SĐT", "Email", "Người liên hệ"])
        self.table.setModel(self._model)

        self._load_data()

    def _load_data(self):
        self._model.removeRows(0, self._model.rowCount())
        for sup in supplier_service.list_suppliers():
            row = [
                QStandardItem(str(sup["id"])),
                QStandardItem(sup["ten"]),
                QStandardItem(sup.get("dia_chi") or ""),
                QStandardItem(sup.get("sdt") or ""),
                QStandardItem(sup.get("email") or ""),
                QStandardItem(sup.get("nguoi_lien_he") or ""),
            ]
            self._model.appendRow(row)

    def _get_selected_id(self) -> int | None:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        row = indexes[0].row()
        return int(self._model.item(row, 0).text())

    def _on_add(self):
        dlg = SupplierForm(parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_edit(self):
        sup_id = self._get_selected_id()
        if sup_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhà cung cấp.")
            return
        sup = supplier_service.get_supplier(sup_id)
        dlg = SupplierForm(supplier=sup, parent=self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_delete(self):
        sup_id = self._get_selected_id()
        if sup_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhà cung cấp.")
            return
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có chắc muốn xóa nhà cung cấp này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                supplier_service.delete_supplier(sup_id, self._current_user)
                self._load_data()
            except BusinessError as e:
                QMessageBox.warning(self, "Lỗi", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def _on_rating(self):
        sup_id = self._get_selected_id()
        if sup_id is None:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn nhà cung cấp.")
            return
        dlg = SupplierRatingDialog(sup_id, self)
        if dlg.exec() == 1:
            self._load_data()

    def _on_double_click(self):
        sup_id = self._get_selected_id()
        if sup_id:
            dlg = SupplierDetailDialog(sup_id, self)
            dlg.exec()