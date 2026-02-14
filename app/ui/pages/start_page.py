from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QHBoxLayout, QVBoxLayout, QWidget


class StartPage(QWidget):
    load_requested = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        head = QHBoxLayout()
        head.addWidget(QLabel("<h2>Start</h2>"))
        help_btn = QPushButton("?")
        help_btn.setObjectName("helpButton")
        help_btn.setFixedWidth(28)
        help_btn.clicked.connect(self._show_help)
        head.addStretch()
        head.addWidget(help_btn)
        layout.addLayout(head)

        info = QLabel("Gespeicherte Projekte")
        info.setStyleSheet("color:#94a3b8;")
        layout.addWidget(info)
        self.project_list = QListWidget()
        self.project_list.setAlternatingRowColors(True)
        self.open_btn = QPushButton("Projekt laden")
        self.open_btn.clicked.connect(self._emit_open)
        layout.addWidget(self.project_list)
        layout.addWidget(self.open_btn)

    def _show_help(self) -> None:
        QMessageBox.information(
            self,
            "Hilfe: Start",
            "Hier siehst du vorhandene Projekte.\n"
            "• Eintrag auswählen\n"
            "• Auf 'Projekt laden' klicken\n"
            "Die Navigation links zeigt Projektübersicht, Etagen und Räume.",
        )

    def set_projects(self, entries: list[dict]) -> None:
        self.project_list.clear()
        for e in entries:
            item = QListWidgetItem(f"{e['name']}\n{e['path']}")
            item.setData(32, e["path"])
            self.project_list.addItem(item)

    def _emit_open(self) -> None:
        current = self.project_list.currentItem()
        if not current:
            return
        path = current.data(32)
        if path:
            self.load_requested.emit(path)
