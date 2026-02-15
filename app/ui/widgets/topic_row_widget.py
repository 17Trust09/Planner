from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Signal
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import OPTION_SETS, TopicDefinition
from app.models.project import TopicState

SENSOR_TOPIC_KEYS = {"room_sensor_general", "room_climate_sensors"}


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event: QWheelEvent) -> None:
        # Verhindert unbeabsichtigte Änderungen per Mausrad beim Hovern.
        event.ignore()


class TopicRowWidget(QWidget):
    changed = Signal()

    def __init__(self, definition: TopicDefinition, state: TopicState):
        super().__init__()
        self.definition = definition
        self.state = state
        self.combos: List[QComboBox] = []
        self._all_options = OPTION_SETS[self.definition.option_set]
        self.is_sensor_topic = self.definition.key in SENSOR_TOPIC_KEYS
        self.quantity_inputs: Dict[str, QLineEdit] = {}

        self.setObjectName("topicCard")

        main = QVBoxLayout(self)
        main.setSpacing(8)
        main.setContentsMargins(10, 8, 10, 8)

        head = QHBoxLayout()
        title = QLabel(f"<b>{definition.title}</b>")
        self.help_btn = QPushButton("?")
        self.help_btn.setObjectName("helpButton")
        self.help_btn.setFixedWidth(28)
        self.help_btn.clicked.connect(self._show_help)
        head.addWidget(title)
        head.addStretch()
        head.addWidget(self.help_btn)
        main.addLayout(head)

        desc = QLabel(definition.description)
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#94a3b8;")
        main.addWidget(desc)

        top = QGridLayout()
        top.setHorizontalSpacing(8)
        self.combo_container = QHBoxLayout()
        self.combo_container.setSpacing(8)
        self.add_btn = QPushButton("+ Auswahl")
        self.remove_btn = QPushButton("- Auswahl")
        self.add_btn.clicked.connect(self.add_combo)
        self.remove_btn.clicked.connect(self.remove_combo)
        controls = QHBoxLayout()
        controls.setSpacing(6)
        controls.addWidget(self.add_btn)
        controls.addWidget(self.remove_btn)

        top.addLayout(self.combo_container, 0, 0)
        top.addLayout(controls, 0, 1)
        main.addLayout(top)

        self.quantity_container = QWidget()
        self.quantity_layout = QGridLayout(self.quantity_container)
        self.quantity_layout.setContentsMargins(0, 0, 0, 0)
        self.quantity_layout.setHorizontalSpacing(8)
        self.quantity_layout.setVerticalSpacing(6)
        self.quantity_container.setVisible(self.is_sensor_topic)
        main.addWidget(self.quantity_container)

        self.assignee = QLineEdit()
        self.assignee.setPlaceholderText("Verantwortlich (z. B. Elektriker)")
        self.assignee.setText(state.assignee)
        self.assignee.textChanged.connect(self._emit)
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notizen")
        self.notes.setFixedHeight(64)
        self.notes.setPlainText(state.notes)
        self.notes.textChanged.connect(self._emit)
        main.addWidget(self.assignee)
        main.addWidget(self.notes)

        initial = max(1, len(state.selections))
        for _ in range(initial):
            self.add_combo(emit=False)
        for i, val in enumerate(state.selections):
            if i < len(self.combos):
                self.combos[i].setCurrentText(val)

        self._refresh_all_combo_options()
        self._sync_quantity_inputs(emit=False)
        self._update_buttons()

    def _selected_values(self) -> list[str]:
        vals: list[str] = []
        for combo in self.combos:
            value = combo.currentText().strip()
            if value and value not in vals:
                vals.append(value)
        return vals

    def _refresh_combo_options(self, combo: QComboBox) -> None:
        current = combo.currentText().strip()
        used_elsewhere = {c.currentText().strip() for c in self.combos if c is not combo and c.currentText().strip()}

        available = [opt for opt in self._all_options if opt not in used_elsewhere or opt == current]

        combo.blockSignals(True)
        combo.clear()
        combo.addItem("")
        combo.addItems(available)
        if current and current in available:
            combo.setCurrentText(current)
        combo.blockSignals(False)

    def _refresh_all_combo_options(self) -> None:
        for combo in self.combos:
            self._refresh_combo_options(combo)

    def _has_free_option(self) -> bool:
        return len(self._selected_values()) < len(self._all_options)

    def add_combo(self, emit: bool = True) -> None:
        # Startet mit einem Feld und lässt zusätzliche Felder zu,
        # solange noch ungenutzte Optionen vorhanden sind.
        if not self._has_free_option() and self.combos:
            return

        combo = NoWheelComboBox()
        combo.currentTextChanged.connect(lambda _: self._combo_changed(combo))
        self.combos.append(combo)
        self.combo_container.addWidget(combo)

        self._refresh_all_combo_options()
        self._sync_quantity_inputs(emit=False)
        self._update_buttons()
        if emit:
            self._emit()

    def remove_combo(self) -> None:
        if len(self.combos) <= 1:
            return
        combo = self.combos.pop()
        combo.setParent(None)
        self._refresh_all_combo_options()
        self._sync_quantity_inputs(emit=False)
        self._update_buttons()
        self._emit()

    def _combo_changed(self, current: QComboBox) -> None:
        text = current.currentText().strip()
        if text:
            for combo in self.combos:
                if combo is not current and combo.currentText().strip() == text:
                    current.blockSignals(True)
                    current.setCurrentIndex(0)
                    current.blockSignals(False)
                    break

        self._refresh_all_combo_options()
        self._sync_quantity_inputs(emit=False)
        self._update_buttons()
        self._emit()

    def _sync_quantity_inputs(self, emit: bool = True) -> None:
        if not self.is_sensor_topic:
            return

        selections = self._selected_values()
        existing_values = {
            key: _safe_int(input_widget.text()) for key, input_widget in self.quantity_inputs.items()
        }

        while self.quantity_layout.count():
            item = self.quantity_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.quantity_inputs.clear()

        if not selections:
            hint = QLabel("Wähle Sensoren aus, dann kannst du die Anzahl je Sensor eingeben.")
            hint.setStyleSheet("color:#94a3b8;")
            self.quantity_layout.addWidget(hint, 0, 0, 1, 2)
            return

        for row_index, selection in enumerate(selections):
            label = QLabel(f"Anzahl {selection}")
            edit = QLineEdit()
            edit.setPlaceholderText("z. B. 1")
            value = self.state.quantities.get(selection, existing_values.get(selection, 1))
            edit.setText(str(max(1, value)))
            edit.textChanged.connect(self._emit)

            self.quantity_layout.addWidget(label, row_index, 0)
            self.quantity_layout.addWidget(edit, row_index, 1)
            self.quantity_inputs[selection] = edit

        if emit:
            self._emit()

    def _quantity_map(self) -> Dict[str, int]:
        if not self.is_sensor_topic:
            return {}
        quantities: Dict[str, int] = {}
        for selection in self._selected_values():
            edit = self.quantity_inputs.get(selection)
            value = _safe_int(edit.text()) if edit else 1
            quantities[selection] = max(1, value)
        return quantities

    def _update_buttons(self) -> None:
        self.add_btn.setEnabled(self._has_free_option())
        self.remove_btn.setEnabled(len(self.combos) > 1)

    def set_missing(self, is_missing: bool) -> None:
        self.setProperty("missing", "true" if is_missing else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def get_state(self) -> TopicState:
        selections = self._selected_values()
        return TopicState(
            selections=selections,
            notes=self.notes.toPlainText().strip(),
            assignee=self.assignee.text().strip(),
            quantities=self._quantity_map(),
        )

    def _show_help(self) -> None:
        option_lines = []
        for option in OPTION_SETS[self.definition.option_set]:
            option_lines.append(f"• {option}: Diese Auswahl bedeutet, dass dieses Kriterium aktiv eingeplant wird.")

        message = (
            f"Thema: {self.definition.title}\n\n"
            f"Worum geht es?\n{self.definition.description}\n\n"
            "Was bedeuten die Auswahlmöglichkeiten?\n"
            + "\n".join(option_lines)
        )
        QMessageBox.information(self, f"Hilfe: {self.definition.title}", message)

    def _emit(self) -> None:
        self.changed.emit()


def _safe_int(value: str) -> int:
    try:
        return int((value or "").strip())
    except ValueError:
        return 1
