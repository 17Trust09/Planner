from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.definitions import GLOBAL_TOPICS, OUTDOOR_AREA_NAME, OUTDOOR_TOPICS, ROOM_TOPICS
from app.models.project import Project
from app.services.evaluation import room_score
from app.services.validation import detect_conflicts


def _floor_plan_image_bytes(floor_data: dict) -> bytes | None:
    image_data = floor_data.get("image_data")
    if image_data:
        try:
            return base64.b64decode(str(image_data), validate=True)
        except (ValueError, TypeError):
            pass

    image_path = floor_data.get("image_path")
    if image_path:
        try:
            return Path(str(image_path)).read_bytes()
        except OSError:
            return None
    return None


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

    flow.append(Paragraph(f"<b>{OUTDOOR_AREA_NAME}</b>", styles["Heading3"]))
    outdoor_data = [["Thema", "Auswahl(en)", "Verantwortlich", "Notizen"]]
    for t in OUTDOOR_TOPICS:
        s = project.outdoor_topics[t.key]
        outdoor_data.append([t.title, ", ".join(s.selections) or "—", s.assignee or "—", s.notes or "—"])
    ot = Table(outdoor_data, repeatRows=1)
    ot.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    flow.append(ot)

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


    if project.floor_plans:
        flow.append(Spacer(1, 12))
        flow.append(Paragraph("<b>Grundrisse</b>", styles["Heading3"]))
        for floor, floor_data in sorted(project.floor_plans.items()):
            if not isinstance(floor_data, dict):
                continue
            placements = floor_data.get("placements", [])
            flow.append(Paragraph(f"Etage: {floor} | Marker: {len(placements)}", styles["Normal"]))

            img_bytes = _floor_plan_image_bytes(floor_data)
            if img_bytes:
                try:
                    img = Image(BytesIO(img_bytes))
                    max_w = 480
                    max_h = 280
                    scale = min(max_w / img.imageWidth, max_h / img.imageHeight, 1.0)
                    img.drawWidth = img.imageWidth * scale
                    img.drawHeight = img.imageHeight * scale
                    flow.append(img)
                except Exception:
                    flow.append(Paragraph("(Grundrissbild konnte im PDF nicht eingebettet werden)", styles["Normal"]))

            if placements:
                marker_lines = [
                    f"• {p.get('label', 'Marker')} @ ({round(float(p.get('x', 0))*100)}%, {round(float(p.get('y', 0))*100)}%)"
                    for p in placements
                ]
                for line in marker_lines[:20]:
                    flow.append(Paragraph(line, styles["Normal"]))
                if len(marker_lines) > 20:
                    flow.append(Paragraph(f"… +{len(marker_lines)-20} weitere Marker", styles["Normal"]))
            flow.append(Spacer(1, 8))

    doc.build(flow)
