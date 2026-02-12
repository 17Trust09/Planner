from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGroupBox, QLabel, QScrollArea, QVBoxLayout, QWidget

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
        root.addWidget(head)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        body = QWidget()
        layout = QVBoxLayout(body)

        by_section = defaultdict(list)
        for topic in topics:
            by_section[topic.section].append(topic)

        for section, section_topics in by_section.items():
            box = QGroupBox(section)
            box_layout = QVBoxLayout(box)
            for topic in section_topics:
                state = states.get(topic.key, TopicState())
                states.setdefault(topic.key, state)
                row = TopicRowWidget(topic, state)
                row.changed.connect(lambda key=topic.key, widget=row: self._update_state(key, widget))
                row.setFrameStyle(QFrame.NoFrame) if hasattr(row, "setFrameStyle") else None
                self.rows[topic.key] = row
                box_layout.addWidget(row)
            layout.addWidget(box)
        layout.addStretch()

        scroll.setWidget(body)
        root.addWidget(scroll)

    def _update_state(self, key: str, row: TopicRowWidget) -> None:
        self.states[key] = row.get_state()
        self.changed.emit()

    def persist(self) -> None:
        for key, row in self.rows.items():
            self.states[key] = row.get_state()
