from __future__ import annotations

from dataclasses import dataclass
import base64
import json
from pathlib import Path
from typing import Dict, List
import re

from PySide6.QtCore import QMimeData, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QDrag, QDragEnterEvent, QDropEvent, QFont, QFontMetrics, QPen, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import OUTDOOR_AREA_NAME
from app.models.project import Project, floor_scopes


@dataclass
class PlacementToken:
    token_id: str
    room_name: str
    item_type: str
    label: str
    marker_kind: str


class FloorPlanListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SingleSelection)

    def startDrag(self, supportedActions):
        current = self.currentItem()
        if current is None:
            return
        payload = current.data(Qt.UserRole)
        if not isinstance(payload, str):
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(payload)
        drag.setMimeData(mime)
        drag.exec(supportedActions)




def _marker_symbol(marker_kind: str) -> str:
    symbols = {
        "lan": "LAN",
        "ap": "AP",
        "sensor": "S",
        "light": "💡",
        "outdoor_light": "☀",
    }
    return symbols.get(marker_kind, "•")


def _marker_label_prefix(marker_kind: str) -> str:
    prefixes = {
        "lan": "🔌",
        "ap": "📶",
        "sensor": "🧪",
        "light": "💡",
        "outdoor_light": "☀️",
    }
    return prefixes.get(marker_kind, "•")

def _marker_color(marker_kind: str) -> QColor:
    palette = {
        "lan": QColor("#2563eb"),
        "ap": QColor("#16a34a"),
        "sensor": QColor("#d97706"),
        "light": QColor("#ca8a04"),
        "outdoor_light": QColor("#9333ea"),
    }
    return palette.get(marker_kind, QColor("#475569"))


class MarkerItem(QGraphicsEllipseItem):
    def __init__(self, label: str, token_id: str, room_name: str, item_type: str, marker_kind: str):
        super().__init__(-14, -14, 28, 28)
        self.token_id = token_id
        self.room_name = room_name
        self.item_type = item_type
        self.marker_kind = marker_kind

        color = _marker_color(marker_kind)
        self.setBrush(QBrush(color))
        self.setPen(QPen(QColor("#f8fafc"), 2.0))
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsScenePositionChanges, True)

        symbol = _marker_symbol(marker_kind)
        self.symbol_text = QGraphicsSimpleTextItem(symbol, self)
        symbol_font = QFont(self.symbol_text.font())
        symbol_font.setBold(True)
        symbol_font.setPointSize(9)
        self.symbol_text.setFont(symbol_font)
        self.symbol_text.setBrush(QBrush(QColor("#f8fafc")))
        symbol_metrics = QFontMetrics(symbol_font)
        symbol_width = symbol_metrics.horizontalAdvance(symbol)
        symbol_height = symbol_metrics.height()
        self.symbol_text.setPos(-symbol_width / 2, -symbol_height / 2 + 1)

        self.label_bg = QGraphicsRectItem(self)
        self.label_bg.setBrush(QBrush(QColor(15, 23, 42, 228)))
        self.label_bg.setPen(QPen(QColor(148, 163, 184, 210), 1.0))

        self.text = QGraphicsSimpleTextItem(label, self)
        self.text.setBrush(QBrush(QColor("#f8fafc")))

        metrics = QFontMetrics(self.text.font())
        text_width = metrics.horizontalAdvance(label)
        text_height = metrics.height()
        padding_x = 8
        padding_y = 4

        self.label_bg.setRect(22, -12, text_width + padding_x * 2, text_height + padding_y * 2)
        self.text.setPos(22 + padding_x, -12 + padding_y)


