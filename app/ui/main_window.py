from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.definitions import FLOORS, GLOBAL_TOPICS, ROOM_TOPICS
from app.models.project import Project, create_empty_project
from app.services.export_excel import export_project_to_excel
from app.services.export_pdf import export_project_to_pdf
from app.services.storage import PROJECTS_DIR, list_projects, load_project, save_project
from app.services.validation import MissingRequiredField, required_field_entries
from app.ui.pages.evaluation_page import EvaluationPage
from app.ui.pages.start_page import StartPage
from app.ui.pages.topic_page import TopicPage


class MissingFieldsDialog(QDialog):
    def __init__(self, missing: list[MissingRequiredField], parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Pflichtfelder fehlen")
        self.resize(600, 380)
        self.selected: MissingRequiredField | None = None
        self.action: str = "cancel"

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Folgende Pflichtfelder fehlen. Du kannst direkt hinspringen oder trotzdem exportieren:"))

        self.list_widget = QListWidget()
        for item in missing:
            text = f"Global: {item.topic_title}" if item.scope == "global" else f"Raum {item.room_name}: {item.topic_title}"
            entry = QListWidgetItem(text)
            entry.setData(Qt.UserRole, item)
            self.list_widget.addItem(entry)
        layout.addWidget(self.list_widget)

        self.buttons = QDialogButtonBox()
        self.jump_btn = self.buttons.addButton("Zum Feld springen", QDialogButtonBox.AcceptRole)
        self.ignore_btn = self.buttons.addButton("Ignorieren und exportieren", QDialogButtonBox.DestructiveRole)
        self.buttons.addButton("Abbrechen", QDialogButtonBox.RejectRole)
        layout.addWidget(self.buttons)

        self.jump_btn.clicked.connect(self._accept_selected)
        self.ignore_btn.clicked.connect(self._accept_ignore)
        self.buttons.rejected.connect(self.reject)
        self.list_widget.itemDoubleClicked.connect(lambda _: self._accept_selected())

    def _accept_selected(self) -> None:
        current = self.list_widget.currentItem()
        if current is None and self.list_widget.count() > 0:
            current = self.list_widget.item(0)
        if current is None:
            return
        self.selected = current.data(Qt.UserRole)
        self.action = "jump"
        self.accept()

    def _accept_ignore(self) -> None:
        self.action = "ignore"
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smarthome Planungsmappe")
        self.resize(1500, 900)

        self.current_project: Project = create_empty_project("Neues Projekt")
        self.current_path: Path | None = None

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        nav_layout = QVBoxLayout(sidebar)
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(8)

        self.lbl_project_info = QLabel()
        self.lbl_project_info.setObjectName("projectInfo")
        self.lbl_project_info.setWordWrap(True)

        self.btn_new = QPushButton("Neues Projekt")
        self.btn_save = QPushButton("Speichern")
        self.btn_save_as = QPushButton("Speichern unter")
        self.btn_export_xlsx = QPushButton("Export Excel")
        self.btn_export_pdf = QPushButton("Export PDF")
        self.nav = QTreeWidget()
        self.nav.setHeaderHidden(True)
        self.nav.setObjectName("navTree")
        self.btn_nav_help = QPushButton("Navigation ?")
        self.btn_nav_help.setObjectName("secondaryButton")

        nav_layout.addWidget(self.lbl_project_info)
        for button in [self.btn_new, self.btn_save, self.btn_save_as, self.btn_export_xlsx, self.btn_export_pdf]:
            button.setObjectName("primaryButton")
            nav_layout.addWidget(button)

        nav_layout.addWidget(self.btn_nav_help)
        nav_layout.addWidget(self.nav, 1)

        self.content_panel = QFrame()
        self.content_panel.setObjectName("contentPanel")
        content_layout = QVBoxLayout(self.content_panel)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(0)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)

        sidebar.setMinimumWidth(220)
        self.content_panel.setMinimumWidth(420)

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.addWidget(sidebar)
        self.main_splitter.addWidget(self.content_panel)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([320, 1180])

        root_layout.addWidget(self.main_splitter)
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

        overview = QTreeWidgetItem(["Projektübersicht"])
        overview.setFlags(overview.flags() & ~Qt.ItemIsSelectable)
        self.nav.addTopLevelItem(overview)
        start_item = QTreeWidgetItem(["Start"])
        start_item.setData(0, Qt.UserRole, "start")
        overview.addChild(start_item)
        global_item = QTreeWidgetItem(["Global"])
        global_item.setData(0, Qt.UserRole, "global")
        overview.addChild(global_item)
        evaluation_item = QTreeWidgetItem(["Auswertung"])
        evaluation_item.setData(0, Qt.UserRole, "evaluation")
        overview.addChild(evaluation_item)

        rooms_root = QTreeWidgetItem(["Räume nach Etage"])
        rooms_root.setFlags(rooms_root.flags() & ~Qt.ItemIsSelectable)
        self.nav.addTopLevelItem(rooms_root)

        for floor, rooms in FLOORS.items():
            floor_item = QTreeWidgetItem([floor])
            floor_item.setFlags(floor_item.flags() & ~Qt.ItemIsSelectable)
            rooms_root.addChild(floor_item)
            for room in rooms:
                room_item = QTreeWidgetItem([room])
                room_item.setData(0, Qt.UserRole, room)
                floor_item.addChild(room_item)

        self.nav.expandAll()
        self.nav.setCurrentItem(start_item)

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
        self.nav.currentItemChanged.connect(self._navigate)
        self.btn_new.clicked.connect(self._new_project)
        self.btn_save.clicked.connect(self._save_project)
        self.btn_save_as.clicked.connect(self._save_project_as)
        self.btn_export_xlsx.clicked.connect(self._export_excel)
        self.btn_export_pdf.clicked.connect(self._export_pdf)
        self.btn_nav_help.clicked.connect(self._show_nav_help)

    def _show_nav_help(self) -> None:
        QMessageBox.information(
            self,
            "Hilfe: Navigation",
            "Projektübersicht enthält Start, globale Einstellungen und Auswertung.\n"
            "Unter 'Räume nach Etage' findest du alle Räume logisch nach EG/OG gruppiert.\n"
            "In jeder Frage kannst du über das '?' die Bedeutung der Auswahl sehen.",
        )

    def _clear_missing_marks(self) -> None:
        self.global_page.clear_all_missing()
        for page in self.room_pages.values():
            page.clear_all_missing()

    def _handle_missing_required_fields(self, missing: list[MissingRequiredField]) -> bool:
        self._clear_missing_marks()
        for field in missing:
            if field.scope == "global":
                self.global_page.mark_missing(field.topic_key, True)
            elif field.room_name and field.room_name in self.room_pages:
                self.room_pages[field.room_name].mark_missing(field.topic_key, True)

        dialog = MissingFieldsDialog(missing, self)
        if dialog.exec() != QDialog.Accepted:
            return False

        if dialog.action == "ignore":
            return True

        if dialog.action == "jump" and dialog.selected:
            field = dialog.selected
            if field.scope == "global":
                self.stack.setCurrentWidget(self.global_page)
                self.global_page.focus_topic(field.topic_key)
            elif field.room_name and field.room_name in self.room_pages:
                page = self.room_pages[field.room_name]
                self.stack.setCurrentWidget(page)
                page.focus_topic(field.topic_key)
        return False

    def _navigate(self, item: QTreeWidgetItem | None, _: QTreeWidgetItem | None = None) -> None:
        if item is None:
            return

        key = item.data(0, Qt.UserRole)
        if key == "start":
            self.stack.setCurrentWidget(self.start_page)
            return
        if key == "global":
            self.stack.setCurrentWidget(self.global_page)
            return
        if key == "evaluation":
            self._persist_all_pages()
            self.eval_page.refresh(self.current_project)
            self.stack.setCurrentWidget(self.eval_page)
            return
        if isinstance(key, str):
            page = self.room_pages.get(key)
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
        project_name = self.current_project.metadata.project_name or "Unbenanntes Projekt"
        file_name = self.current_path.name if self.current_path else "(noch nicht gespeichert)"
        self.lbl_project_info.setText(f"Aktuelles Projekt:\n{project_name}\nDatei: {file_name}")

    def _export_excel(self) -> None:
        self._persist_all_pages()
        missing = required_field_entries(self.current_project)
        if missing and not self._handle_missing_required_fields(missing):
            return
        target, _ = QFileDialog.getSaveFileName(self, "Excel exportieren", "export.xlsx", "Excel (*.xlsx)")
        if not target:
            return
        export_project_to_excel(self.current_project, Path(target))
        self._clear_missing_marks()

    def _export_pdf(self) -> None:
        self._persist_all_pages()
        missing = required_field_entries(self.current_project)
        if missing and not self._handle_missing_required_fields(missing):
            return
        target, _ = QFileDialog.getSaveFileName(self, "PDF exportieren", "report.pdf", "PDF (*.pdf)")
        if not target:
            return
        export_project_to_pdf(self.current_project, Path(target))
        self._clear_missing_marks()
