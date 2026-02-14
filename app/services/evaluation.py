from __future__ import annotations

from collections import Counter
from math import ceil
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


def network_rollup(project: Project) -> dict:
    ports_by_room: Dict[str, int] = {}

    base_map = {
        "Keine LAN-Ports": 0,
        "1 Port": 1,
        "2 Ports": 2,
        "4 Ports": 4,
        "6+ Ports": 6,
    }

    for room_name, room in project.rooms.items():
        selections = room.topics.get("room_lan_ports").selections if room.topics.get("room_lan_ports") else []
        port_count = 0
        for selection in selections:
            if selection in base_map:
                port_count = max(port_count, base_map[selection])
        if "Reserveport einplanen" in selections:
            port_count += 1
        if port_count > 0:
            ports_by_room[room_name] = port_count

    total_ports = sum(ports_by_room.values())
    total_cables = total_ports
    planned_with_overhead = ceil(total_ports * 1.2) + 2 if total_ports else 0

    if planned_with_overhead <= 8:
        switch = "8 Ports"
    elif planned_with_overhead <= 16:
        switch = "16 Ports"
    elif planned_with_overhead <= 24:
        switch = "24 Ports"
    elif planned_with_overhead <= 48:
        switch = "48 Ports"
    else:
        switch = "Mehrere Switches oder 48+ Ports"

    return {
        "ports_by_room": ports_by_room,
        "total_ports": total_ports,
        "total_cables": total_cables,
        "ports_with_overhead": planned_with_overhead,
        "recommended_switch": switch,
    }
