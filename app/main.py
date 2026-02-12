from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.services.storage import ensure_storage
from app.ui.main_window import MainWindow


def main() -> int:
    ensure_storage()
    app = QApplication(sys.argv)
    app.setStyleSheet(
        "QMainWindow{background:#f3f5f8;} QGroupBox{font-weight:bold; margin-top:12px;}"
        "QGroupBox::title{subcontrol-origin: margin; left: 10px; padding:0 4px;}"
        "QTextEdit,QLineEdit,QComboBox{background:#ffffff;border:1px solid #dbe1e8;border-radius:6px;padding:4px;}"
        "QPushButton{background:#1d4ed8;color:white;padding:8px;border-radius:6px;}"
        "QPushButton:disabled{background:#94a3b8;}"
    )
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
