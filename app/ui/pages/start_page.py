from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget


class StartPage(QWidget):
    load_requested = Signal(str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Start</h2>"))
        layout.addWidget(QLabel("Gespeicherte Projekte"))
        self.project_list = QListWidget()
        self.open_btn = QPushButton("Projekt laden")
        self.open_btn.clicked.connect(self._emit_open)
        layout.addWidget(self.project_list)
        layout.addWidget(self.open_btn)

    def set_projects(self, entries: list[dict]) -> None:
        self.project_list.clear()
        for e in entries:
            self.project_list.addItem(f"{e['name']}|{e['path']}")

    def _emit_open(self) -> None:
        current = self.project_list.currentItem()
        if not current:
            return
        path = current.text().split("|", 1)[1]
        self.load_requested.emit(path)
