from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import OUTDOOR_AREA_NAME
from app.models.project import Project
from app.services.evaluation import build_room_matrix, network_rollup, room_score, topic_metrics
from app.services.pricing import estimate_project_costs
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
        self.layout.addWidget(self.table, 2)

        self.detail_tabs = QTabWidget()
        self.metrics_view = QTextEdit()
        self.metrics_view.setReadOnly(True)
        self.network_view = QTextEdit()
        self.network_view.setReadOnly(True)
        self.score_view = QTextEdit()
        self.score_view.setReadOnly(True)
        self.conflicts_view = QTextEdit()
        self.conflicts_view.setReadOnly(True)
        self.cost_view = QTextEdit()
        self.cost_view.setReadOnly(True)

        self.detail_tabs.addTab(self.metrics_view, "Kennzahlen")
        self.detail_tabs.addTab(self.network_view, "Netzwerk")
        self.detail_tabs.addTab(self.score_view, "Raum-Ampeln")
        self.detail_tabs.addTab(self.conflicts_view, "Konflikte")
        self.detail_tabs.addTab(self.cost_view, "Kosten")
        self.layout.addWidget(self.detail_tabs, 1)

    def _show_help(self) -> None:
        QMessageBox.information(
            self,
            "Hilfe: Auswertung",
            "Die Auswertung ist in Tabs gegliedert: Kennzahlen, Netzwerk, Raum-Ampeln, Konflikte und Kosten.\n"
            "So sind die Infos übersichtlicher und leichter zu lesen.",
        )

    def refresh(self, project: Project) -> None:
        matrix = build_room_matrix(project)
        metrics = topic_metrics(project)
        rooms = [OUTDOOR_AREA_NAME, *project.rooms.keys()]
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
        pricing = estimate_project_costs(project)

        metric_lines = ["Themen-Metriken:"]
        for topic, m in metrics.items():
            metric_lines.append(
                f"• {topic}: Bereiche {m['rooms_with_selection']}/{m['room_count']} | "
                f"Diversity {m['diversity']} | Dominanz {m['dominant_ratio']:.2f}"
            )
        self.metrics_view.setPlainText("\n".join(metric_lines))

        network_lines = ["Netzwerk-Gesamtsumme:"]
        if not net["client_ports_by_room"] and not net["ap_count_by_room"] and net["outdoor_poe_devices"] == 0:
            network_lines.append("• Noch keine LAN-/AP-Angaben je Raum erfasst.")
        else:
            network_lines.append("\nLAN-Dosen / Client-Kabel je Raum:")
            if not net["client_ports_by_room"]:
                network_lines.append("• Keine LAN-Dosen geplant")
            else:
                for room, amount in net["client_ports_by_room"].items():
                    network_lines.append(f"• {room}: {amount} Port(s)")

            network_lines.append("\nAccess Points (PoE) je Raum:")
            if not net["ap_count_by_room"]:
                network_lines.append("• Keine APs geplant")
            else:
                for room, amount in net["ap_count_by_room"].items():
                    network_lines.append(f"• {room}: {amount} AP(s)")

            network_lines.append("\nAußenbereich (PoE):")
            network_lines.append(f"• Außenkameras: {net['outdoor_camera_count']}")
            network_lines.append(f"• Smarte Türklingeln: {net['outdoor_doorbell_count']}")
            network_lines.append(f"• Outdoor-APs: {net['outdoor_ap_count']}")
            network_lines.append(f"• PoE-Geräte außen gesamt: {net['outdoor_poe_devices']}")

            network_lines.append("\nSummen:")
            network_lines.append(f"• LAN-Dosen/Client-Kabel: {net['total_client_ports']}")
            network_lines.append(f"• APs innen: {net['total_ap_count']}")
            network_lines.append(f"• AP/PoE-Kabel gesamt (innen + außen): {net['total_ap_poe_cables']}")
            network_lines.append(f"• Gesamtkabel (Dosen + PoE): {net['total_cables']}")
            network_lines.append(f"• Reserve/Uplink pauschal: {net['reserve_uplink_ports']} Ports")
            network_lines.append(f"• Empfehlung inkl. Reserve/Uplink: {net['ports_with_overhead']} Ports")
            network_lines.append(f"• Empfohlene Switch-Größe: {net['recommended_switch']}")
            if net["split_recommended"]:
                network_lines.append("• Hinweis: Wegen hoher Port-/PoE-Last wird ein Switch-Split empfohlen.")
                network_lines.append(
                    f"  - PoE-Switch: {net['split_plan']['poe_switch']} ({net['split_plan']['poe_ports']} Ports inkl. Reserve)"
                )
                network_lines.append(
                    f"  - Non-PoE-Switch: {net['split_plan']['client_switch']} ({net['split_plan']['client_ports']} Ports inkl. Reserve)"
                )
        self.network_view.setPlainText("\n".join(network_lines))

        score_lines = ["Raum-Ampeln:"]
        score_order = [OUTDOOR_AREA_NAME, *project.rooms.keys()]
        for room in score_order:
            s = scores.get(room)
            if not s:
                continue
            score_lines.append(f"• {room}: {s['ampel']} ({s['value']}) | Konflikte: {s['conflicts']}")
        self.score_view.setPlainText("\n".join(score_lines))

        conflict_lines = ["Konfliktliste:"]
        if not conflicts:
            conflict_lines.append("• Keine Konflikte gefunden")
        else:
            for room, items in conflicts.items():
                conflict_lines.append(f"\n{room}:")
                for item in items:
                    conflict_lines.append(f"• {item}")
        self.conflicts_view.setPlainText("\n".join(conflict_lines))

        cost_lines = ["Kostenschätzung (Richtwerte):"]
        if pricing["switch_split_active"]:
            cost_lines.append("• Switch-Strategie: Split aktiv (PoE + Non-PoE)")
        else:
            cost_lines.append("• Switch-Strategie: Einzelswitch")
        if not pricing["line_items"]:
            cost_lines.append("• Noch keine relevanten Komponenten ausgewählt.")
        else:
            for item in pricing["line_items"]:
                c = item["cost"]
                cost_lines.append(
                    f"• {item['category']} ({item['quantity']}x): {item['description']} | "
                    f"{c['min']:.0f}€ / {c['typical']:.0f}€ / {c['max']:.0f}€ (min/typ/max)"
                )

            t = pricing["totals"]
            cost_lines.append("\nGesamt:")
            cost_lines.append(f"• Min: {t['min']:.0f}€")
            cost_lines.append(f"• Typisch: {t['typical']:.0f}€")
            cost_lines.append(f"• Max: {t['max']:.0f}€")

        cost_lines.append("\nAnnahmen:")
        for assumption in pricing["assumptions"]:
            cost_lines.append(f"• {assumption}")
        self.cost_view.setPlainText("\n".join(cost_lines))
