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
    QMessageBox,
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
    "CONTROL_OPTIONS": {
        "Kippschalter (klassisch)": "Klassischer Schalter mit fester EIN/AUS-Funktion ohne Szenenlogik.",
        "Taster (Impuls)": "Impulsgeber für Relais/Aktor; Logik liegt in Aktor oder Steuerung.",
        "Doppeltaster / Szenentaster": "Mehrere Funktionen/Szenen über getrennte Tasten am selben Bedienstelle.",
        "Drehdimmer": "Haptischer Dimmer direkt am Raum, oft mit Ein/Aus + Helligkeitsregelung.",
        "Wallpanel/Tablet": "Visualisierung an der Wand für zentrale Bedienung mehrerer Funktionen.",
        "Sprachsteuerung (optional)": "Bedienung per Sprachassistent als Ergänzung zu physischen Tastern.",
        "App (nur Ergänzung)": "Smartphone-App als Zusatz, nicht als alleinige Primärbedienung.",
    },
    "LIGHT_OPTIONS": {
        "Nur Grundbeleuchtung": "Ein zentraler Lichtkreis pro Raum ohne zusätzliche Lichtstimmung.",
        "Zonen (mehrere Lichtkreise)": "Mehrere getrennt schaltbare Bereiche im Raum (z. B. Decke, Esstisch).",
        "Indirekt (LED-Cove/Decke/Wand)": "Licht über Reflexion/Verblendung für weiche Grundstimmung.",
        "Direkt (Spots/Downlights)": "Gerichtetes Licht auf Nutzflächen mit klarer Ausleuchtung.",
        "Akzentlicht (Regal/Nische)": "Gezielte Betonung von Möbeln/Architektur, eher dekorativ.",
        "RGB (Ambient)": "Farbwechsel-Licht für Szenen und Ambiente, meist nicht Hauptlicht.",
        "Tunable White (Warm/Kalt)": "Einstellbare Farbtemperatur (warm bis kaltweiß) je nach Nutzung.",
    },
    "LIGHT_LOGIC_OPTIONS": {
        "Aktor im Schaltschrank (Stern)": "Schalt-/Dimmaktor sitzt zentral im Schaltschrank; Leitungen laufen sternförmig dorthin.",
        "Aktor Unterputz (dezentral)": "Aktor liegt lokal hinter Schalter/Leuchte im Raum.",
        "Smarte Leuchtmittel (Dauerstrom)": "Leuchten erhalten Dauerstrom; Schaltlogik sitzt in der Lampe selbst.",
        "Mischform (Aktor + smarte Lampen)": "Kombination aus klassischer Aktorik und smarten Leuchtmitteln je nach Bereich.",
    },
    "HEAT_OPTIONS": {
        "Keine Einzelraumregelung": "Temperatur wird zentral geführt, nicht pro Raum individuell geregelt.",
        "Thermostat (Heizkörper)": "Raumweise Regelung über Heizkörperthermostate.",
        "FBH (Fußbodenheizung) – Raumregelung": "Raumweise Steuerung der Fußbodenheizkreise über Stellantriebe.",
        "Fenster-auf-Erkennung": "Heizleistung wird bei geöffnetem Fenster reduziert/pausiert.",
        "Zeitprogramm": "Temperaturprofile nach Tageszeit/Wochentag.",
        "Nachtabsenkung / Eco-Modus": "Automatische Sollwertsenkung zur Energieeinsparung in Ruhezeiten.",
    },
    "SHADE_OPTIONS": {
        "Keine Beschattung": "Keine automatisierte oder geplante Rollladen/Jalousie-Logik.",
        "Manuell": "Bedienung nur per Taster/Hand ohne Automationsregeln.",
        "Zeitgesteuert": "Feste Fahrzeiten (z. B. morgens hoch, abends runter).",
        "Sonnenstand (Azimut/Höhe)": "Automatik orientiert sich an Sonnenposition für Blend-/Wärmeschutz.",
        "Wetter/Windschutz": "Sicherheitsautomatik bei Wind/Regen (v. a. bei Raffstores/Markisen).",
        "Sommer-Hitzeschutz": "Automatisches Schließen bei starker Einstrahlung zur Kühlungsunterstützung.",
    },
    "ROOM_NETWORK_OPTIONS": {
        "LAN-Dose vorhanden": "Fester Ethernet-Anschluss ist geplant/vorhanden.",
        "LAN-Dose optional": "LAN ist vorgesehen, kann aber je nach Bedarf entfallen.",
        "WLAN reicht": "Raumnutzung benötigt keinen festen LAN-Anschluss.",
        "AP in/nahe Raum geplant": "Access Point in unmittelbarer Nähe für stabile Funkversorgung.",
        "PoE im Raum (z.B. Panel/Kamera)": "Stromversorgung über Netzwerkkabel für passende Geräte.",
    },
    "SECURITY_OPTIONS": {
        "Kein Bedarf": "Für diesen Raum sind keine speziellen Sicherheitsfunktionen geplant.",
        "Fensterkontakte": "Öffnungsstatus der Fenster wird überwacht.",
        "Türkontakt": "Öffnungsstatus der Tür wird überwacht.",
        "Alarmmodus (Nacht/Abwesend)": "Sensoren werden je nach Hausmodus scharf/unscharf geschaltet.",
        "Sirene/Signalgeber": "Akustische/optische Alarmierung bei erkannten Ereignissen.",
        "Kamera (lokal)": "Videoüberwachung mit lokaler Speicherung/Verarbeitung.",
    },
    "WATER_OPTIONS": {
        "Nicht nötig": "Kein Leckschutz für diesen Bereich vorgesehen.",
        "Lecksensor": "Nur Erkennung von Wasseraustritt ohne automatische Reaktion.",
        "Lecksensor + Push-Alarm": "Erkennung plus Benachrichtigung auf Smartphone.",
        "Lecksensor + Absperrventil (optional)": "Erkennung plus automatische/optionale Wasserabschaltung.",
    },
    "POWER_OPTIONS": {
        "Normale Steckdosen": "Standard-Stromkreise ohne Schalt- oder Messfunktion.",
        "Schaltbar (Smart Plug)": "Steckdosen/Geräte lassen sich ein- und ausschalten.",
        "Schaltbar + Messung": "Schalten und gleichzeitige Energie-/Leistungsmessung.",
        "Fester Aktor/Relais + Messung": "Fest installierte Schalttechnik inkl. Messung im Verteil-/Unterputzbereich.",
        "Großverbraucher separat messen": "Eigene Messung für Geräte mit hoher Leistung (z. B. Trockner, Sauna).",
    },
    "GLOBAL_STERN_OPTIONS": {
        "Keine Sternverkabelung (klassisch)": "Klassische Installation, Schalter/Aktoren lokal ohne zentrale Sternstruktur.",
        "Teilweise Sternverkabelung": "Nur ausgewählte Kreise zentral geführt, Rest klassisch/dezentral.",
        "Komplette Sternverkabelung": "Alle relevanten Leitungen laufen zentral in den Verteilerschrank.",
        "Zentrale Aktoren (Hutschiene)": "Schalt-/Dimmaktoren sitzen im Schaltschrank auf Hutschiene.",
        "Dezentrale Aktoren (UP)": "Aktorik sitzt Unterputz direkt in den Räumen.",
    },
    "GLOBAL_PHASE_OPTIONS": {
        "Nicht relevant": "Keine besondere Phasenplanung erforderlich.",
        "3 Phasen sauber verteilt": "Verbraucher werden möglichst gleichmäßig auf L1/L2/L3 verteilt.",
        "3 Phasen + Lastmanagement vorgesehen": "Zusätzlich zur Verteilung wird aktive Laststeuerung eingeplant.",
        "Lastmanagement zwingend (WP/Wallbox)": "Pflicht bei großen Lasten wie Wärmepumpe/Wallbox, um Spitzen zu begrenzen.",
    },
    "SERVER_OPTIONS": {
        "Raspberry Pi": "Kompakte, stromsparende Lösung für kleine bis mittlere Installationen.",
        "Intel NUC / Mini-PC": "Leistungsstärkeres lokales System mit Reserven für Add-ons und Datenbanken.",
        "Unraid Server": "Container-/VM-basierte Plattform auf Unraid-System.",
        "Proxmox Host": "Virtualisierungsplattform für HA als VM/Container mit Snapshot-Optionen.",
        "NAS (Synology/QNAP)": "Betrieb auf NAS-Gerät, häufig via Container-App.",
        "Home Assistant Green/Yellow": "Dedizierte HA-Hardware mit einfacher Inbetriebnahme.",
        "VM auf bestehendem Server": "Einbindung in vorhandene Serverlandschaft per virtueller Maschine.",
    },
    "HA_OS_OPTIONS": {
        "Home Assistant OS": "Komplettsystem inkl. Supervisor/Add-ons; einfache Verwaltung.",
        "Home Assistant Container": "HA als Docker-Container; Add-ons/Updates separat verwalten.",
        "Home Assistant Supervised": "Linux + Docker + Supervisor; flexibel, aber wartungsintensiver.",
        "Home Assistant Core": "Reine Python-Installation ohne Supervisor/Add-ons.",
    },
    "BACKUP_OPTIONS": {
        "Keine Strategie": "Es ist aktuell kein belastbares Backup-Konzept vorgesehen.",
        "Lokales Backup": "Sicherung auf lokalem Datenträger im Hausnetz.",
        "NAS-Backup": "Zentrale Sicherung auf NAS-System.",
        "Offsite-Backup": "Zusätzliche Sicherung außerhalb des Standorts.",
        "3-2-1 Backup-Strategie": "3 Kopien, 2 Medientypen, 1 Kopie extern für hohe Ausfallsicherheit.",
    },
    "PROTOCOL_OPTIONS": {
        "Zigbee": "Mesh-Funkprotokoll für Sensoren/Aktoren mit niedrigem Energiebedarf.",
        "Z-Wave": "Funkprotokoll im Sub-GHz-Bereich mit guter Gebäudedurchdringung.",
        "Thread/Matter": "Neuer Standard für herstellerübergreifende Smart-Home-Kompatibilität.",
        "KNX": "Kabelgebundenes/professionelles Gebäudesystem für robuste Automatisierung.",
        "Modbus": "Industrienahe Schnittstelle für technische Anlagen und Energiemessung.",
        "WLAN": "IP-basierte Funkanbindung über bestehendes Wi-Fi-Netz.",
        "Bluetooth": "Kurzstreckenfunk, meist für einzelne Geräte oder Provisionierung.",
        "MQTT": "Nachrichtenprotokoll zur Integration verteilter Smart-Home-Komponenten.",
    },
    "CABLE_OPTIONS": {
        "Klassische Verdrahtung": "Konventionelle Elektroinstallation ohne zentrale Smart-Home-Struktur.",
        "Teilweise Sternverdrahtung": "Ein Teil der Verbraucher wird sternförmig zentral angebunden.",
        "Komplette Sternverdrahtung": "Alle relevanten Verbraucher/Bedienstellen sternförmig zur Zentrale.",
        "BUS-basierte Verdrahtung": "Steuerung über Bus-System (z. B. KNX), getrennt von Lastkreisen.",
        "Mischform": "Kombination aus klassischer, Stern- und/oder BUS-Verdrahtung.",
    },
    "ROOM_ROLE_OPTIONS": {
        "Wohnen": "Fokus auf Komfort, Medien, flexible Szenen und Aufenthaltsqualität.",
        "Arbeiten": "Fokus auf produktives Licht, stabile Netzverbindung und Ergonomie.",
        "Schlafen": "Fokus auf Ruhe, einfache Bedienung, Nacht-/Morgenautomationen.",
        "Kinder": "Fokus auf Sicherheit, einfache Bedienbarkeit und zeitliche Begrenzungen.",
        "Bad/Wellness": "Fokus auf Feuchtraum-Anforderungen, Komfortlicht und Lüftung.",
        "Technikraum": "Fokus auf Infrastruktur, Wartungszugang und Monitoring.",
        "Verkehrsfläche": "Fokus auf Orientierung/Präsenzlicht und kurze Aufenthaltsdauer.",
    },
    "COVERAGE_OPTIONS": {
        "Hoch (Office/Streaming)": "Hohe Bandbreite und stabile Latenz auch bei starker Nutzung.",
        "Mittel": "Normale Alltagsnutzung mit solider Verbindung.",
        "Basis": "Grundversorgung für einfache Anwendungen.",
        "Optional": "Nur bei Bedarf aktiv ausbauen.",
    },
    "CAMERA_STORAGE_OPTIONS": {
        "Keine Kamera": "Es wird keine Videoüberwachung geplant.",
        "NVR lokal": "Aufzeichnung auf dediziertem lokalen Rekorder.",
        "NAS-Aufzeichnung": "Kameradaten werden auf NAS gespeichert.",
        "SD-Karte lokal": "Speicherung direkt in der Kamera auf SD-Karte.",
        "Hybrid": "Kombination aus lokaler und zentraler Speicherung.",
    },
    "AUTOMATION_LEVEL_OPTIONS": {
        "Keine Automationen": "Nur manuelle Bedienung, keine Regeln/Szenen.",
        "Basis (Zeit/Schwellwert)": "Einfache Regeln nach Uhrzeit oder Messwerten.",
        "Mittel (Szenen + Präsenz)": "Kombination aus Szenenlogik und Anwesenheitserkennung.",
        "Erweitert (Kontext + Energie)": "Umfangreiche Logik mit Kontextdaten und Energieoptimierung.",
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
        info_btn.setToolTipDuration(30000)
        info_btn.setCursor(Qt.PointingHandCursor)
        info_btn.clicked.connect(self._show_info_dialog)
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

    def _show_info_dialog(self) -> None:
        QMessageBox.information(self, f"Info: {self.definition.title}", self.info_text)

    def _build_info_text(self) -> str:
        topic_explainer = TOPIC_HELP_OVERRIDES.get(self.definition.key, self.definition.help_text.strip() or self.definition.description)
        legends = OPTION_SET_LEGENDS.get(self.definition.option_set, {})

        if self.definition.option_set == "YES_MAYBE_NO":
            return f"Thema: {self.definition.title}\nBedeutung: {topic_explainer}"

        options_text = "\n".join(f"• {option}: {legends.get(option, option)}" for option in self.options)
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
