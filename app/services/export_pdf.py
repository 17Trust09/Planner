from __future__ import annotations

from pathlib import Path
from typing import Callable
from xml.sax.saxutils import escape

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.definitions import GLOBAL_TOPICS, ROOM_TOPICS
from app.models.project import Project
from app.services.evaluation import room_score
from app.services.validation import detect_conflicts_detailed

DEFAULT_EMPTY = "N/A"
PAGE_CONTENT_WIDTH = 539


def _paragraph_text(value: str) -> str:
    safe = escape(value or DEFAULT_EMPTY)
    return safe.replace("\n", "<br/>")


def _cell(value: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_paragraph_text(value), style)


def _table(data, header_color: str, col_widths=None, compact: bool = False) -> Table:
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if compact:
        style.extend([
            ("FONTSIZE", (0, 0), (-1, -1), 8.2),
            ("LEADING", (0, 0), (-1, -1), 10),
        ])
    t.setStyle(TableStyle(style))
    return t


def _score_chart(scores: dict[str, dict]) -> Drawing:
    rooms = list(scores.keys())
    values = [max(0, min(100, int(scores[room].get("value", 0)))) for room in rooms]

    drawing = Drawing(PAGE_CONTENT_WIDTH, 220)
    drawing.add(String(10, 200, "Raum-Score Übersicht (0-100)", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor("#0F172A")))

    chart = VerticalBarChart()
    chart.x = 45
    chart.y = 35
    chart.height = 145
    chart.width = 470
    chart.data = [values]
    chart.strokeColor = colors.HexColor("#94A3B8")
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 20
    chart.valueAxis.strokeColor = colors.HexColor("#64748B")
    chart.valueAxis.labels.fontSize = 8
    chart.categoryAxis.categoryNames = [r[:14] for r in rooms]
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.angle = 25
    chart.categoryAxis.labels.dy = -8
    chart.bars[0].fillColor = colors.HexColor("#2563EB")
    chart.bars[0].strokeColor = colors.HexColor("#1D4ED8")
    chart.barSpacing = 3
    chart.groupSpacing = 8
    drawing.add(chart)
    return drawing


def _ampel_indicator(ampel: str, value: float) -> str:
    palette = {
        "gruen": ("#16A34A", "Grün"),
        "gelb": ("#CA8A04", "Gelb"),
        "rot": ("#DC2626", "Rot"),
    }
    tone, _ = palette.get(ampel, ("#64748B", "Unbekannt"))
    return f"Ampel-Status: <font color='{tone}'><b>●</b></font> &nbsp;&nbsp;Score: <b>{value}</b>"


