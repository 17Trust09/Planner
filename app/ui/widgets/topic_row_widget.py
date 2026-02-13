from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import OPTION_SETS, TopicDefinition
from app.models.project import TopicState


class TopicRowWidget(QWidget):
    changed = Signal()

    def __init__(self, definition: TopicDefinition, state: TopicState):
        super().__init__()
        self.definition = definition
        self.state = state
        self.combos: List[QComboBox] = []

        options = OPTION_SETS[self.definition.option_set]
        self.selection_limit = len(options)
        self.info_text = self._build_info_text(options)

        main = QVBoxLayout(self)

        title_row = QHBoxLayout()
        title = QLabel(f"<b>{definition.title}</b>")
        title.setToolTip(self.info_text)
        info = QLabel("ⓘ")
        info.setToolTip(self.info_text)
        info.setCursor(Qt.WhatsThisCursor)
        info.setStyleSheet("color:#1d4ed8; font-weight:700;")
        title_row.addWidget(title)
        title_row.addWidget(info)
        title_row.addStretch()
        main.addLayout(title_row)

        desc = QLabel(definition.description)
        desc.setStyleSheet("color:#334155;")
        desc.setToolTip(self.info_text)
        main.addWidget(desc)

        top = QGridLayout()
        self.combo_container = QHBoxLayout()
        self.add_btn = QPushButton("+ Auswahl")
        self.remove_btn = QPushButton("- Auswahl")
        self.add_btn.clicked.connect(self.add_combo)
        self.remove_btn.clicked.connect(self.remove_combo)
        controls = QHBoxLayout()
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
        self.notes.setPlainText(state.notes)
        self.notes.textChanged.connect(self._emit)
        main.addWidget(self.assignee)
        main.addWidget(self.notes)

        initial = self.selection_limit
        for _ in range(initial):
            self.add_combo(emit=False)
        for i, val in enumerate(state.selections):
            if i < len(self.combos):
                self.combos[i].setCurrentText(val)
        self._update_buttons()

    def _build_info_text(self, options: List[str]) -> str:
        details = self.definition.help_text.strip() if self.definition.help_text else ""
        options_text = "\n".join(f"• {o}" for o in options)
        base = (
            f"Thema: {self.definition.title}\n"
            f"Beschreibung: {self.definition.description}\n\n"
            f"Mögliche Antworten ({len(options)}):\n{options_text}"
        )
        if not details:
            return base
        return f"{base}\n\nHinweise:\n{details}"

    def add_combo(self, emit: bool = True) -> None:
        if len(self.combos) >= self.selection_limit:
            return
        combo = QComboBox()
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
        self.add_btn.setEnabled(len(self.combos) < self.selection_limit)
        self.remove_btn.setEnabled(len(self.combos) > 1)

    def get_state(self) -> TopicState:
        selections = []
        for c in self.combos:
            value = c.currentText().strip()
            if value and value not in selections:
                selections.append(value)
        return TopicState(selections=selections, notes=self.notes.toPlainText().strip(), assignee=self.assignee.text().strip())

    def _emit(self) -> None:
        self.changed.emit()
