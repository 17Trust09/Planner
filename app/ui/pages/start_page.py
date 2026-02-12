from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget, QInputDialog


class StartPage(QWidget):
    load_requested = Signal(str)
    delete_requested = Signal(str)
    rename_requested = Signal(str, str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Start</h2>"))
        layout.addWidget(QLabel("Gespeicherte Projekte"))
        self.project_list = QListWidget()
        btns = QHBoxLayout()
        self.open_btn = QPushButton("Projekt laden")
        self.rename_btn = QPushButton("Umbenennen")
        self.delete_btn = QPushButton("Löschen")
        self.open_btn.clicked.connect(self._emit_open)
        self.rename_btn.clicked.connect(self._emit_rename)
        self.delete_btn.clicked.connect(self._emit_delete)
        btns.addWidget(self.open_btn)
        btns.addWidget(self.rename_btn)
        btns.addWidget(self.delete_btn)
        layout.addWidget(self.project_list)
        layout.addLayout(btns)

    def set_projects(self, entries: list[dict]) -> None:
        self.project_list.clear()
        for e in entries:
            self.project_list.addItem(f"{e['name']}|{e['path']}")

    def _current_path(self) -> str | None:
        current = self.project_list.currentItem()
        if not current:
            return None
        return current.text().split("|", 1)[1]

    def _emit_open(self) -> None:
        path = self._current_path()
        if path:
            self.load_requested.emit(path)

    def _emit_delete(self) -> None:
        path = self._current_path()
        if path:
            self.delete_requested.emit(path)

    def _emit_rename(self) -> None:
        current = self.project_list.currentItem()
        if not current:
            return
        name, path = current.text().split("|", 1)
        new_name, ok = QInputDialog.getText(self, "Projekt umbenennen", "Neuer Name:", text=name)
        if ok and new_name.strip():
            self.rename_requested.emit(path, new_name.strip())
