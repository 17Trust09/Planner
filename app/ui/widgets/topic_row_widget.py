from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import OPTION_SETS, TopicDefinition
from app.models.project import TopicState

TOPIC_HELP_OVERRIDES: Dict[str, str] = {
    "global_cloud": "Legt fest, ob Cloud-Dienste (z. B. Fernzugriff, Hersteller-Services) erlaubt sind oder ob alles lokal/offline betrieben werden soll.",
    "global_stern": "Beschreibt, ob Leitungen sternförmig zentral im Schaltschrank zusammenlaufen oder dezentral verteilt werden.",
    "global_cable_type": "Definiert die grundlegende Verdrahtungsphilosophie (klassisch, Stern, BUS oder Mischform).",
    "global_phase": "Hier wird geplant, wie elektrische Lasten auf Phasen verteilt werden, um Überlastung und Schieflast zu vermeiden.",
    "room_heat": "Legt fest, wie die Raumtemperatur geregelt wird (manuell, zeitgesteuert oder sensorbasiert).",
    "room_light_logic": "Beschreibt, wo die Schaltlogik sitzt: zentral im Schaltschrank, dezentral im Raum oder als Mischform.",
}

OPTION_SET_LEGENDS: Dict[str, Dict[str, str]] = {
    "GLOBAL_STERN_OPTIONS": {
        "Keine Sternverkabelung (klassisch)": "Klassische Installation, Schalter/Aktoren lokal ohne zentrale Sternstruktur.",
        "Teilweise Sternverkabelung": "Nur ausgewählte Kreise zentral geführt, Rest klassisch/dezentral.",
        "Komplette Sternverkabelung": "Alle relevanten Leitungen laufen zentral in den Verteilerschrank.",
        "Zentrale Aktoren (Hutschiene)": "Schalt-/Dimmaktoren sitzen im Schaltschrank auf Hutschiene.",
        "Dezentrale Aktoren (UP)": "Aktorik sitzt Unterputz direkt in den Räumen.",
    },
    "CABLE_OPTIONS": {
        "Klassische Verdrahtung": "Konventionelle Elektroinstallation ohne zentrale Smart-Home-Struktur.",
        "Teilweise Sternverdrahtung": "Ein Teil der Verbraucher wird sternförmig zentral angebunden.",
        "Komplette Sternverdrahtung": "Alle relevanten Verbraucher/Bedienstellen sternförmig zur Zentrale.",
        "BUS-basierte Verdrahtung": "Steuerung über Bus-System (z. B. KNX), getrennt von Lastkreisen.",
        "Mischform": "Kombination aus klassischer, Stern- und/oder BUS-Verdrahtung.",
    },
    "GLOBAL_PHASE_OPTIONS": {
        "Nicht relevant": "Keine besondere Phasenplanung erforderlich.",
        "3 Phasen sauber verteilt": "Verbraucher werden möglichst gleichmäßig auf L1/L2/L3 verteilt.",
        "3 Phasen + Lastmanagement vorgesehen": "Zusätzlich zur Verteilung wird aktive Laststeuerung eingeplant.",
        "Lastmanagement zwingend (WP/Wallbox)": "Pflicht bei großen Lasten wie Wärmepumpe/Wallbox, um Spitzen zu begrenzen.",
    },
    "HA_OS_OPTIONS": {
        "Home Assistant OS": "Komplettsystem inkl. Supervisor/Add-ons; einfache Verwaltung.",
        "Home Assistant Container": "HA als Docker-Container; Add-ons/Updates separat verwalten.",
        "Home Assistant Supervised": "Linux + Docker + Supervisor; flexibel, aber wartungsintensiver.",
        "Home Assistant Core": "Reine Python-Installation ohne Supervisor/Add-ons.",
    },
}


class SafeComboBox(QComboBox):
    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.view().isVisible() or self.hasFocus():
            super().wheelEvent(event)
            return
        event.ignore()


class TopicRowWidget(QWidget):
    changed = Signal()

    def __init__(self, definition: TopicDefinition, state: TopicState):
        super().__init__()
        self.definition = definition
        self.state = state
        self.combos: List[QComboBox] = []

        self.options = OPTION_SETS[self.definition.option_set]
        self.selection_limit = len(self.options)
        self.info_text = self._build_info_text()

        main = QVBoxLayout(self)

        title_row = QHBoxLayout()
        title = QLabel(f"<b>{definition.title}</b>")
        title.setToolTip(self.info_text)

        info_btn = QToolButton()
        info_btn.setText("?")
        info_btn.setToolTip(self.info_text)
        info_btn.setCursor(Qt.WhatsThisCursor)
        info_btn.setStyleSheet("QToolButton{color:#1d4ed8; font-weight:700; border:1px solid #93c5fd; border-radius:10px; padding:0 6px;}")

        title_row.addWidget(title)
        title_row.addWidget(info_btn)
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

        initial = max(1, len(state.selections))
        for _ in range(initial):
            self.add_combo(emit=False)
        for i, val in enumerate(state.selections):
            if i < len(self.combos):
                self.combos[i].setCurrentText(val)
        self._update_buttons()

    def _build_info_text(self) -> str:
        topic_explainer = TOPIC_HELP_OVERRIDES.get(self.definition.key, self.definition.help_text.strip() or self.definition.description)
        legends = OPTION_SET_LEGENDS.get(self.definition.option_set, {})
        options_text = "\n".join(f"• {option}: {legends.get(option, 'Auswahloption für dieses Thema.') }" for option in self.options)
        return (
            f"Thema: {self.definition.title}\n"
            f"Bedeutung: {topic_explainer}\n\n"
            f"Auswahl-Legende:\n{options_text}"
        )

    def add_combo(self, emit: bool = True) -> None:
        if len(self.combos) >= self.selection_limit:
            return
        combo = SafeComboBox()
        combo.setFocusPolicy(Qt.StrongFocus)
        combo.addItem("")
        combo.addItems(self.options)
        combo.currentTextChanged.connect(lambda _: self._combo_changed(combo))
        combo.setToolTip(self.info_text)
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
