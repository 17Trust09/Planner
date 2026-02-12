from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import FLOORS, GLOBAL_TOPICS, ROOM_TOPICS
from app.models.project import Project, create_empty_project
from app.services.export_excel import export_project_to_excel
from app.services.export_pdf import export_project_to_pdf
from app.services.storage import PROJECTS_DIR, list_projects, load_project, save_project
from app.services.validation import validate_required_fields
from app.ui.pages.evaluation_page import EvaluationPage
from app.ui.pages.start_page import StartPage
from app.ui.pages.topic_page import TopicPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smarthome Planungsmappe")
        self.resize(1500, 900)

        self.current_project: Project = create_empty_project("Neues Projekt")
        self.current_path: Path | None = None

        root = QWidget()
        root_layout = QHBoxLayout(root)

        nav_layout = QVBoxLayout()
        self.btn_new = QPushButton("Neues Projekt")
        self.btn_save = QPushButton("Speichern")
        self.btn_save_as = QPushButton("Speichern unter")
        self.btn_export_xlsx = QPushButton("Export Excel")
        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_status = QPushButton("Status: Entwurf")
        self.nav = QListWidget()

        nav_layout.addWidget(self.btn_new)
        nav_layout.addWidget(self.btn_save)
        nav_layout.addWidget(self.btn_save_as)
        nav_layout.addWidget(self.btn_export_xlsx)
        nav_layout.addWidget(self.btn_export_pdf)
        nav_layout.addWidget(self.btn_status)
        nav_layout.addWidget(self.nav)

        self.stack = QStackedWidget()
        root_layout.addLayout(nav_layout, 1)
        root_layout.addWidget(self.stack, 5)
        self.setCentralWidget(root)

        self.start_page = StartPage()
        self.start_page.load_requested.connect(self._load_from_start)
        self.eval_page = EvaluationPage()

        self.room_pages: dict[str, TopicPage] = {}

        self._build_navigation()
        self._build_pages()
        self._bind_events()
        self.refresh_start()

    def _build_navigation(self) -> None:
        self.nav.clear()
        self.nav.addItem("Start")
        self.nav.addItem("Global")
        self.nav.addItem("Auswertung")
        for floor, rooms in FLOORS.items():
            self.nav.addItem(f"-- {floor} --")
            for room in rooms:
                self.nav.addItem(room)
        self.nav.setCurrentRow(0)

    def _build_pages(self) -> None:
        self.stack.addWidget(self.start_page)
        self.global_page = TopicPage("Global_Planung", GLOBAL_TOPICS, self.current_project.global_topics)
        self.global_page.changed.connect(self._on_project_changed)
        self.stack.addWidget(self.global_page)
        self.stack.addWidget(self.eval_page)
        for room_name in self.current_project.rooms.keys():
            page = TopicPage(room_name, ROOM_TOPICS, self.current_project.rooms[room_name].topics)
            page.changed.connect(self._on_project_changed)
            self.room_pages[room_name] = page
            self.stack.addWidget(page)
        self.eval_page.refresh(self.current_project)

    def _bind_events(self) -> None:
        self.nav.currentRowChanged.connect(self._navigate)
        self.btn_new.clicked.connect(self._new_project)
        self.btn_save.clicked.connect(self._save_project)
        self.btn_save_as.clicked.connect(self._save_project_as)
        self.btn_export_xlsx.clicked.connect(self._export_excel)
        self.btn_export_pdf.clicked.connect(self._export_pdf)
        self.btn_status.clicked.connect(self._cycle_status)

    def _navigate(self, row: int) -> None:
        text = self.nav.item(row).text()
        if text.startswith("--"):
            return
        if text == "Start":
            self.stack.setCurrentWidget(self.start_page)
            return
        if text == "Global":
            self.stack.setCurrentWidget(self.global_page)
            return
        if text == "Auswertung":
            self._persist_all_pages()
            self.eval_page.refresh(self.current_project)
            self.stack.setCurrentWidget(self.eval_page)
            return
        page = self.room_pages.get(text)
        if page:
            self.stack.setCurrentWidget(page)

    def _new_project(self) -> None:
        self.current_project = create_empty_project("Projekt Neu")
        self.current_path = None
        self._rebuild_for_project()

    def _rebuild_for_project(self) -> None:
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        self.room_pages.clear()
        self.start_page = StartPage()
        self.start_page.load_requested.connect(self._load_from_start)
        self.eval_page = EvaluationPage()
        self._build_pages()
        self.refresh_start()

    def _persist_all_pages(self) -> None:
        self.global_page.persist()
        for page in self.room_pages.values():
            page.persist()

    def _on_project_changed(self) -> None:
        # Kein Full-Reload: Änderungen bleiben lokal auf der aktiven Seite.
        self.current_project.touch()

    def _save_project(self) -> None:
        self._persist_all_pages()
        if self.current_path is None:
            self._save_project_as()
            return
        save_project(self.current_project, self.current_path)
        self.refresh_start()

    def _save_project_as(self) -> None:
        self._persist_all_pages()
        target, _ = QFileDialog.getSaveFileName(self, "Projekt speichern", str(PROJECTS_DIR / "projekt.json"), "JSON (*.json)")
        if not target:
            return
        self.current_path = Path(target)
        save_project(self.current_project, self.current_path)
        self.refresh_start()

    def _load_from_start(self, path: str) -> None:
        try:
            self.current_project = load_project(Path(path))
        except (FileNotFoundError, ValueError) as exc:
            QMessageBox.critical(self, "Fehler", str(exc))
            return
        self.current_path = Path(path)
        self._rebuild_for_project()

    def refresh_start(self) -> None:
        self.start_page.set_projects(list_projects())
        self.btn_status.setText(f"Status: {self.current_project.metadata.status}")


    def _cycle_status(self) -> None:
        order = ["Entwurf", "Prüfung", "Freigegeben"]
        cur = self.current_project.metadata.status
        idx = order.index(cur) if cur in order else 0
        self.current_project.metadata.status = order[(idx + 1) % len(order)]
        self.btn_status.setText(f"Status: {self.current_project.metadata.status}")

    def _export_excel(self) -> None:
        self._persist_all_pages()
        errors = validate_required_fields(self.current_project)
        if errors:
            QMessageBox.warning(self, "Pflichtfelder fehlen", "\n".join(errors[:20]))
            return
        target, _ = QFileDialog.getSaveFileName(self, "Excel exportieren", "export.xlsx", "Excel (*.xlsx)")
        if not target:
            return
        export_project_to_excel(self.current_project, Path(target))

    def _export_pdf(self) -> None:
        self._persist_all_pages()
        errors = validate_required_fields(self.current_project)
        if errors:
            QMessageBox.warning(self, "Pflichtfelder fehlen", "\n".join(errors[:20]))
            return
        if self.current_project.metadata.status != "Freigegeben":
            QMessageBox.warning(self, "Status", "PDF Export nur im Status 'Freigegeben'.")
            return
        target, _ = QFileDialog.getSaveFileName(self, "PDF exportieren", "report.pdf", "PDF (*.pdf)")
        if not target:
            return
        export_project_to_pdf(self.current_project, Path(target))