class FloorPlanCanvas(QGraphicsView):
    marker_changed = Signal()
    token_dropped = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setRenderHints(self.renderHints())
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item: QGraphicsPixmapItem | None = None
        self.marker_items: Dict[str, MarkerItem] = {}

    def set_image(self, pixmap: QPixmap | None) -> None:
        self.scene.clear()
        self.marker_items.clear()
        if pixmap and not pixmap.isNull():
            self.image_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.image_item)
            self.scene.setSceneRect(self.image_item.boundingRect())
        else:
            self.image_item = None
            self.scene.setSceneRect(0, 0, 900, 600)

    def add_marker(self, token: dict, x: float, y: float) -> None:
        if self.image_item is None:
            return
        marker = MarkerItem(
            token["label"],
            token["token_id"],
            token["room_name"],
            token["item_type"],
            token.get("marker_kind", "sensor"),
        )
        marker.setPos(x, y)
        self.scene.addItem(marker)
        self.marker_items[token["token_id"]] = marker

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if self.image_item is None:
            return
        payload = event.mimeData().text()
        try:
            token = json.loads(payload)
        except json.JSONDecodeError:
            return
        required_keys = {"token_id", "room_name", "item_type", "label", "marker_kind"}
        if not isinstance(token, dict) or not required_keys.issubset(token.keys()):
            return
        scene_pos = self.mapToScene(event.position().toPoint())
        self.token_dropped.emit(
            {
                "token_id": str(token["token_id"]),
                "room_name": str(token["room_name"]),
                "item_type": str(token["item_type"]),
                "label": str(token["label"]),
                "marker_kind": str(token["marker_kind"]),
                "x": float(scene_pos.x()),
                "y": float(scene_pos.y()),
            }
        )
        event.acceptProposedAction()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.marker_changed.emit()


