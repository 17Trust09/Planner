from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import GLOBAL_TOPICS, ROOM_TOPICS
from app.models.project import Project, RoomData, TopicState, create_empty_project
from app.services.import_excel import import_project_from_excel
from app.services.storage import (
    PROJECTS_DIR,
    list_projects,
    load_project,
    remove_project,
    rename_project_in_index,
    save_project,
)
from app.services.topic_visibility import is_room_topic_applicable
from app.services.validation import validate_required_fields
from app.ui.export_worker import ExportWorker
from app.ui.pages.evaluation_page import EvaluationPage
from app.ui.pages.rooms_page import RoomsPage
from app.ui.pages.start_page import StartPage
from app.ui.pages.topic_page import TopicPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smarthome Planungsmappe")
        self.resize(1500, 900)

        self.current_project: Project = create_empty_project("Neues Projekt")
        self.current_path: Path | None = None
        self.export_thread: QThread | None = None
        self.export_dialog: QProgressDialog | None = None

        root = QWidget()
        root_layout = QHBoxLayout(root)

        nav_layout = QVBoxLayout()
        self.btn_new = QPushButton("Neues Projekt")
        self.btn_save = QPushButton("Speichern")
        self.btn_save_as = QPushButton("Speichern unter")
        self.btn_import_xlsx = QPushButton("Import Excel")
        self.btn_export_xlsx = QPushButton("Export Excel")
        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_status = QPushButton("Status: Entwurf")
        self.nav = QListWidget()

        for b in [self.btn_new, self.btn_save, self.btn_save_as, self.btn_import_xlsx, self.btn_export_xlsx, self.btn_export_pdf, self.btn_status]:
            nav_layout.addWidget(b)
        nav_layout.addWidget(self.nav)

        self.stack = QStackedWidget()
        root_layout.addLayout(nav_layout, 1)
        root_layout.addWidget(self.stack, 5)
        self.setCentralWidget(root)

        self.start_page = StartPage()
        self.start_page.load_requested.connect(self._load_from_start)
        self.start_page.delete_requested.connect(self._delete_project)
        self.start_page.rename_requested.connect(self._rename_project)
        self.rooms_page = RoomsPage()
        self.rooms_page.rooms_changed.connect(self._on_rooms_changed)
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
        self.nav.addItem("Räume")
        self.nav.addItem("Auswertung")

        grouped: dict[str, list[str]] = {}
        for room in self.current_project.rooms.values():
            grouped.setdefault(room.floor, []).append(room.name)

        for floor in sorted(grouped.keys()):
            self.nav.addItem(f"-- {floor} --")
            for room_name in sorted(grouped[floor]):
                self.nav.addItem(room_name)
        self.nav.setCurrentRow(0)

    def _build_pages(self) -> None:
        self.stack.addWidget(self.start_page)
        self.global_page = TopicPage("Global_Planung", GLOBAL_TOPICS, self.current_project.global_topics)
        self.global_page.changed.connect(self._on_project_changed)
        self.stack.addWidget(self.global_page)

        room_config_data = {
            room.name: {"floor": room.floor, "room_type": room.room_type}
            for room in self.current_project.rooms.values()
        }
        self.rooms_page.set_rooms(room_config_data)
        self.stack.addWidget(self.rooms_page)

        self.stack.addWidget(self.eval_page)
        for room_name in self.current_project.rooms.keys():
            room = self.current_project.rooms[room_name]
            visible_topics = [topic for topic in ROOM_TOPICS if is_room_topic_applicable(self.current_project, room, topic)]
            page = TopicPage(f"{room_name} ({room.floor})", visible_topics, self.current_project.rooms[room_name].topics)
            page.changed.connect(self._on_project_changed)
            self.room_pages[room_name] = page
            self.stack.addWidget(page)
        self.eval_page.refresh(self.current_project)

    def _bind_events(self) -> None:
        self.nav.currentRowChanged.connect(self._navigate)
        self.btn_new.clicked.connect(self._new_project)
        self.btn_save.clicked.connect(self._save_project)
        self.btn_save_as.clicked.connect(self._save_project_as)
        self.btn_import_xlsx.clicked.connect(self._import_excel)
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
        if text == "Räume":
            self.stack.setCurrentWidget(self.rooms_page)
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
        self.start_page.delete_requested.connect(self._delete_project)
        self.start_page.rename_requested.connect(self._rename_project)
        self.rooms_page = RoomsPage()
        self.rooms_page.rooms_changed.connect(self._on_rooms_changed)
        self.eval_page = EvaluationPage()
        self._build_navigation()
        self._build_pages()
        self.refresh_start()

    def _persist_all_pages(self) -> None:
        self.global_page.persist()
        for page in self.room_pages.values():
            page.persist()

    def _on_project_changed(self) -> None:
        self.current_project.touch()

    def _on_rooms_changed(self) -> None:
        updated = self.rooms_page.get_rooms()
        existing = self.current_project.rooms

        new_rooms: dict[str, RoomData] = {}
        for room_name, info in updated.items():
            if room_name in existing:
                room = existing[room_name]
                room.floor = info["floor"]
                room.room_type = info.get("room_type", "other")
                new_rooms[room_name] = room
            else:
                new_rooms[room_name] = RoomData(
                    name=room_name,
                    floor=info["floor"],
                    room_type=info.get("room_type", "other"),
                    topics={topic.key: TopicState() for topic in ROOM_TOPICS},
                )

        self.current_project.rooms = new_rooms
        self.current_project.touch()
        self._rebuild_for_project()

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

    def _delete_project(self, path: str) -> None:
        remove_project(Path(path))
        if self.current_path and str(self.current_path) == path:
            self._new_project()
        self.refresh_start()

    def _rename_project(self, path: str, new_name: str) -> None:
        p = Path(path)
        if p.exists():
            proj = load_project(p)
            proj.metadata.project_name = new_name
            save_project(proj, p)
        rename_project_in_index(p, new_name)
        self.refresh_start()

    def refresh_start(self) -> None:
        self.start_page.set_projects(list_projects())
        self.btn_status.setText(f"Status: {self.current_project.metadata.status}")

    def _cycle_status(self) -> None:
        order = ["Entwurf", "Prüfung", "Freigegeben"]
        cur = self.current_project.metadata.status
        idx = order.index(cur) if cur in order else 0
        self.current_project.metadata.status = order[(idx + 1) % len(order)]
        self.btn_status.setText(f"Status: {self.current_project.metadata.status}")

    def _import_excel(self) -> None:
        source, _ = QFileDialog.getOpenFileName(self, "Excel importieren", "", "Excel (*.xlsx)")
        if not source:
            return
        try:
            imported = import_project_from_excel(Path(source), "Importiertes Projekt")
        except Exception as exc:
            QMessageBox.critical(self, "Importfehler", str(exc))
            return
        self.current_project = imported
        self.current_path = None
        self._rebuild_for_project()

    def _start_export(self, kind: str, target: Path) -> None:
        self.export_dialog = QProgressDialog("Export läuft...", None, 0, 0, self)
        self.export_dialog.setWindowTitle("Bitte warten")
        self.export_dialog.setCancelButton(None)
        self.export_dialog.show()

        self.export_thread = QThread()
        worker = ExportWorker(self.current_project, target, kind)
        worker.moveToThread(self.export_thread)
        self.export_thread.started.connect(worker.run)
        worker.finished.connect(self._on_export_finished)
        worker.failed.connect(self._on_export_failed)
        worker.finished.connect(self.export_thread.quit)
        worker.failed.connect(self.export_thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        self.export_thread.finished.connect(self.export_thread.deleteLater)
        self.export_thread.start()

    def _on_export_finished(self, target: str) -> None:
        if self.export_dialog:
            self.export_dialog.close()
        QMessageBox.information(self, "Export", f"Export erfolgreich: {target}")

    def _on_export_failed(self, message: str) -> None:
        if self.export_dialog:
            self.export_dialog.close()
        QMessageBox.critical(self, "Exportfehler", message)

    def _export_excel(self) -> None:
        self._persist_all_pages()
        errors = validate_required_fields(self.current_project)
        if errors:
            QMessageBox.warning(self, "Pflichtfelder fehlen", "\n".join(errors[:20]))
            return
        target, _ = QFileDialog.getSaveFileName(self, "Excel exportieren", "export.xlsx", "Excel (*.xlsx)")
        if target:
            self._start_export("excel", Path(target))

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
        if target:
            self._start_export("pdf", Path(target))
