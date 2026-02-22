from __future__ import annotations

from typing import Dict, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import OUTDOOR_AREA_NAME, ROOM_TOPICS
from app.models.project import Project, RoomData, StructureArea, StructureSubarea, TopicState


class HouseStructurePage(QWidget):
    changed = Signal()
    structure_changed = Signal()

    def __init__(self, project: Project):
        super().__init__()
        self.project = project

        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Hausstruktur</h2>"))
        hint = QLabel("Bereiche, Unterbereiche und Räume verwalten. Raum-Optionen bleiben für alle Räume identisch.")
        hint.setStyleSheet("color:#94a3b8;")
        root.addWidget(hint)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        root.addWidget(self.tree, 1)

        actions = QHBoxLayout()
        self.btn_add_area = QPushButton("Bereich +")
        self.btn_add_subarea = QPushButton("Unterbereich +")
        self.btn_add_room = QPushButton("Raum +")
        self.btn_rename = QPushButton("Umbenennen")
        self.btn_delete = QPushButton("Löschen")

        for button in [self.btn_add_area, self.btn_add_subarea, self.btn_add_room, self.btn_rename, self.btn_delete]:
            actions.addWidget(button)
        actions.addStretch()
        root.addLayout(actions)

        self.btn_add_area.clicked.connect(self._add_area)
        self.btn_add_subarea.clicked.connect(self._add_subarea)
        self.btn_add_room.clicked.connect(self._add_room)
        self.btn_rename.clicked.connect(self._rename_selected)
        self.btn_delete.clicked.connect(self._delete_selected)

        self.refresh()

    def refresh(self) -> None:
        self.tree.clear()
        for area in self.project.house_areas:
            area_item = QTreeWidgetItem([area.name])
            area_item.setData(0, Qt.UserRole, ("area", area.name))
            self.tree.addTopLevelItem(area_item)
            for sub in area.subareas:
                sub_item = QTreeWidgetItem([sub.name])
                sub_item.setData(0, Qt.UserRole, ("subarea", area.name, sub.name))
                area_item.addChild(sub_item)
                for room_id in sub.rooms:
                    room = self.project.rooms.get(room_id)
                    if room is None:
                        continue
                    room_item = QTreeWidgetItem([room.name])
                    room_item.setData(0, Qt.UserRole, ("room", area.name, sub.name, room_id))
                    sub_item.addChild(room_item)
        self.tree.expandAll()

    def persist(self) -> None:
        return

    def _selected_payload(self) -> Tuple[str, ...] | None:
        current = self.tree.currentItem()
        if current is None:
            return None
        payload = current.data(0, Qt.UserRole)
        if isinstance(payload, tuple):
            return payload
        return None

    def _add_area(self) -> None:
        name, ok = QInputDialog.getText(self, "Bereich hinzufügen", "Bereichsname:")
        if not ok:
            return
        area_name = (name or "").strip()
        if not area_name:
            return
        if any(a.name == area_name for a in self.project.house_areas):
            QMessageBox.warning(self, "Bereich", "Ein Bereich mit diesem Namen existiert bereits.")
            return
        self.project.house_areas.append(StructureArea(name=area_name))
        self._emit_structure_changed()

    def _add_subarea(self) -> None:
        payload = self._selected_payload()
        area_name = None
        if payload and payload[0] in {"area", "subarea", "room"}:
            area_name = payload[1]
        if not area_name:
            QMessageBox.information(self, "Unterbereich", "Bitte zuerst einen Bereich auswählen.")
            return
        if area_name == OUTDOOR_AREA_NAME:
            QMessageBox.information(self, "Unterbereich", "Für den Außenbereich sind keine Unterbereiche nötig.")
            return

        area = self._find_area(area_name)
        if area is None:
            return

        sub_name, ok = QInputDialog.getText(self, "Unterbereich hinzufügen", "Unterbereichsname:")
        if not ok:
            return
        sub_name = (sub_name or "").strip()
        if not sub_name:
            return
        if any(sub.name == sub_name for a in self.project.house_areas for sub in a.subareas):
            QMessageBox.warning(self, "Unterbereich", "Der Unterbereichsname muss eindeutig sein.")
            return
        area.subareas.append(StructureSubarea(name=sub_name))
        self._emit_structure_changed()

    def _add_room(self) -> None:
        payload = self._selected_payload()
        if not payload:
            QMessageBox.information(self, "Raum", "Bitte zuerst einen Unterbereich auswählen.")
            return

        if payload[0] == "room":
            area_name, sub_name = payload[1], payload[2]
        elif payload[0] == "subarea":
            area_name, sub_name = payload[1], payload[2]
        else:
            QMessageBox.information(self, "Raum", "Bitte zuerst einen Unterbereich auswählen.")
            return

        room_name, ok = QInputDialog.getText(self, "Raum hinzufügen", "Raumname:")
        if not ok:
            return
        room_name = (room_name or "").strip()
        if not room_name:
            return
        if room_name in self.project.rooms:
            QMessageBox.warning(self, "Raum", "Ein Raum mit diesem Namen existiert bereits.")
            return

        area = self._find_area(area_name)
        if area is None:
            return
        sub = self._find_subarea(area, sub_name)
        if sub is None:
            return

        self.project.rooms[room_name] = RoomData(
            name=room_name,
            floor=sub_name,
            area=area_name,
            topics={topic.key: TopicState() for topic in ROOM_TOPICS},
        )
        sub.rooms.append(room_name)
        self._emit_structure_changed()

    def _rename_selected(self) -> None:
        payload = self._selected_payload()
        if not payload:
            return

        kind = payload[0]
        if kind == "area":
            old_name = payload[1]
            new_name, ok = QInputDialog.getText(self, "Bereich umbenennen", "Neuer Name:", text=old_name)
            if not ok:
                return
            new_name = (new_name or "").strip()
            if not new_name or new_name == old_name:
                return
            if any(a.name == new_name for a in self.project.house_areas):
                QMessageBox.warning(self, "Bereich", "Ein Bereich mit diesem Namen existiert bereits.")
                return
            area = self._find_area(old_name)
            if area is None:
                return
            area.name = new_name
            for room in self.project.rooms.values():
                if room.area == old_name:
                    room.area = new_name
            self._emit_structure_changed()
            return

        if kind == "subarea":
            area_name, old_name = payload[1], payload[2]
            new_name, ok = QInputDialog.getText(self, "Unterbereich umbenennen", "Neuer Name:", text=old_name)
            if not ok:
                return
            new_name = (new_name or "").strip()
            if not new_name or new_name == old_name:
                return
            if any(sub.name == new_name for a in self.project.house_areas for sub in a.subareas):
                QMessageBox.warning(self, "Unterbereich", "Der Unterbereichsname muss eindeutig sein.")
                return
            area = self._find_area(area_name)
            sub = self._find_subarea(area, old_name) if area else None
            if sub is None:
                return
            sub.name = new_name
            for room_id in sub.rooms:
                if room_id in self.project.rooms:
                    self.project.rooms[room_id].floor = new_name
            if old_name in self.project.floor_plans and new_name not in self.project.floor_plans:
                self.project.floor_plans[new_name] = self.project.floor_plans.pop(old_name)
            self._emit_structure_changed()
            return

        if kind == "room":
            room_id = payload[3]
            room = self.project.rooms.get(room_id)
            if room is None:
                return
            new_name, ok = QInputDialog.getText(self, "Raum umbenennen", "Neuer Name:", text=room.name)
            if not ok:
                return
            new_name = (new_name or "").strip()
            if not new_name or new_name == room_id:
                return
            if new_name in self.project.rooms:
                QMessageBox.warning(self, "Raum", "Ein Raum mit diesem Namen existiert bereits.")
                return

            self.project.rooms[new_name] = self.project.rooms.pop(room_id)
            self.project.rooms[new_name].name = new_name
            for area in self.project.house_areas:
                for sub in area.subareas:
                    sub.rooms = [new_name if rid == room_id else rid for rid in sub.rooms]

            for scope_data in self.project.floor_plans.values():
                placements = scope_data.get("placements", [])
                for placement in placements:
                    if placement.get("room_name") == room_id:
                        placement["room_name"] = new_name
            self._emit_structure_changed()

    def _delete_selected(self) -> None:
        payload = self._selected_payload()
        if not payload:
            return
        kind = payload[0]

        if kind == "room":
            room_id = payload[3]
            for area in self.project.house_areas:
                for sub in area.subareas:
                    sub.rooms = [rid for rid in sub.rooms if rid != room_id]
            self.project.rooms.pop(room_id, None)
            self._purge_room_placements(room_id)
            self._emit_structure_changed()
            return

        if kind == "subarea":
            area_name, sub_name = payload[1], payload[2]
            area = self._find_area(area_name)
            if area is None:
                return
            sub = self._find_subarea(area, sub_name)
            if sub is None:
                return
            for room_id in list(sub.rooms):
                self.project.rooms.pop(room_id, None)
                self._purge_room_placements(room_id)
            area.subareas = [s for s in area.subareas if s.name != sub_name]
            self.project.floor_plans.pop(sub_name, None)
            self._emit_structure_changed()
            return

        if kind == "area":
            area_name = payload[1]
            if area_name == OUTDOOR_AREA_NAME:
                QMessageBox.information(self, "Bereich", "Der Außenbereich kann nicht gelöscht werden.")
                return
            area = self._find_area(area_name)
            if area is None:
                return
            for sub in area.subareas:
                for room_id in list(sub.rooms):
                    self.project.rooms.pop(room_id, None)
                    self._purge_room_placements(room_id)
                self.project.floor_plans.pop(sub.name, None)
            self.project.house_areas = [a for a in self.project.house_areas if a.name != area_name]
            self._emit_structure_changed()

    def _purge_room_placements(self, room_id: str) -> None:
        for scope_data in self.project.floor_plans.values():
            placements = scope_data.get("placements", [])
            scope_data["placements"] = [p for p in placements if p.get("room_name") != room_id]

    def _find_area(self, area_name: str) -> StructureArea | None:
        return next((a for a in self.project.house_areas if a.name == area_name), None)

    @staticmethod
    def _find_subarea(area: StructureArea | None, sub_name: str) -> StructureSubarea | None:
        if area is None:
            return None
        return next((s for s in area.subareas if s.name == sub_name), None)

    def _emit_structure_changed(self) -> None:
        if not any(area.name == OUTDOOR_AREA_NAME for area in self.project.house_areas):
            self.project.house_areas.insert(0, StructureArea(name=OUTDOOR_AREA_NAME))
        self.refresh()
        self.changed.emit()
        self.structure_changed.emit()
