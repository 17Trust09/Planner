from __future__ import annotations

from typing import List

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
        self._update_buttons()

    def add_combo(self, emit: bool = True) -> None:
        if len(self.combos) >= self.definition.max_selections:
            return
        combo = NoWheelComboBox()
        combo.addItem("")
        combo.addItems(OPTION_SETS[self.definition.option_set])
        combo.currentTextChanged.connect(lambda _: self._combo_changed(combo))
        self.combos.append(combo)
        self.combo_container.addWidget(combo)
        self._update_buttons()
        if emit:
            self._emit()

    def remove_combo(self) -> None:
        if len(self.combos) <= 1:
            return
        combo = self.combos.pop()
        combo.setParent(None)
        self._update_buttons()
        self._emit()

    def _combo_changed(self, current: QComboBox) -> None:
        text = current.currentText().strip()
        if not text:
            self._emit()
            return
        for combo in self.combos:
            if combo is not current and combo.currentText().strip() == text:
                current.setCurrentIndex(0)
                break
        self._emit()

    def _update_buttons(self) -> None:
        self.add_btn.setEnabled(len(self.combos) < self.definition.max_selections)
        self.remove_btn.setEnabled(len(self.combos) > 1)

    def get_state(self) -> TopicState:
        selections = []
        for c in self.combos:
            value = c.currentText().strip()
            if value and value not in selections:
                selections.append(value)
        return TopicState(selections=selections, notes=self.notes.toPlainText().strip(), assignee=self.assignee.text().strip())

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
