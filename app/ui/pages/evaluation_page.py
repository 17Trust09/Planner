from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget

from app.models.project import Project
from app.services.evaluation import build_room_matrix, room_score, topic_metrics
from app.services.validation import detect_conflicts


class EvaluationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("<h2>Auswertung</h2>"))
        self.table = QTableWidget()
        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.summary)

    def refresh(self, project: Project) -> None:
        matrix = build_room_matrix(project)
        metrics = topic_metrics(project)
        rooms = list(project.rooms.keys())
        topics = list(matrix.keys())

        self.table.setRowCount(len(topics))
        self.table.setColumnCount(len(rooms) + 1)
        self.table.setHorizontalHeaderLabels(["Topic", *rooms])
        for row_idx, topic in enumerate(topics):
            self.table.setItem(row_idx, 0, QTableWidgetItem(topic))
            for col_idx, room in enumerate(rooms, 1):
                text = ", ".join(matrix[topic][room]) or "—"
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(text))

        scores = room_score(project)
        conflicts = detect_conflicts(project)
        lines = ["Kennzahlen / Konflikte:"]
        for topic, m in metrics.items():
            lines.append(f"- {topic}: Räume {m['rooms_with_selection']}/{m['room_count']} | Diversity {m['diversity']} | Dominanz {m['dominant_ratio']:.2f}")
        lines.append("\nRaum-Ampeln:")
        for room, s in scores.items():
            lines.append(f"- {room}: {s['ampel']} ({s['value']}) | Konflikte: {s['conflicts']}")
        lines.append("\nKonfliktliste:")
        if not conflicts:
            lines.append("- Keine Konflikte gefunden")
        else:
            for room, items in conflicts.items():
                for item in items:
                    lines.append(f"- {room}: {item}")
        self.summary.setPlainText("\n".join(lines))
