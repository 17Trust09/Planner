from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from app.models.project import Project
from app.services.export_excel import export_project_to_excel
from app.services.export_pdf import export_project_to_pdf


class ExportWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, project: Project, target: Path, kind: str):
        super().__init__()
        self.project = project
        self.target = target
        self.kind = kind

    def run(self) -> None:
        try:
            if self.kind == "excel":
                export_project_to_excel(self.project, self.target)
            elif self.kind == "pdf":
                export_project_to_pdf(self.project, self.target)
            else:
                raise ValueError("Unbekannter Exporttyp")
            self.finished.emit(str(self.target))
        except Exception as exc:
            self.failed.emit(str(exc))
