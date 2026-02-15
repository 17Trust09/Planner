from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from app.services.storage import ensure_storage
from app.ui.main_window import MainWindow

SPLASH_MIN_SECONDS = 8.0


def _load_logo_pixmap() -> QPixmap | None:
    exe_dir = Path(sys.executable).resolve().parent
    argv0_dir = Path(sys.argv[0]).resolve().parent if sys.argv and sys.argv[0] else exe_dir
    meipass_dir = Path(getattr(sys, "_MEIPASS", exe_dir))

    # Reihenfolge bewusst: erst benutzernahe Orte (neben EXE / aktueller Ordner),
    # danach Bundle-Verzeichnisse. So funktioniert One-File-EXE zuverlässig.
    search_bases = []
    for base in [
        exe_dir,
        exe_dir.parent,
        argv0_dir,
        argv0_dir.parent,
        Path.cwd(),
        meipass_dir,
    ]:
        resolved = base.resolve()
        if resolved not in search_bases:
            search_bases.append(resolved)

    preferred_names = [
        "logo.png",
        "logo.jpg",
        "logo.jpeg",
        "logo.webp",
        "splash_logo.png",
        "splash_logo.jpg",
        "splash_logo.jpeg",
    ]

    for base in search_bases:
        for rel in [Path("."), Path("data"), Path("app/assets")]:
            folder = base / rel
            for name in preferred_names:
                candidate = folder / name
                if candidate.exists():
                    pixmap = QPixmap(str(candidate))
                    if not pixmap.isNull():
                        return pixmap

    # Fallback: erstes Bild in EXE-Ordner bzw. data-Unterordnern laden,
    # damit auch frei benannte Dateien funktionieren.
    for base in search_bases:
        for folder in [base, base / "data"]:
            if not folder.exists():
                continue
            for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
                for candidate in sorted(folder.glob(ext)):
                    pixmap = QPixmap(str(candidate))
                    if not pixmap.isNull():
                        return pixmap

    return None


def _create_splash() -> QSplashScreen:
    pixmap = QPixmap(900, 520)
    pixmap.fill(QColor("#081125"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    bg_gradient = QLinearGradient(0, 0, 900, 520)
    bg_gradient.setColorAt(0.0, QColor("#071226"))
    bg_gradient.setColorAt(0.5, QColor("#0b1d39"))
    bg_gradient.setColorAt(1.0, QColor("#0c2b54"))
    painter.fillRect(0, 0, 900, 520, bg_gradient)

    painter.setPen(QColor("#2A3A57"))
    painter.drawRoundedRect(30, 30, 840, 460, 18, 18)

    logo_pixmap = _load_logo_pixmap()
    if logo_pixmap is not None:
        scaled = logo_pixmap.scaled(360, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (900 - scaled.width()) // 2
        painter.drawPixmap(x, 72, scaled)
    else:
        painter.setPen(QColor("#bfefff"))
        painter.setFont(QFont("Arial", 42, QFont.Black))
        painter.drawText(0, 145, 900, 80, Qt.AlignCenter, "Tim Hölzer")

    painter.setPen(QColor("#EAF6FF"))
    painter.setFont(QFont("Arial", 24, QFont.Bold))
    painter.drawText(0, 302, 900, 40, Qt.AlignCenter, "Tim Hölzer")

    painter.setPen(QColor("#B9DFFF"))
    painter.setFont(QFont("Arial", 16, QFont.DemiBold))
    painter.drawText(0, 344, 900, 32, Qt.AlignCenter, "Homeplanung")

    painter.setPen(QColor("#7EA8CC"))
    painter.setFont(QFont("Arial", 11))
    painter.drawText(0, 388, 900, 24, Qt.AlignCenter, "Smart Home · Elektrik · IT-Netzwerk")
    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowFlag(Qt.WindowStaysOnTopHint, True)
    return splash


def main() -> int:
    splash_started_at = time.perf_counter()
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

    elapsed = time.perf_counter() - splash_started_at
    remaining = max(0.0, SPLASH_MIN_SECONDS - elapsed)
    end_time = time.perf_counter() + remaining
    while time.perf_counter() < end_time:
        app.processEvents()
        time.sleep(0.05)

    window = MainWindow()
    window.show()
    splash.finish(window)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