class FloorPlanPage(QWidget):
    changed = Signal()

    def __init__(self, project: Project):
        super().__init__()
        self.project = project
        scopes = floor_scopes(project)
        self.current_floor = scopes[0] if scopes else OUTDOOR_AREA_NAME
        self.tokens_by_floor: Dict[str, List[PlacementToken]] = {}

        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Grundriss-Planung</h2>"))
        hint = QLabel(
            "Lade pro Bereich einen Grundriss und ziehe LAN-Dosen, Access Points, Sensoren oder Lichtpunkte aus der Liste auf das Bild."
        )
        hint.setStyleSheet("color:#94a3b8;")
        root.addWidget(hint)

        legend = QLabel("Legende: 🔌 LAN · 📶 AP · 🧪 Sensor · 💡 Innenlicht · ☀️ Außenlicht")
        legend.setStyleSheet("color:#cbd5e1;")
        root.addWidget(legend)

        top_row = QHBoxLayout()
        self.floor_buttons: Dict[str, QPushButton] = {}
        for floor in floor_scopes(project):
            button = QPushButton(floor)
            button.clicked.connect(lambda _=False, name=floor: self._select_floor(name))
            self.floor_buttons[floor] = button
            top_row.addWidget(button)
        top_row.addStretch()
        self.btn_upload = QPushButton("Grundrissbild laden")
        self.btn_upload.clicked.connect(self._upload_image)
        self.btn_remove = QPushButton("Bild entfernen")
        self.btn_remove.clicked.connect(self._remove_image)
        self.btn_delete_marker = QPushButton("Marker entfernen")
        self.btn_delete_marker.clicked.connect(self._delete_selected_markers)
        top_row.addWidget(self.btn_upload)
        top_row.addWidget(self.btn_remove)
        top_row.addWidget(self.btn_delete_marker)
        root.addLayout(top_row)

        self.summary_label = QLabel()
        root.addWidget(self.summary_label)

        content = QHBoxLayout()
        self.todo_list = FloorPlanListWidget()
        self.todo_list.setMinimumWidth(300)
        self.todo_list.setMaximumWidth(420)
        self.canvas = FloorPlanCanvas()
        self.canvas.token_dropped.connect(self._place_token)
        self.canvas.marker_changed.connect(self._emit_changed)

        content.addWidget(self.todo_list)
        content.addWidget(self.canvas, 1)
        root.addLayout(content, 1)

        self._ensure_storage()
        self._refresh_tokens()
        self._select_floor(self.current_floor)

    def _ensure_storage(self) -> None:
        if not hasattr(self.project, "floor_plans") or not isinstance(getattr(self.project, "floor_plans"), dict):
            self.project.floor_plans = {}

    def _refresh_tokens(self) -> None:
        self.tokens_by_floor = {}
        for room in self.project.rooms.values():
            socket_selections = room.topics.get("room_lan_socket_count").selections if room.topics.get("room_lan_socket_count") else []
            ap_selections = room.topics.get("room_access_point").selections if room.topics.get("room_access_point") else []
            sockets = _parse_amount(socket_selections)
            aps = _parse_amount(ap_selections)
            floor_tokens = self.tokens_by_floor.setdefault(room.floor, [])

            for idx in range(1, sockets + 1):
                floor_tokens.append(
                    PlacementToken(
                        token_id=f"{room.name}|lan|{idx}",
                        room_name=room.name,
                        item_type="LAN-Dose",
                        label=f"{room.name} LAN {idx}",
                        marker_kind="lan",
                    )
                )
            for idx in range(1, aps + 1):
                floor_tokens.append(
                    PlacementToken(
                        token_id=f"{room.name}|ap|{idx}",
                        room_name=room.name,
                        item_type="Access Point",
                        label=f"{room.name} AP {idx}",
                        marker_kind="ap",
                    )
                )

            ceiling_topic = room.topics.get("room_ceiling_light_count")
            spot_topic = room.topics.get("room_spotlight_count")
            ceiling_lights = _parse_amount(ceiling_topic.selections if ceiling_topic else [])
            spot_lights = _parse_amount(spot_topic.selections if spot_topic else [])

            for idx in range(1, ceiling_lights + 1):
                floor_tokens.append(
                    PlacementToken(
                        token_id=f"{room.name}|light_ceiling|{idx}",
                        room_name=room.name,
                        item_type="Deckenlicht",
                        label=f"{room.name} Deckenlicht {idx}",
                        marker_kind="light",
                    )
                )
            for idx in range(1, spot_lights + 1):
                floor_tokens.append(
                    PlacementToken(
                        token_id=f"{room.name}|light_spot|{idx}",
                        room_name=room.name,
                        item_type="Spot",
                        label=f"{room.name} Spot {idx}",
                        marker_kind="light",
                    )
                )

            sensor_index = 1
            sensor_selections = []
            for sensor_key in ["room_sensor_general", "room_climate_sensors"]:
                topic = room.topics.get(sensor_key)
                if topic:
                    sensor_selections.extend(topic.selections)

            sensor_quantities: Dict[str, int] = {}
            for sensor_key in ["room_sensor_general", "room_climate_sensors"]:
                topic = room.topics.get(sensor_key)
                if topic and isinstance(topic.quantities, dict):
                    for sensor_name, quantity in topic.quantities.items():
                        try:
                            sensor_quantities[sensor_name] = max(sensor_quantities.get(sensor_name, 0), int(quantity))
                        except (TypeError, ValueError):
                            sensor_quantities[sensor_name] = max(sensor_quantities.get(sensor_name, 0), 1)

            for sensor_name in sensor_selections:
                count = max(1, sensor_quantities.get(sensor_name, 1))
                for local_index in range(1, count + 1):
                    floor_tokens.append(
                        PlacementToken(
                            token_id=f"{room.name}|sensor|{_slug(sensor_name)}|{sensor_index}",
                            room_name=room.name,
                            item_type=f"Sensor: {sensor_name}",
                            label=f"{room.name} {sensor_name} {local_index}",
                            marker_kind="sensor",
                        )
                    )
                    sensor_index += 1

        outdoor_tokens = self.tokens_by_floor.setdefault(OUTDOOR_AREA_NAME, [])
        outdoor_light_topic = self.project.outdoor_topics.get("outdoor_light_count")
        outdoor_lights = _parse_amount(outdoor_light_topic.selections if outdoor_light_topic else [])
        for idx in range(1, outdoor_lights + 1):
            outdoor_tokens.append(
                PlacementToken(
                    token_id=f"außen|light|{idx}",
                    room_name=OUTDOOR_AREA_NAME,
                    item_type="Außenlicht",
                    label=f"Außenlicht {idx}",
                    marker_kind="outdoor_light",
                )
            )

    def _select_floor(self, floor: str) -> None:
        self.current_floor = floor
        for name, button in self.floor_buttons.items():
            button.setEnabled(name != floor)
        self._reload_floor_view()

    def refresh(self) -> None:
        scopes = floor_scopes(self.project)
        if self.current_floor not in scopes:
            self.current_floor = scopes[0] if scopes else OUTDOOR_AREA_NAME
        self._reload_floor_view()

    def _reload_floor_view(self) -> None:
        self._refresh_tokens()
        self.todo_list.clear()
        floor_data = self.project.floor_plans.setdefault(self.current_floor, {"image_path": "", "placements": []})
        placements = floor_data.get("placements", [])
        valid_ids = {token.token_id for token in self.tokens_by_floor.get(self.current_floor, [])}
        placements = [p for p in placements if p.get("token_id") in valid_ids]
        floor_data["placements"] = placements
        placed_ids = {p.get("token_id") for p in placements}

        pending = [token for token in self.tokens_by_floor.get(self.current_floor, []) if token.token_id not in placed_ids]
        for token in pending:
            item = QListWidgetItem(f"{_marker_label_prefix(token.marker_kind)} {token.label} ({token.item_type})")
            item.setData(
                Qt.UserRole,
                json.dumps(
                    {
                        "token_id": token.token_id,
                        "room_name": token.room_name,
                        "item_type": token.item_type,
                        "label": token.label,
                        "marker_kind": token.marker_kind,
                    },
                    ensure_ascii=False,
                ),
            )
            self.todo_list.addItem(item)

        room_summaries: Dict[str, Dict[str, int]] = {}
        for token in self.tokens_by_floor.get(self.current_floor, []):
            row = room_summaries.setdefault(token.room_name, {"LAN-Dose": 0, "Access Point": 0, "Sensor": 0, "Licht": 0})
            if token.marker_kind == "lan":
                row["LAN-Dose"] += 1
            elif token.marker_kind == "ap":
                row["Access Point"] += 1
            elif token.marker_kind == "sensor":
                row["Sensor"] += 1
            elif token.marker_kind in {"light", "outdoor_light"}:
                row["Licht"] += 1

        summary_parts = [
            f"{room}: {counts['LAN-Dose']} LAN-Dosen, {counts['Access Point']} AP, {counts['Sensor']} Sensoren, {counts['Licht']} Lichter"
            for room, counts in room_summaries.items()
        ]
        self.summary_label.setText(
            " • ".join(summary_parts) if summary_parts else "Keine platzierbaren Objekte auf diesem Bereich."
        )

        self._load_floor_image_and_markers()

    def _load_floor_image_and_markers(self) -> None:
        floor_data = self.project.floor_plans.setdefault(self.current_floor, {"image_path": "", "placements": []})
        image_path = floor_data.get("image_path", "")
        pixmap = QPixmap(image_path) if image_path else QPixmap()

        if pixmap.isNull() and floor_data.get("image_data"):
            try:
                image_bytes = base64.b64decode(str(floor_data.get("image_data")), validate=True)
                pixmap.loadFromData(image_bytes)
            except (ValueError, TypeError):
                pass

        if image_path and pixmap.isNull() and not floor_data.get("image_data"):
            QMessageBox.warning(self, "Grundriss", f"Bild konnte nicht geladen werden:\n{image_path}")
        self.canvas.set_image(pixmap if not pixmap.isNull() else None)

        if self.canvas.image_item is None:
            return
        width = self.canvas.image_item.pixmap().width() or 1
        height = self.canvas.image_item.pixmap().height() or 1

        for placement in floor_data.get("placements", []):
            self.canvas.add_marker(
                {
                    "token_id": placement.get("token_id", ""),
                    "room_name": placement.get("room_name", ""),
                    "item_type": placement.get("item_type", ""),
                    "label": placement.get("label", ""),
                    "marker_kind": placement.get("marker_kind", "sensor"),
                },
                float(placement.get("x", 0.0)) * width,
                float(placement.get("y", 0.0)) * height,
            )

    def _place_token(self, placement: dict) -> None:
        if self.canvas.image_item is None:
            return
        floor_data = self.project.floor_plans.setdefault(self.current_floor, {"image_path": "", "placements": []})
        placements = [p for p in floor_data.get("placements", []) if p.get("token_id") != placement["token_id"]]

        width = self.canvas.image_item.pixmap().width() or 1
        height = self.canvas.image_item.pixmap().height() or 1

        bounded_x = max(0.0, min(placement["x"], float(width)))
        bounded_y = max(0.0, min(placement["y"], float(height)))
        placement["x"] = bounded_x / width
        placement["y"] = bounded_y / height
        placements.append(placement)

        floor_data["placements"] = placements
        self._reload_floor_view()
        self.changed.emit()

    def _delete_selected_markers(self) -> None:
        if self.canvas.image_item is None:
            return

        selected = [item for item in self.canvas.scene.selectedItems() if isinstance(item, MarkerItem)]
        if not selected:
            return

        for marker in selected:
            self.canvas.scene.removeItem(marker)
            self.canvas.marker_items.pop(marker.token_id, None)

        self._emit_changed()
        self._reload_floor_view()

    def _upload_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Grundrissbild wählen",
            str(Path.cwd()),
            "Bilder (*.png *.jpg *.jpeg *.bmp *.webp)",
        )
        if not file_path:
            return
        floor_data = self.project.floor_plans.setdefault(self.current_floor, {"image_path": "", "placements": []})
        floor_data["image_path"] = file_path
        floor_data.setdefault("placements", [])
        try:
            floor_data["image_data"] = base64.b64encode(Path(file_path).read_bytes()).decode("ascii")
        except OSError:
            floor_data["image_data"] = ""
        self._reload_floor_view()
        self.changed.emit()

    def _remove_image(self) -> None:
        floor_data = self.project.floor_plans.setdefault(self.current_floor, {"image_path": "", "placements": []})
        floor_data["image_path"] = ""
        floor_data["image_data"] = ""
        floor_data["placements"] = []
        self._reload_floor_view()
        self.changed.emit()

    def _emit_changed(self) -> None:
        if self.canvas.image_item is None:
            return
        width = self.canvas.image_item.pixmap().width() or 1
        height = self.canvas.image_item.pixmap().height() or 1
        floor_data = self.project.floor_plans.setdefault(self.current_floor, {"image_path": "", "placements": []})
        placements: List[dict] = []
        for marker in self.canvas.marker_items.values():
            pos = marker.pos()
            placements.append(
                {
                    "token_id": marker.token_id,
                    "room_name": marker.room_name,
                    "item_type": marker.item_type,
                    "label": marker.text.text(),
                    "marker_kind": marker.marker_kind,
                    "x": max(0.0, min(pos.x(), float(width))) / width,
                    "y": max(0.0, min(pos.y(), float(height))) / height,
                }
            )
        floor_data["placements"] = placements
        self.changed.emit()

    def persist(self) -> None:
        self._emit_changed()


def _parse_amount(selections: List[str]) -> int:
    if not selections:
        return 0

    best = 0
    for selection in selections:
        match = re.search(r"(\d+)", selection)
        if match:
            best = max(best, int(match.group(1)))
    return best


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")
