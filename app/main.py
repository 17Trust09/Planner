from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from app.services.storage import ensure_storage
from app.ui.main_window import MainWindow


def _create_splash() -> QSplashScreen:
    pixmap = QPixmap(760, 420)
    pixmap.fill(QColor("#0B1220"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.fillRect(30, 30, 700, 360, QColor("#111827"))

    painter.setPen(QColor("#60A5FA"))
    painter.setFont(QFont("Arial", 26, QFont.Bold))
    painter.drawText(0, 160, 760, 44, Qt.AlignCenter, "Hi, willkommen")

    painter.setPen(QColor("#E5E7EB"))
    painter.setFont(QFont("Arial", 22, QFont.Bold))
    painter.drawText(0, 206, 760, 44, Qt.AlignCenter, "zu Tims Homeplanung")

    painter.setPen(QColor("#94A3B8"))
    painter.setFont(QFont("Arial", 12))
    painter.drawText(0, 260, 760, 28, Qt.AlignCenter, "App wird gestartet …")
    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowFlag(Qt.WindowStaysOnTopHint, True)
    return splash


def main() -> int:
    app = QApplication(sys.argv)
    splash = _create_splash()
    splash.show()
    splash.showMessage("Lade Projektstruktur …", Qt.AlignBottom | Qt.AlignHCenter, QColor("#CBD5E1"))
    app.processEvents()

    ensure_storage()
    app.setStyleSheet(
        """
        QWidget {
            background: #0b1220;
            color: #e5e7eb;
            font-size: 14px;
        }

        QMainWindow {
            background: #030712;
        }

        QFrame#sidebar {
            background: #0f172a;
            border-radius: 14px;
            border: 1px solid #1f2a44;
        }

        QFrame#contentPanel {
            background: #111827;
            border-radius: 14px;
            border: 1px solid #263247;
        }

        QPushButton {
            background: #1f2937;
            color: #e5e7eb;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 8px 10px;
            font-weight: 600;
        }

        QPushButton:hover {
            background: #273449;
        }

        QPushButton#primaryButton {
            background: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 10px 12px;
            font-weight: 700;
        }

        QPushButton#primaryButton:hover {
            background: #1d4ed8;
        }

        QPushButton#primaryButton:pressed {
            background: #1e40af;
        }

        QPushButton#primaryButton:disabled {
            background: #475569;
            color: #cbd5e1;
        }

        QPushButton#secondaryButton {
            background: #111827;
            border: 1px solid #334155;
            color: #e2e8f0;
        }

        QPushButton#secondaryButton:hover {
            background: #1f2937;
        }

        QPushButton#helpButton {
            background: #374151;
            border: 1px solid #4b5563;
            color: #f8fafc;
            border-radius: 14px;
            font-weight: 800;
            padding: 2px;
        }

        QPushButton#helpButton:hover {
            background: #4b5563;
        }

        QTreeWidget#navTree {
            background: #111827;
            color: #e5e7eb;
            border: 1px solid #263247;
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
            background: #2563eb;
            color: #ffffff;
        }

        QTreeWidget#navTree::item:hover {
            background: #1f2937;
        }

        QLabel {
            background: transparent;
            color: #e5e7eb;
        }

        QLabel#projectInfo {
            background: #0b1324;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 8px;
            color: #cbd5e1;
            font-size: 12px;
        }

        QWidget#topicCard {
            background: #0f172a;
            border: 1px solid #2b3a55;
            border-radius: 10px;
        }

        QWidget#topicCard[missing=true],
        QWidget#topicCard[missing="true"] {
            border: 2px solid #ef4444;
            background: #1f0f16;
        }

        QGroupBox {
            font-weight: 700;
            margin-top: 16px;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 14px;
            background: #111827;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
            color: #cbd5e1;
        }

        QTextEdit,
        QLineEdit,
        QComboBox,
        QListWidget,
        QTableWidget,
        QTabWidget::pane {
            background: #0f172a;
            color: #e5e7eb;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 4px;
            selection-background-color: #2563eb;
            selection-color: #ffffff;
        }

        QTableWidget::item {
            padding: 6px;
        }

        QHeaderView::section {
            background: #1f2937;
            color: #e2e8f0;
            border: none;
            border-right: 1px solid #334155;
            border-bottom: 1px solid #334155;
            padding: 6px;
            font-weight: 700;
        }

        QTabBar::tab {
            background: #1f2937;
            color: #cbd5e1;
            padding: 8px 14px;
            border: 1px solid #334155;
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 4px;
        }

        QTabBar::tab:selected {
            background: #111827;
            color: #ffffff;
            font-weight: 700;
        }

        QTabBar::tab:hover {
            background: #273449;
        }

        QScrollArea {
            border: none;
            background: transparent;
        }

        QSplitter::handle {
            background: #1f2937;
            border-radius: 2px;
        }

        QSplitter::handle:horizontal {
            width: 8px;
            margin: 8px 2px;
        }

        QSplitter::handle:hover {
            background: #3b82f6;
        }


        QMessageBox {
            background: #0f172a;
        }

        QMessageBox QLabel {
            color: #e5e7eb;
        }
        """
    )
    splash.showMessage("Starte Oberfläche …", Qt.AlignBottom | Qt.AlignHCenter, QColor("#CBD5E1"))
    app.processEvents()

    window = MainWindow()
    window.show()
    splash.finish(window)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
