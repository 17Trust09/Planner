from __future__ import annotations

import json
from pathlib import Path
from typing import List

from app.models.project import Project

DATA_DIR = Path("data")
PROJECTS_DIR = DATA_DIR / "projects"
INDEX_FILE = DATA_DIR / "projects_index.json"


def ensure_storage() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text("[]", encoding="utf-8")


def list_projects() -> List[dict]:
    ensure_storage()
    try:
        return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def update_index(name: str, path: Path) -> None:
    entries = [e for e in list_projects() if e.get("path") != str(path)]
    entries.append({"name": name, "path": str(path)})
    INDEX_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def save_project(project: Project, path: Path) -> None:
    ensure_storage()
    project.touch()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(project.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    update_index(project.metadata.project_name, path)


def load_project(path: Path) -> Project:
    if not path.exists():
        raise FileNotFoundError(f"Projektdatei nicht gefunden: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Ungültiges JSON: {exc}") from exc
    return Project.from_dict(data)
