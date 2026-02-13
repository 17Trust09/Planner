from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.models.project import Project
from app.services.export_excel import export_project_to_excel
from app.services.export_pdf import export_project_to_pdf


class ExportWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)
    progress = Signal(int, str, str)

    def __init__(self, project: Project, target: Path, kind: str):
        super().__init__()
        self.project = project
        self.target = target
        self.kind = kind

    def run(self) -> None:
        try:
            started_at = time.monotonic()

            def on_progress(percent: int, message: str) -> None:
                percent = max(0, min(100, percent))
                eta_text = "Dauer wird berechnet..."
                if percent > 0:
                    elapsed = time.monotonic() - started_at
                    remaining = max(0.0, elapsed * (100 - percent) / percent)
                    eta_text = f"ca. {int(round(remaining))}s verbleibend"
                self.progress.emit(percent, message, eta_text)

            on_progress(0, "Export startet...")
            if self.kind == "excel":
                export_project_to_excel(self.project, self.target, on_progress)
            elif self.kind == "pdf":
                export_project_to_pdf(self.project, self.target, on_progress)
            else:
                raise ValueError("Unbekannter Exporttyp")
            on_progress(100, "Export abgeschlossen")
            self.finished.emit(str(self.target))
        except Exception as exc:
            self.failed.emit(str(exc))
