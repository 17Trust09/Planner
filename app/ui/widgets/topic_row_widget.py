from __future__ import annotations

from pathlib import Path
from typing import List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import OPTION_SETS, TopicDefinition
from app.models.project import TopicState

DOCUMENT_CATEGORIES = [
    "Betriebsanweisung",
    "Bedienungsanleitung",
    "Allgemeine Unterlagen",
    "Dokumentation",
]


class TopicRowWidget(QWidget):
    changed = Signal()

    def __init__(self, definition: TopicDefinition, state: TopicState):
        super().__init__()
        self.definition = definition
        self.state = state
        self.combos: List[QComboBox] = []

        main = QVBoxLayout(self)
        title = QLabel(f"<b>{definition.title}</b>")
        desc = QLabel(definition.description)
        desc.setStyleSheet("color:#64748b;")
        main.addWidget(title)
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

        assets_box = QGroupBox("Anlagen (itemspezifisch)")
        assets_layout = QVBoxLayout(assets_box)

        image_row = QHBoxLayout()
        self.select_image_btn = QPushButton("Bild auswählen")
        self.clear_image_btn = QPushButton("Bild entfernen")
        self.select_image_btn.clicked.connect(self._select_image)
        self.clear_image_btn.clicked.connect(self._clear_image)
        image_row.addWidget(self.select_image_btn)
        image_row.addWidget(self.clear_image_btn)
        image_row.addStretch()
        assets_layout.addLayout(image_row)

        self.image_label = QLabel()
        assets_layout.addWidget(self.image_label)

        docs_row = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItems(DOCUMENT_CATEGORIES)
        self.upload_doc_btn = QPushButton("Datei hochladen")
        self.upload_doc_btn.clicked.connect(self._upload_document)
        docs_row.addWidget(QLabel("Kategorie:"))
        docs_row.addWidget(self.category_combo)
        docs_row.addWidget(self.upload_doc_btn)
        assets_layout.addLayout(docs_row)

        self.documents_list = QListWidget()
        assets_layout.addWidget(self.documents_list)

        remove_row = QHBoxLayout()
        self.remove_doc_btn = QPushButton("Ausgewählte Datei entfernen")
        self.remove_doc_btn.clicked.connect(self._remove_selected_document)
        remove_row.addWidget(self.remove_doc_btn)
        remove_row.addStretch()
        assets_layout.addLayout(remove_row)

        main.addWidget(assets_box)

        initial = max(1, len(state.selections))
        for _ in range(initial):
            self.add_combo(emit=False)
        for i, val in enumerate(state.selections):
            if i < len(self.combos):
                self.combos[i].setCurrentText(val)
        self._update_buttons()
        self._refresh_assets_view()

    def add_combo(self, emit: bool = True) -> None:
        if len(self.combos) >= self.definition.max_selections:
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
        self.add_btn.setEnabled(len(self.combos) < self.definition.max_selections)
        self.remove_btn.setEnabled(len(self.combos) > 1)

    def _select_image(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Anzeigebild auswählen", "", "Bilder (*.png *.jpg *.jpeg *.webp *.bmp)")
        if not selected:
            return
        self.state.display_image = selected
        self._refresh_assets_view()
        self._emit()

    def _clear_image(self) -> None:
        if not self.state.display_image:
            return
        self.state.display_image = ""
        self._refresh_assets_view()
        self._emit()

    def _upload_document(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Dokument auswählen", "", "Alle Dateien (*.*)")
        if not selected:
            return
        self.state.documents.append({"category": self.category_combo.currentText(), "path": selected})
        self._refresh_assets_view()
        self._emit()

    def _remove_selected_document(self) -> None:
        row = self.documents_list.currentRow()
        if row < 0 or row >= len(self.state.documents):
            return
        self.state.documents.pop(row)
        self._refresh_assets_view()
        self._emit()

    def _refresh_assets_view(self) -> None:
        if self.state.display_image:
            self.image_label.setText(f"Ausgewählt: {Path(self.state.display_image).name}")
        else:
            self.image_label.setText("Kein Anzeigebild ausgewählt")

        self.documents_list.clear()
        for item in self.state.documents:
            category = item.get("category", "Unkategorisiert")
            file_name = Path(item.get("path", "")).name or "Unbekannte Datei"
            self.documents_list.addItem(f"{category}: {file_name}")

    def get_state(self) -> TopicState:
        selections = []
        for c in self.combos:
            value = c.currentText().strip()
            if value and value not in selections:
                selections.append(value)
        return TopicState(
            selections=selections,
            notes=self.notes.toPlainText().strip(),
            assignee=self.assignee.text().strip(),
            display_image=self.state.display_image,
            documents=list(self.state.documents),
        )

    def _emit(self) -> None:
        self.changed.emit()
