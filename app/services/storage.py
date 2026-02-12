from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.models.project import Project
from app.services.change_log import build_change_log, write_change_log

DATA_DIR = Path("data")
PROJECTS_DIR = DATA_DIR / "projects"
INDEX_FILE = DATA_DIR / "projects_index.json"
CHANGES_DIR = DATA_DIR / "changes"


def ensure_storage() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    CHANGES_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text("[]", encoding="utf-8")


def list_projects() -> List[dict]:
    ensure_storage()
    try:
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _write_index(entries: List[dict]) -> None:
    INDEX_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def update_index(name: str, path: Path) -> None:
    entries = [e for e in list_projects() if e.get("path") != str(path)]
    entries.append({"name": name, "path": str(path)})
    _write_index(entries)


def rename_project_in_index(path: Path, new_name: str) -> None:
    entries = list_projects()
    for item in entries:
        if item.get("path") == str(path):
            item["name"] = new_name
    _write_index(entries)


def remove_project(path: Path) -> None:
    if path.exists():
        path.unlink()
    entries = [e for e in list_projects() if e.get("path") != str(path)]
    _write_index(entries)


def save_project(project: Project, path: Path) -> None:
    ensure_storage()
    previous = None
    if path.exists():
        try:
            previous = load_project(path)
        except Exception:
            previous = None
    project.touch()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(project.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    update_index(project.metadata.project_name, path)
    if previous is not None:
        changes = build_change_log(previous, project)
        if changes:
            change_file = CHANGES_DIR / f"{path.stem}_changes.txt"
            write_change_log(change_file, changes)


def load_project(path: Path) -> Project:
    if not path.exists():
        raise FileNotFoundError(f"Projektdatei nicht gefunden: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ungültiges JSON: {exc}") from exc
    return Project.from_dict(data)