def export_project_to_pdf(
    project: Project,
    target_file: Path,
    on_progress: Callable[[int, str], None] | None = None,
) -> None:
    def report(step: int, total: int, message: str) -> None:
        if on_progress:
            on_progress(int(step * 100 / total), message)

    room_count = len(project.rooms)
    total_steps = 6 + room_count
    step = 0

    target_file.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(target_file), pagesize=A4, leftMargin=28, rightMargin=28, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], textColor=colors.HexColor("#1E3A8A"), spaceAfter=8, spaceBefore=4)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], textColor=colors.HexColor("#0F172A"), leading=13)
    muted_style = ParagraphStyle("Muted", parent=styles["Normal"], textColor=colors.HexColor("#475569"), leading=12)
    table_cell_style = ParagraphStyle("TableCell", parent=styles["Normal"], fontSize=8.1, leading=10)

    flow = []
    step += 1
    report(step, total_steps, "PDF wird vorbereitet")

    flow.append(Paragraph("<b>Smarthome / IT / Elektrik Planungsreport</b>", styles["Title"]))
    flow.append(Paragraph(f"Projekt: <b>{escape(project.metadata.project_name)}</b>", styles["Heading3"]))
    flow.append(Paragraph(f"Status: {escape(project.metadata.status)} | Version: {escape(str(project.metadata.version))}", muted_style))
    flow.append(Paragraph(f"Erstellt: {escape(str(project.metadata.updated_at))}", muted_style))
    flow.append(Spacer(1, 10))

    scores = room_score(project)
    conflicts = detect_conflicts_detailed(project)

    total_conflicts = sum(len(c) for c in conflicts.values())
    room_values = [max(0, min(100, int(scores[r].get("value", 0)))) for r in scores]
    avg_score = round(sum(room_values) / len(room_values), 1) if room_values else 0.0
    kpi_data = [
        [_cell("Kennzahl", table_cell_style), _cell("Wert", table_cell_style)],
        [_cell("Räume gesamt", table_cell_style), _cell(str(len(project.rooms)), table_cell_style)],
        [_cell("Ø Raum-Score", table_cell_style), _cell(str(avg_score), table_cell_style)],
        [_cell("Konflikte erkannt", table_cell_style), _cell(str(total_conflicts), table_cell_style)],
    ]
    flow.append(_table(kpi_data, "#0F172A", col_widths=[260, 120], compact=True))
    flow.append(Spacer(1, 12))
    flow.append(_score_chart(scores))
    flow.append(Spacer(1, 12))
    step += 1
    report(step, total_steps, "Management-Übersicht wurde erstellt")

    flow.append(Paragraph("Globale Planung", section_style))
    flow.append(Paragraph("Übersicht aller globalen Entscheidungen und Verantwortlichkeiten.", muted_style))
    global_data = [[
        _cell("Sektion", table_cell_style),
        _cell("Thema", table_cell_style),
        _cell("Auswahl(en)", table_cell_style),
        _cell("Verantwortlich", table_cell_style),
        _cell("Notizen", table_cell_style),
    ]]
    for t in GLOBAL_TOPICS:
        s = project.global_topics[t.key]
        global_data.append([
            _cell(t.section, table_cell_style),
            _cell(t.title, table_cell_style),
            _cell(", ".join(s.selections) or DEFAULT_EMPTY, table_cell_style),
            _cell(s.assignee or DEFAULT_EMPTY, table_cell_style),
            _cell(s.notes or DEFAULT_EMPTY, table_cell_style),
        ])
    flow.append(_table(global_data, "#1D4ED8", col_widths=[78, 100, 165, 86, 110], compact=True))
    flow.append(PageBreak())
    step += 1
    report(step, total_steps, "Globale Inhalte wurden aufgebaut")

    open_points: list[str] = []
    for idx, (room_name, room) in enumerate(project.rooms.items()):
        flow.append(Paragraph(f"Raumprofil: {escape(room_name)}", section_style))
        score = scores[room_name]
        flow.append(Paragraph(_ampel_indicator(score["ampel"], score["value"]), body_style))
        flow.append(Spacer(1, 6))

        rows = [[
            _cell("Thema", table_cell_style),
            _cell("Auswahl(en)", table_cell_style),
            _cell("Verantwortlich", table_cell_style),
            _cell("Notizen", table_cell_style),
        ]]
        for t in ROOM_TOPICS:
            s = room.topics[t.key]
            rows.append([
                _cell(t.title, table_cell_style),
                _cell(", ".join(s.selections) or DEFAULT_EMPTY, table_cell_style),
                _cell(s.assignee or DEFAULT_EMPTY, table_cell_style),
                _cell(s.notes or DEFAULT_EMPTY, table_cell_style),
            ])
        flow.append(_table(rows, "#0F172A", col_widths=[100, 192, 92, 155], compact=True))

        if room_name in conflicts:
            flow.append(Spacer(1, 6))
            flow.append(Paragraph("Konflikte", styles["Heading4"]))
            conflict_rows = [[_cell("Priorität", table_cell_style), _cell("Beschreibung", table_cell_style)]]
            for c in conflicts[room_name]:
                severity = c["severity"].upper()
                msg = c["message"]
                conflict_rows.append([_cell(severity, table_cell_style), _cell(msg, table_cell_style)])
                open_points.append(f"{room_name}: [{severity}] {msg}")
            flow.append(_table(conflict_rows, "#B91C1C", col_widths=[80, 445], compact=True))

        if idx < room_count - 1:
            flow.append(PageBreak())

        step += 1
        report(step, total_steps, f"Raum '{room_name}' wurde verarbeitet")

    flow.append(PageBreak())
    flow.append(Paragraph("Offene Punkte", section_style))
    if not open_points:
        flow.append(Paragraph("Keine offenen Konfliktpunkte erkannt.", body_style))
    else:
        flow.append(Paragraph("Diese Punkte sollten vor Freigabe geklärt werden.", muted_style))
        todo_rows = [[_cell("Punkt", table_cell_style)]] + [[_cell(item, table_cell_style)] for item in open_points]
        flow.append(_table(todo_rows, "#7C3AED", col_widths=[525], compact=True))
    step += 1
    report(step, total_steps, "Offene Punkte wurden zusammengestellt")

    doc.build(flow)
    step += 1
    report(step, total_steps, "PDF-Datei wird gespeichert")
