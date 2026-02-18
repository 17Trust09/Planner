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


def _parse_count(selection: str) -> int:
    selection = selection.strip()
    if selection.isdigit():
        return int(selection)

    mapping = {
        "Keine LAN-Ports": 0,
        "6+ Ports": 6,
        "0 AP": 0,
        "1 AP": 1,
        "2 AP": 2,
        "3 AP": 3,
        "4 AP": 4,
        "Kein AP im Raum": 0,
        "AP im Raum": 1,
        "AP in Flur/nahe Raum": 1,
        "Optional bei Bedarf": 0,
        "Meshing statt Kabel-AP": 0,
    }
    if selection in mapping:
        return mapping[selection]

    for n in range(1, 11):
        if selection in {f"{n} Port", f"{n} Ports"}:
            return n
    return 0


def network_rollup(project: Project) -> dict:
    client_ports_by_room: Dict[str, int] = {}
    ap_count_by_room: Dict[str, int] = {}

    for room_name, room in project.rooms.items():
        lan_selections = room.topics.get("room_lan_ports").selections if room.topics.get("room_lan_ports") else []
        ap_selections = room.topics.get("room_access_point").selections if room.topics.get("room_access_point") else []

        client_ports = max((_parse_count(s) for s in lan_selections), default=0)
        ap_count = max((_parse_count(s) for s in ap_selections), default=0)

        if client_ports > 0:
            client_ports_by_room[room_name] = client_ports
        if ap_count > 0:
            ap_count_by_room[room_name] = ap_count

    outdoor_camera = max((_parse_count(s) for s in project.outdoor_topics["outdoor_camera_count"].selections), default=0)
    outdoor_doorbell = max((_parse_count(s) for s in project.outdoor_topics["outdoor_doorbell_count"].selections), default=0)
    outdoor_ap = max((_parse_count(s) for s in project.outdoor_topics["outdoor_access_points"].selections), default=0)

    total_client_ports = sum(client_ports_by_room.values())
    total_ap_count = sum(ap_count_by_room.values())
    outdoor_poe_devices = outdoor_camera + outdoor_doorbell + outdoor_ap
    total_ap_poe_cables = total_ap_count + outdoor_poe_devices
    total_cables = total_client_ports + total_ap_poe_cables

    reserve_uplink_ports = 3 if total_cables else 0
    planned_with_overhead = total_cables + reserve_uplink_ports

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
        "client_ports_by_room": client_ports_by_room,
        "ap_count_by_room": ap_count_by_room,
        "outdoor_camera_count": outdoor_camera,
        "outdoor_doorbell_count": outdoor_doorbell,
        "outdoor_ap_count": outdoor_ap,
        "outdoor_poe_devices": outdoor_poe_devices,
        "total_client_ports": total_client_ports,
        "total_ap_count": total_ap_count,
        "total_ap_poe_cables": total_ap_poe_cables,
        "total_cables": total_cables,
        "reserve_uplink_ports": reserve_uplink_ports,
        "ports_with_overhead": planned_with_overhead,
        "recommended_switch": switch,
    }
