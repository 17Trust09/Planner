from __future__ import annotations

from typing import Dict, List

from app.models.definitions import GLOBAL_TOPICS, ROOM_TOPICS
from app.models.project import Project
from app.services.topic_visibility import is_room_topic_applicable


ConflictItem = Dict[str, str]


def validate_required_fields(project: Project) -> List[str]:
    errors: List[str] = []
    for topic in GLOBAL_TOPICS:
        if topic.required_for_export and not project.global_topics[topic.key].selections:
            errors.append(f"Global: '{topic.title}' ist Pflichtfeld.")
    for room_name, room in project.rooms.items():
        for topic in ROOM_TOPICS:
            if not is_room_topic_applicable(project, room, topic):
                continue
            if topic.required_for_export and not room.topics[topic.key].selections:
                errors.append(f"Raum {room_name}: '{topic.title}' ist Pflichtfeld.")
    return errors


def detect_conflicts_detailed(project: Project) -> Dict[str, List[ConflictItem]]:
    conflicts: Dict[str, List[ConflictItem]] = {}
    shade_topic = next(t for t in ROOM_TOPICS if t.key == "room_shade")

    for room_name, room in project.rooms.items():
        room_conflicts: List[ConflictItem] = []
        net = room.topics["room_network"].selections
        shade = room.topics["room_shade"].selections
        sensor = room.topics["room_sensor_general"].selections + room.topics["room_climate_sensors"].selections
        security = room.topics["room_security"].selections
        camera_mode = room.topics["room_camera_storage"].selections

        if any("PoE" in s for s in net) and not any("LAN-Dose" in s for s in net):
            room_conflicts.append({"severity": "kritisch", "message": "PoE gewählt, aber keine LAN-Dose berücksichtigt."})
        if is_room_topic_applicable(project, room, shade_topic):
            if any("Sonnenstand" in s or "Zeitgesteuert" in s for s in shade) and not sensor:
                room_conflicts.append({"severity": "warnung", "message": "Automatische Beschattung ohne Sensorik gewählt."})
        if any("Kamera" in s for s in security) and not any("PoE" in s or "LAN" in s for s in net):
            room_conflicts.append({"severity": "kritisch", "message": "Kamera geplant, aber kein passendes Netzwerkprofil gewählt."})
        if any("NVR" in s or "NAS" in s for s in camera_mode) and not any("LAN" in s for s in net):
            room_conflicts.append({"severity": "warnung", "message": "Lokale Kamera-Aufzeichnung ohne stabiles LAN-Profil."})
        if room.topics["room_coverage"].selections and "WLAN reicht" in net and "Hoch (Office/Streaming)" in room.topics["room_coverage"].selections:
            room_conflicts.append({"severity": "info", "message": "Hoher Netzbedarf bei WLAN-only – LAN optional prüfen."})

        if room_conflicts:
            conflicts[room_name] = room_conflicts
    return conflicts


def detect_conflicts(project: Project) -> Dict[str, List[str]]:
    detailed = detect_conflicts_detailed(project)
    return {room: [f"[{c['severity'].upper()}] {c['message']}" for c in items] for room, items in detailed.items()}
