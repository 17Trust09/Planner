from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.definitions import GLOBAL_TOPICS, ROOM_TOPICS
from app.models.project import Project
from app.services.evaluation import room_score
from app.services.validation import detect_conflicts


def export_project_to_pdf(project: Project, target_file: Path) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(target_file), pagesize=A4)
    styles = getSampleStyleSheet()
    flow = []

    flow.append(Paragraph(f"<b>Smarthome Planungsmappe</b>", styles["Title"]))
    flow.append(Paragraph(f"Projekt: {project.metadata.project_name}", styles["Heading2"]))
    flow.append(Paragraph(f"Status: {project.metadata.status} | Version: {project.metadata.version}", styles["Normal"]))
    flow.append(Spacer(1, 12))

    flow.append(Paragraph("<b>Global Planung</b>", styles["Heading3"]))
    global_data = [["Thema", "Auswahl(en)", "Verantwortlich", "Notizen"]]
    for t in GLOBAL_TOPICS:
        s = project.global_topics[t.key]
        global_data.append([t.title, ", ".join(s.selections) or "—", s.assignee or "—", s.notes or "—"])
    gt = Table(global_data, repeatRows=1)
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D4ED8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    flow.append(gt)
    flow.append(Spacer(1, 12))

    scores = room_score(project)
    conflicts = detect_conflicts(project)
    for room_name, room in project.rooms.items():
        flow.append(Paragraph(f"<b>Raum: {room_name}</b>", styles["Heading3"]))
        score = scores[room_name]
        flow.append(Paragraph(f"Ampel-Score: {score['ampel']} ({score['value']})", styles["Normal"]))
        rows = [["Thema", "Auswahl(en)", "Verantwortlich", "Notizen"]]
        for t in ROOM_TOPICS:
            s = room.topics[t.key]
            rows.append([t.title, ", ".join(s.selections) or "—", s.assignee or "—", s.notes or "—"])
        tb = Table(rows, repeatRows=1)
        tb.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        flow.append(tb)
        if room_name in conflicts:
            flow.append(Paragraph("Konflikte:", styles["Normal"]))
            for c in conflicts[room_name]:
                flow.append(Paragraph(f"• {c}", styles["Normal"]))
        flow.append(Spacer(1, 10))

    doc.build(flow)
