from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget

from app.models.project import Project
from app.services.evaluation import build_room_matrix, network_rollup, room_score, topic_metrics
from app.services.validation import detect_conflicts


class EvaluationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        head = QHBoxLayout()
        head.addWidget(QLabel("<h2>Auswertung</h2>"))
        help_btn = QPushButton("?")
        help_btn.setObjectName("helpButton")
        help_btn.setFixedWidth(28)
        help_btn.clicked.connect(self._show_help)
        head.addStretch()
        head.addWidget(help_btn)

        self.layout.addLayout(head)
        self.table = QTableWidget()
        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.summary)

    def _show_help(self) -> None:
        QMessageBox.information(
            self,
            "Hilfe: Auswertung",
            "Hier werden alle Antworten raumübergreifend zusammengefasst.\n"
            "Zusätzlich gibt es eine LAN-Gesamtsumme (Ports/Kabel) plus Switch-Empfehlung.",
        )

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
        net = network_rollup(project)

        lines = ["Kennzahlen / Konflikte:"]
        for topic, m in metrics.items():
            lines.append(f"- {topic}: Räume {m['rooms_with_selection']}/{m['room_count']} | Diversity {m['diversity']} | Dominanz {m['dominant_ratio']:.2f}")

        lines.append("\nNetzwerk-Gesamtsumme:")
        if not net["ports_by_room"]:
            lines.append("- Noch keine LAN-Ports je Raum erfasst.")
        else:
            for room, amount in net["ports_by_room"].items():
                lines.append(f"- {room}: {amount} Port(s) / Kabel")
            lines.append(f"- Gesamtsumme Ports: {net['total_ports']}")
            lines.append(f"- Gesamtsumme Kabel: {net['total_cables']}")
            lines.append(f"- Empfehlung mit Reserve/Uplink: {net['ports_with_overhead']} Ports")
            lines.append(f"- Empfohlene Switch-Größe: {net['recommended_switch']}")

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
