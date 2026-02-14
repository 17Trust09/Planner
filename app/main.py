from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.services.storage import ensure_storage
from app.ui.main_window import MainWindow


def main() -> int:
    ensure_storage()
    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
        QWidget {
            background: #f3f6fb;
            color: #0f172a;
            font-size: 14px;
        }

        QMainWindow {
            background: #eef2f8;
        }

        QFrame#sidebar {
            background: #0f172a;
            border-radius: 14px;
            border: 1px solid #1e293b;
        }

        QFrame#contentPanel {
            background: #ffffff;
            border-radius: 14px;
            border: 1px solid #dbe3ef;
        }


        QPushButton {
            background: #e2e8f0;
            color: #0f172a;
            border: 1px solid #c9d5e5;
            border-radius: 8px;
            padding: 8px 10px;
            font-weight: 600;
        }

        QPushButton:hover {
            background: #d6e2f3;
        }

        QPushButton#primaryButton {
            background: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 10px 12px;
            font-weight: 600;
        }

        QPushButton#primaryButton:hover {
            background: #1d4ed8;
        }

        QPushButton#primaryButton:pressed {
            background: #1e40af;
        }

        QPushButton#primaryButton:disabled {
            background: #94a3b8;
            color: #e2e8f0;
        }

        QTreeWidget#navTree {
            background: #111827;
            color: #e5e7eb;
            border: 1px solid #1f2937;
            border-radius: 10px;
            padding: 6px;
            outline: none;
        }

        QTreeWidget#navTree::item {
            height: 26px;
            border-radius: 6px;
            padding: 3px 6px;
        }

        QTreeWidget#navTree::item:selected {
            background: #1d4ed8;
            color: #ffffff;
        }

        QTreeWidget#navTree::item:hover {
            background: #1f2937;
        }

        QLabel {
            background: transparent;
            color: #0f172a;
        }

        QWidget#topicCard {
            background: #ffffff;
            border: 1px solid #dbe3ef;
            border-radius: 10px;
        }

        QGroupBox {

            font-weight: 700;
            margin-top: 16px;
            border: 1px solid #dbe3ef;
            border-radius: 12px;
            padding: 14px;
            background: #f8fafc;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
            color: #0f172a;
        }

        QTextEdit,
        QLineEdit,
        QComboBox,
        QListWidget,
        QTableWidget,
        QTabWidget::pane {
            background: #ffffff;
            color: #0f172a;
            border: 1px solid #cdd7e4;
            border-radius: 8px;
            padding: 4px;
        }

        QTableWidget::item {
            padding: 6px;
        }

        QHeaderView::section {
            background: #e8eef7;
            color: #0f172a;
            border: none;
            border-right: 1px solid #d4deea;
            border-bottom: 1px solid #d4deea;
            padding: 6px;
            font-weight: 600;
        }

        QTabBar::tab {
            background: #e6edf8;
            color: #1e293b;
            padding: 8px 14px;
            border: 1px solid #ccd8ea;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 4px;
        }

        QTabBar::tab:selected {
            background: #ffffff;
            color: #0f172a;
            font-weight: 700;
        }

        QTabBar::tab:hover {
            background: #dbe7f8;
        }

        QScrollArea {
            border: none;
            background: transparent;
        }
        """
    )
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
