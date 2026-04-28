"""Điểm vào ứng dụng PyQt6 quản lý đại lý xe hơi."""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

# Thêm thư mục gốc vào sys.path để import src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.db.init_db import init_db
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("QuanLyDaiLyXe")
    app.setOrganizationName("CarDealer")

    # Khởi tạo DB nếu chưa tồn tại
    db_path = Path("app.db")
    if not db_path.exists():
        init_db(str(db_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
