from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from app.models.definitions import TopicDefinition
from app.models.project import TopicState
from app.ui.widgets.topic_row_widget import TopicRowWidget


class TopicPage(QWidget):
    changed = Signal()

    def __init__(self, title: str, topics: List[TopicDefinition], states: Dict[str, TopicState]):
        super().__init__()
        self.topics = topics
        self.states = states
        self.rows: Dict[str, TopicRowWidget] = {}
        self.tabs = QTabWidget()
        self.topic_tab_index: Dict[str, int] = {}

        root = QVBoxLayout(self)
        head_row = QHBoxLayout()
        head = QLabel(f"<h2>{title}</h2>")
        page_help = QPushButton("?")
        page_help.setObjectName("helpButton")
        page_help.setFixedWidth(28)
        page_help.clicked.connect(self._show_page_help)
        head_row.addWidget(head)
        head_row.addStretch()
        head_row.addWidget(page_help)
        subtitle = QLabel("Themen sind nach Unterbereichen gegliedert. Dadurch bleiben Planung und IT-Struktur übersichtlich.")
        subtitle.setStyleSheet("color:#94a3b8;")
        root.addLayout(head_row)
        root.addWidget(subtitle)

        root.addWidget(self.tabs)

        domain_labels = {
            "SMART_HOME": "Smart Home",
            "ELEKTRIK": "Elektrik",
            "IT_NETZWERK": "IT & Netzwerk",
        }

        by_domain_section = defaultdict(lambda: defaultdict(list))
        for topic in topics:
            domain = topic.domains[0] if topic.domains else "SMART_HOME"
            by_domain_section[domain][topic.section].append(topic)

        for domain in ["SMART_HOME", "ELEKTRIK", "IT_NETZWERK"]:
            sections = by_domain_section.get(domain)
            if not sections:
                continue

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            body = QWidget()
            layout = QVBoxLayout(body)

            tab_index = self.tabs.count()
            for section, section_topics in sections.items():
                box = QGroupBox(section)
                box_layout = QVBoxLayout(box)
                for topic in section_topics:
                    row_state = self.states.setdefault(topic.key, TopicState())
                    row = TopicRowWidget(topic, row_state)
                    row.changed.connect(lambda key=topic.key, widget=row: self._update_state(key, widget))
                    row.setFrameStyle(QFrame.NoFrame) if hasattr(row, "setFrameStyle") else None
                    self.rows[topic.key] = row
                    self.topic_tab_index[topic.key] = tab_index
                    box_layout.addWidget(row)
                layout.addWidget(box)

            layout.addStretch()
            scroll.setWidget(body)
            self.tabs.addTab(scroll, domain_labels[domain])

    def _show_page_help(self) -> None:
        QMessageBox.information(
            self,
            "Hilfe zur Seite",
            "Diese Seite ist in Tabs (Smart Home / Elektrik / IT & Netzwerk) gegliedert. "
            "Jede Frage hat ein eigenes '?' für eine Einsteiger-Erklärung inklusive Bedeutung der Auswahloptionen.",
        )

    def mark_missing(self, topic_key: str, is_missing: bool) -> None:
        row = self.rows.get(topic_key)
        if row:
            row.set_missing(is_missing)

    def clear_all_missing(self) -> None:
        for row in self.rows.values():
            row.set_missing(False)

    def focus_topic(self, topic_key: str) -> None:
        tab_idx = self.topic_tab_index.get(topic_key)
        if tab_idx is not None:
            self.tabs.setCurrentIndex(tab_idx)
        row = self.rows.get(topic_key)
        if row:
            row.setFocus()

    def _update_state(self, key: str, row: TopicRowWidget) -> None:
        self.states[key] = row.get_state()
        row.set_missing(False)
        self.changed.emit()

    def persist(self) -> None:
        for key, row in self.rows.items():
            self.states[key] = row.get_state()
