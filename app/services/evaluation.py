from __future__ import annotations

from collections import Counter
from typing import Dict, List

from app.models.definitions import ROOM_TOPICS
from app.models.project import Project
from app.services.validation import detect_conflicts


def build_room_matrix(project: Project) -> Dict[str, Dict[str, List[str]]]:
    matrix: Dict[str, Dict[str, List[str]]] = {}
    for topic in ROOM_TOPICS:
        matrix[topic.title] = {}
        for room_name, room in project.rooms.items():
            matrix[topic.title][room_name] = room.topics[topic.key].selections
    return matrix


def topic_metrics(project: Project) -> Dict[str, dict]:
    metrics: Dict[str, dict] = {}
    room_count = len(project.rooms)
    for topic in ROOM_TOPICS:
        all_values: List[str] = []
        rooms_with = 0
        for room in project.rooms.values():
            sels = room.topics[topic.key].selections
            if sels:
                rooms_with += 1
            all_values.extend(sels)
        freq = Counter(all_values)
        diversity = len(freq)
        dominant = (freq.most_common(1)[0][1] / len(all_values)) if all_values else 0.0
        metrics[topic.title] = {
            "rooms_with_selection": rooms_with,
            "room_count": room_count,
            "frequency": dict(freq),
            "diversity": diversity,
            "dominant_ratio": dominant,
        }
    return metrics


def room_score(project: Project) -> Dict[str, dict]:
    conflicts = detect_conflicts(project)
    scores: Dict[str, dict] = {}
    total = len(ROOM_TOPICS)
    for room_name, room in project.rooms.items():
        filled = sum(1 for t in ROOM_TOPICS if room.topics[t.key].selections)
        completeness = filled / total if total else 0
        c = len(conflicts.get(room_name, []))
        raw = max(0.0, completeness - c * 0.1)
        if raw >= 0.8:
            color = "grün"
        elif raw >= 0.55:
            color = "gelb"
        else:
            color = "rot"
        scores[room_name] = {"value": round(raw, 2), "ampel": color, "conflicts": c}
    return scores
