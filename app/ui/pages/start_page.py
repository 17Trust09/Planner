from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QHBoxLayout, QVBoxLayout, QWidget


class StartPage(QWidget):
    load_requested = Signal(str)
    rename_requested = Signal(str)

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

        action_row = QHBoxLayout()
        self.open_btn = QPushButton("Projekt laden")
        self.open_btn.clicked.connect(self._emit_open)
        self.rename_btn = QPushButton("Projekt umbenennen")
        self.rename_btn.clicked.connect(self._emit_rename)
        action_row.addWidget(self.open_btn)
        action_row.addWidget(self.rename_btn)

        layout.addWidget(self.project_list)
        layout.addLayout(action_row)

    def _show_help(self) -> None:
        QMessageBox.information(
            self,
            "Hilfe: Start",
            "Hier siehst du vorhandene Projekte.\n"
            "• Eintrag auswählen\n"
            "• Auf 'Projekt laden' klicken\n"
            "• Bei Bedarf über 'Projekt umbenennen' den Projektnamen anpassen\n"
            "Die Navigation links zeigt Projektübersicht, Etagen und Räume.",
        )

    def set_projects(self, entries: list[dict]) -> None:
        self.project_list.clear()
        for e in entries:
            item = QListWidgetItem(f"{e['name']}\n{e['path']}")
            item.setData(Qt.UserRole, e["path"])
            self.project_list.addItem(item)

    def _selected_path(self) -> str | None:
        current = self.project_list.currentItem()
        if not current:
            return None
        path = current.data(Qt.UserRole)
        return path if isinstance(path, str) and path else None

    def _emit_open(self) -> None:
        path = self._selected_path()
        if path:
            self.load_requested.emit(path)

    def _emit_rename(self) -> None:
        path = self._selected_path()
        if path:
            self.rename_requested.emit(path)
