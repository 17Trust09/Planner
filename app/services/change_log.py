from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from app.models.project import Project


def _topic_changes(before: Dict[str, dict], after: Dict[str, dict], prefix: str) -> List[str]:
    changes: List[str] = []
    keys = sorted(set(before.keys()) | set(after.keys()))
    for key in keys:
        b = before.get(key, {})
        a = after.get(key, {})
        b_sel = b.get("selections", [])
        a_sel = a.get("selections", [])
        if b_sel != a_sel:
            changes.append(f"{prefix}.{key}.selections: {b_sel} -> {a_sel}")
        if b.get("notes", "") != a.get("notes", ""):
            changes.append(f"{prefix}.{key}.notes geändert")
        if b.get("assignee", "") != a.get("assignee", ""):
            changes.append(f"{prefix}.{key}.assignee: '{b.get('assignee', '')}' -> '{a.get('assignee', '')}'")
    return changes


def build_change_log(previous: Project, current: Project) -> List[str]:
    changes: List[str] = []
    if previous.metadata.status != current.metadata.status:
        changes.append(f"metadata.status: {previous.metadata.status} -> {current.metadata.status}")
    prev_global = {k: asdict(v) for k, v in previous.global_topics.items()}
    curr_global = {k: asdict(v) for k, v in current.global_topics.items()}
    changes.extend(_topic_changes(prev_global, curr_global, "global"))
    for room_name, room in current.rooms.items():
        prev_room = previous.rooms.get(room_name)
        if not prev_room:
            changes.append(f"room.{room_name}: neu")
            continue
        prev_topics = {k: asdict(v) for k, v in prev_room.topics.items()}
        room_topics = {k: asdict(v) for k, v in room.topics.items()}
        changes.extend(_topic_changes(prev_topics, room_topics, f"room.{room_name}"))
    return changes


def write_change_log(path: Path, changes: List[str]) -> None:
    if not changes:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(changes), encoding="utf-8")
