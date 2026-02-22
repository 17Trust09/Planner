from __future__ import annotations

from collections import Counter
from math import ceil
from typing import Dict, List

from app.models.definitions import OUTDOOR_AREA_NAME, OUTDOOR_TOPICS, ROOM_TOPICS
from app.models.project import Project
from app.services.validation import detect_conflicts


def build_room_matrix(project: Project) -> Dict[str, Dict[str, List[str]]]:
    matrix: Dict[str, Dict[str, List[str]]] = {}

    for topic in ROOM_TOPICS:
        matrix[topic.title] = {}
        for room_name, room in project.rooms.items():
            matrix[topic.title][room_name] = room.topics[topic.key].selections
        matrix[topic.title][OUTDOOR_AREA_NAME] = []

    for topic in OUTDOOR_TOPICS:
        matrix[topic.title] = {}
        for room_name in project.rooms.keys():
            matrix[topic.title][room_name] = []
        matrix[topic.title][OUTDOOR_AREA_NAME] = project.outdoor_topics[topic.key].selections

    return matrix


def topic_metrics(project: Project) -> Dict[str, dict]:
    metrics: Dict[str, dict] = {}

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
            "room_count": len(project.rooms),
            "frequency": dict(freq),
            "diversity": diversity,
            "dominant_ratio": dominant,
        }

    for topic in OUTDOOR_TOPICS:
        selections = project.outdoor_topics[topic.key].selections
        freq = Counter(selections)
        metrics[topic.title] = {
            "rooms_with_selection": 1 if selections else 0,
            "room_count": 1,
            "frequency": dict(freq),
            "diversity": len(freq),
            "dominant_ratio": (freq.most_common(1)[0][1] / len(selections)) if selections else 0.0,
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

    outdoor_filled = sum(1 for t in OUTDOOR_TOPICS if project.outdoor_topics[t.key].selections)
    outdoor_total = len(OUTDOOR_TOPICS)
    outdoor_raw = outdoor_filled / outdoor_total if outdoor_total else 0
    if outdoor_raw >= 0.8:
        outdoor_color = "grün"
    elif outdoor_raw >= 0.55:
        outdoor_color = "gelb"
    else:
        outdoor_color = "rot"
    scores[OUTDOOR_AREA_NAME] = {"value": round(outdoor_raw, 2), "ampel": outdoor_color, "conflicts": 0}

    return scores


def _parse_count(selection: str) -> int:
    selection = selection.strip()
    if selection.isdigit():
        return int(selection)

    mapping = {
        "0 Dosen": 0,
        "1 Dose": 1,
        "2 Dosen": 2,
        "3 Dosen": 3,
        "4 Dosen": 4,
        "5 Dosen": 5,
        "6 Dosen": 6,
        "7 Dosen": 7,
        "8 Dosen": 8,
        "1 Port je Dose": 1,
        "2 Ports je Dose": 2,
        "3 Ports je Dose": 3,
        "4 Ports je Dose": 4,
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




def _switch_size_for_ports(port_count: int) -> str:
    if port_count <= 0:
        return "Kein zusätzlicher Switch"
    if port_count <= 8:
        return "8 Ports"
    if port_count <= 16:
        return "16 Ports"
    if port_count <= 24:
        return "24 Ports"
    if port_count <= 48:
        return "48 Ports"
    return "Mehrere Switches oder 48+ Ports"


def network_rollup(project: Project) -> dict:
    client_ports_by_room: Dict[str, int] = {}
    ap_count_by_room: Dict[str, int] = {}

    for room_name, room in project.rooms.items():
        socket_selections = room.topics.get("room_lan_socket_count").selections if room.topics.get("room_lan_socket_count") else []
        ports_per_socket_selections = room.topics.get("room_lan_ports_per_socket").selections if room.topics.get("room_lan_ports_per_socket") else []
        ap_selections = room.topics.get("room_access_point").selections if room.topics.get("room_access_point") else []

        socket_count = max((_parse_count(s) for s in socket_selections), default=0)
        ports_per_socket = max((_parse_count(s) for s in ports_per_socket_selections), default=0)
        client_ports = socket_count * ports_per_socket
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

    switch = _switch_size_for_ports(planned_with_overhead)

    poe_ratio = (outdoor_poe_devices + total_ap_count) / total_cables if total_cables else 0.0
    split_recommended = planned_with_overhead > 48 or (planned_with_overhead > 24 and poe_ratio >= 0.4)

    poe_ports_with_reserve = (outdoor_poe_devices + total_ap_count) + (1 if (outdoor_poe_devices + total_ap_count) else 0)
    client_ports_with_reserve = total_client_ports + (2 if total_client_ports else 0)
    split_plan = {
        "poe_ports": poe_ports_with_reserve,
        "poe_switch": _switch_size_for_ports(poe_ports_with_reserve),
        "client_ports": client_ports_with_reserve,
        "client_switch": _switch_size_for_ports(client_ports_with_reserve),
    }

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
        "poe_ratio": round(poe_ratio, 2),
        "split_recommended": split_recommended,
        "split_plan": split_plan,
    }


def recommended_global_network_topics(project: Project) -> Dict[str, List[str]]:
    net = network_rollup(project)

    switch_value = net["recommended_switch"]
    if switch_value == "Mehrere Switches oder 48+ Ports":
        switch_value = "Mehrere Switches"

    poe_share = (net["total_ap_poe_cables"] / net["ports_with_overhead"]) if net["ports_with_overhead"] else 0.0
    if poe_share >= 0.6:
        poe_share_value = "Ja"
    elif poe_share >= 0.25:
        poe_share_value = "Vielleicht"
    else:
        poe_share_value = "Nein"

    total_planned_aps = net["total_ap_count"] + net["outdoor_ap_count"]
    ap_count_value = "Ja" if total_planned_aps > 0 else "Nein"
    poe_planning_value = "Ja" if net["total_ap_poe_cables"] > 0 else "Nein"

    return {
        "global_switch_size": [switch_value],
        "global_switch_poe": [poe_share_value],
        "global_ap_count": [ap_count_value],
        "global_poe": [poe_planning_value],
    }
