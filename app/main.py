from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.services.storage import ensure_storage
from app.ui.main_window import MainWindow


def main() -> int:
    ensure_storage()
    app = QApplication(sys.argv)
    app.setStyleSheet(
        "QMainWindow,QWidget{background:#f8fafc;color:#0f172a;}"
        "QScrollArea{border:none;}"
        "QGroupBox{font-weight:700; margin-top:12px; border:1px solid #cbd5e1; border-radius:8px; padding:8px; background:#ffffff;}"
        "QGroupBox::title{subcontrol-origin: margin; left: 10px; padding:0 6px; color:#0f172a; background:#ffffff;}"
        "QLabel{color:#1e293b;}"
        "QLineEdit,QTextEdit,QComboBox{background:#ffffff; color:#0f172a; border:1px solid #94a3b8; border-radius:6px; padding:6px;}"
        "QLineEdit:focus,QTextEdit:focus,QComboBox:focus{border:1px solid #2563eb;}"
        "QPushButton{background:#1d4ed8; color:#ffffff; border:none; padding:8px; border-radius:6px; font-weight:600;}"
        "QPushButton:hover{background:#1e40af;}"
        "QPushButton:pressed{background:#1e3a8a;}"
        "QPushButton:disabled{background:#94a3b8; color:#f8fafc;}"
        "QListWidget{background:#ffffff; color:#0f172a; border:1px solid #cbd5e1; border-radius:8px; padding:4px;}"
        "QListWidget::item{padding:6px 8px; border-radius:4px;}"
        "QListWidget::item:selected{background:#dbeafe; color:#1e3a8a;}"
    )
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
