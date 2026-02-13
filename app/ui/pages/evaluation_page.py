from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.project import Project
from app.services.evaluation import build_room_matrix, room_score, topic_metrics
from app.services.validation import detect_conflicts


class EvaluationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("<h2>Auswertung</h2>"))

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.matrix_container = QWidget()
        self.matrix_layout = QVBoxLayout(self.matrix_container)
        self.matrix_layout.setContentsMargins(0, 0, 0, 0)
        self.matrix_layout.setSpacing(10)
        self.scroll.setWidget(self.matrix_container)

        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.summary)

    def refresh(self, project: Project) -> None:
        matrix = build_room_matrix(project)
        metrics = topic_metrics(project)
        rooms = list(project.rooms.keys())
        topics = list(matrix.keys())

        while self.matrix_layout.count() > 0:
            item = self.matrix_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for topic in topics:
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setStyleSheet("QFrame { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; }")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(6)

            header = QLabel(f"<b>{topic}</b>")
            card_layout.addWidget(header)

            for room in rooms:
                values = ", ".join(matrix[topic][room]) or "—"
                row = QLabel(f"<b>{room}:</b> {values}")
                row.setWordWrap(True)
                row.setTextFormat(Qt.RichText)
                row.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
                card_layout.addWidget(row)

            self.matrix_layout.addWidget(card)
        self.matrix_layout.addStretch()

        scores = room_score(project)
        conflicts = detect_conflicts(project)
        lines = ["Kennzahlen / Konflikte:"]
        for topic, m in metrics.items():
            lines.append(f"- {topic}: Räume {m['rooms_with_selection']}/{m['room_count']} | Diversity {m['diversity']} | Dominanz {m['dominant_ratio']:.2f}")
        lines.append("\nRaum-Ampeln:")
        for room, s in scores.items():
            badge = self._ampel_badge(s["ampel"])
            lines.append(f"- {room}: {badge} ({s['value']}) | Konflikte: {s['conflicts']}")
        lines.append("\nKonfliktliste:")
        if not conflicts:
            lines.append("- Keine Konflikte gefunden")
        else:
            for room, items in conflicts.items():
                for item in items:
                    lines.append(f"- {room}: {item}")
        self.summary.setHtml("<br>".join(lines))

    @staticmethod
    def _ampel_badge(color: str) -> str:
        palette = {
            "gruen": ("#16A34A", "Grün"),
            "gelb": ("#CA8A04", "Gelb"),
            "rot": ("#DC2626", "Rot"),
        }
        tone, _ = palette.get(color, ("#64748B", "Unbekannt"))
        return f"<span style='color:{tone};font-size:16px;'>●</span>"
