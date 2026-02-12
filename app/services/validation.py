from __future__ import annotations

from typing import Dict, List

from app.models.definitions import GLOBAL_TOPICS, ROOM_TOPICS
from app.models.project import Project


def validate_required_fields(project: Project) -> List[str]:
    errors: List[str] = []
    for topic in GLOBAL_TOPICS:
        if topic.required_for_export and not project.global_topics[topic.key].selections:
            errors.append(f"Global: '{topic.title}' ist Pflichtfeld.")
    for room_name, room in project.rooms.items():
        for topic in ROOM_TOPICS:
            if topic.required_for_export and not room.topics[topic.key].selections:
                errors.append(f"Raum {room_name}: '{topic.title}' ist Pflichtfeld.")
    return errors


def detect_conflicts(project: Project) -> Dict[str, List[str]]:
    conflicts: Dict[str, List[str]] = {}
    for room_name, room in project.rooms.items():
        room_conflicts: List[str] = []
        net = room.topics["room_network"].selections
        shade = room.topics["room_shade"].selections
        sensor = room.topics["room_sensor_general"].selections + room.topics["room_climate_sensors"].selections

        if any("PoE" in s for s in net) and not any("LAN-Dose" in s for s in net):
            room_conflicts.append("PoE gewählt, aber keine LAN-Dose berücksichtigt.")
        if any("Sonnenstand" in s or "Zeitgesteuert" in s for s in shade) and not sensor:
            room_conflicts.append("Automatische Beschattung ohne Sensorik gewählt.")
        if any("Kamera" in s for s in room.topics["room_security"].selections) and not any("PoE" in s or "LAN" in s for s in net):
            room_conflicts.append("Kamera geplant, aber kein passendes Netzwerkprofil gewählt.")
        if room_conflicts:
            conflicts[room_name] = room_conflicts
    return conflicts
