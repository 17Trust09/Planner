from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGroupBox, QLabel, QScrollArea, QTabWidget, QVBoxLayout, QWidget

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

        root = QVBoxLayout(self)
        head = QLabel(f"<h2>{title}</h2>")
        subtitle = QLabel("Themen sind nach Unterbereichen gegliedert. Dadurch bleiben Planung und IT-Struktur übersichtlich.")
        subtitle.setStyleSheet("color:#475569;")
        root.addWidget(head)
        root.addWidget(subtitle)

        tabs = QTabWidget()
        root.addWidget(tabs)

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

            for section, section_topics in sections.items():
                box = QGroupBox(section)
                box_layout = QVBoxLayout(box)
                for topic in section_topics:
                    row_state = self.states.setdefault(topic.key, TopicState())
                    row = TopicRowWidget(topic, row_state)
                    row.changed.connect(lambda key=topic.key, widget=row: self._update_state(key, widget))
                    row.setFrameStyle(QFrame.NoFrame) if hasattr(row, "setFrameStyle") else None
                    self.rows[topic.key] = row
                    box_layout.addWidget(row)
                layout.addWidget(box)

            layout.addStretch()
            scroll.setWidget(body)
            tabs.addTab(scroll, domain_labels[domain])

    def _update_state(self, key: str, row: TopicRowWidget) -> None:
        self.states[key] = row.get_state()
        self.changed.emit()

    def persist(self) -> None:
        for key, row in self.rows.items():
            self.states[key] = row.get_state()
