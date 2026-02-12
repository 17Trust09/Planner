from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)

from app.models.definitions import ROOM_TYPE_OPTIONS


class RoomsPage(QWidget):
    rooms_changed = Signal()

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Räume konfigurieren</h2>"))
        root.addWidget(QLabel("Räume flexibel anlegen/löschen und Raumtyp für dynamische Fragen setzen."))

        self.room_list = QListWidget()
        root.addWidget(self.room_list)

        form = QFormLayout()
        self.type_combo = QComboBox()
        for key, label in ROOM_TYPE_OPTIONS.items():
            self.type_combo.addItem(label, key)
        self.type_combo.currentIndexChanged.connect(self._emit_type_change)
        form.addRow("Raumtyp", self.type_combo)
        root.addLayout(form)

        btns = QHBoxLayout()
        self.btn_add = QPushButton("Raum hinzufügen")
        self.btn_delete = QPushButton("Raum löschen")
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_delete)
        root.addLayout(btns)

        self.btn_add.clicked.connect(self._request_add)
        self.btn_delete.clicked.connect(self._request_delete)
        self.room_list.currentRowChanged.connect(self._sync_selected_type)

        self._rooms: dict[str, dict] = {}
        self._syncing = False

    def set_rooms(self, rooms: dict[str, dict]) -> None:
        self._syncing = True
        self._rooms = rooms
        self.room_list.clear()
        for room_name, info in sorted(self._rooms.items(), key=lambda x: (x[1]["floor"], x[0])):
            room_type = ROOM_TYPE_OPTIONS.get(info.get("room_type", "other"), "Sonstiges")
            self.room_list.addItem(f"{info['floor']} | {room_name} ({room_type})")
        if self.room_list.count() > 0:
            self.room_list.setCurrentRow(0)
        self._syncing = False

    def _current_room_name(self) -> str | None:
        current = self.room_list.currentItem()
        if not current:
            return None
        text = current.text().split(" | ", 1)[1]
        return text.split(" (", 1)[0]

    def _sync_selected_type(self) -> None:
        if self._syncing:
            return
        room_name = self._current_room_name()
        if not room_name:
            return
        room_type = self._rooms[room_name].get("room_type", "other")
        idx = self.type_combo.findData(room_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)

    def _emit_type_change(self) -> None:
        if self._syncing:
            return
        room_name = self._current_room_name()
        if not room_name:
            return
        self._rooms[room_name]["room_type"] = self.type_combo.currentData()
        self.set_rooms(self._rooms)
        self.rooms_changed.emit()

    def _request_add(self) -> None:
        room_name, ok = QInputDialog.getText(self, "Raum hinzufügen", "Raumname:")
        if not ok or not room_name.strip():
            return
        room_name = room_name.strip()
        if room_name in self._rooms:
            QMessageBox.warning(self, "Raum vorhanden", "Der Raum existiert bereits.")
            return
        floor, ok_floor = QInputDialog.getText(self, "Stockwerk", "Stockwerk (z. B. EG, OG, UG):", text="EG")
        if not ok_floor or not floor.strip():
            return
        self._rooms[room_name] = {"floor": floor.strip(), "room_type": "other"}
        self.set_rooms(self._rooms)
        self.rooms_changed.emit()

    def _request_delete(self) -> None:
        if self._syncing:
            return
        room_name = self._current_room_name()
        if not room_name:
            return
        if QMessageBox.question(self, "Raum löschen", f"Raum '{room_name}' wirklich löschen?") != QMessageBox.Yes:
            return
        del self._rooms[room_name]
        self.set_rooms(self._rooms)
        self.rooms_changed.emit()

    def get_rooms(self) -> dict[str, dict]:
        return self._rooms
