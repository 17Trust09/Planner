from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List

from app.models.definitions import FLOORS, GLOBAL_TOPICS, OUTDOOR_TOPICS, OUTDOOR_AREA_NAME, ROOM_TOPICS


@dataclass
class TopicState:
    selections: List[str] = field(default_factory=list)
    notes: str = ""
    assignee: str = ""
    quantities: Dict[str, int] = field(default_factory=dict)


@dataclass
class RoomData:
    name: str
    floor: str
    area: str = "Innenbereich"
    topics: Dict[str, TopicState] = field(default_factory=dict)


@dataclass
class StructureSubarea:
    name: str
    rooms: List[str] = field(default_factory=list)


@dataclass
class StructureArea:
    name: str
    subareas: List[StructureSubarea] = field(default_factory=list)


@dataclass
class ProjectMetadata:
    project_name: str
    status: str = "Entwurf"
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class Project:
    metadata: ProjectMetadata
    global_topics: Dict[str, TopicState]
    outdoor_topics: Dict[str, TopicState]
    rooms: Dict[str, RoomData]
    house_areas: List[StructureArea] = field(default_factory=list)
    pricing_settings: Dict[str, object] = field(default_factory=dict)
    floor_plans: Dict[str, Dict[str, object]] = field(default_factory=dict)

    def touch(self) -> None:
        self.metadata.updated_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> "Project":
        metadata = ProjectMetadata(**data["metadata"])

        raw_global_topics = {k: TopicState(**v) for k, v in data.get("global_topics", {}).items()}
        global_topics = {topic.key: raw_global_topics.get(topic.key, TopicState()) for topic in GLOBAL_TOPICS}

        raw_outdoor_topics = {k: TopicState(**v) for k, v in data.get("outdoor_topics", {}).items()}
        outdoor_topics = {topic.key: raw_outdoor_topics.get(topic.key, TopicState()) for topic in OUTDOOR_TOPICS}

        rooms: Dict[str, RoomData] = {}
        raw_rooms = data.get("rooms", {})
        for room_key, room_data in raw_rooms.items():
            if room_key == OUTDOOR_AREA_NAME:
                continue
            raw_topics = {k: TopicState(**v) for k, v in room_data.get("topics", {}).items()}
            topics = {topic.key: raw_topics.get(topic.key, TopicState()) for topic in ROOM_TOPICS}
            room_name = str(room_data.get("name") or room_key)
            room_floor = str(room_data.get("floor") or room_data.get("subarea") or "Allgemein")
            room_area = str(room_data.get("area") or "Innenbereich")
            rooms[room_key] = RoomData(name=room_name, floor=room_floor, area=room_area, topics=topics)

        # Fallback für ältere Projekte, die Außenbereich evtl. in rooms abgelegt haben.
        outdoor_room_legacy = data.get("rooms", {}).get(OUTDOOR_AREA_NAME)
        if outdoor_room_legacy and not data.get("outdoor_topics"):
            legacy_topics = {k: TopicState(**v) for k, v in outdoor_room_legacy.get("topics", {}).items()}
            for topic in OUTDOOR_TOPICS:
                outdoor_topics[topic.key] = legacy_topics.get(topic.key, outdoor_topics[topic.key])

        house_areas = _parse_house_areas(data.get("house_areas"), rooms)
        _ensure_rooms_in_structure(house_areas, rooms)

        pricing_settings_raw = data.get("pricing_settings", {})
        pricing_settings = pricing_settings_raw if isinstance(pricing_settings_raw, dict) else {}

        floor_plans_raw = data.get("floor_plans", {})
        floor_plans = floor_plans_raw if isinstance(floor_plans_raw, dict) else {}

        return Project(
            metadata=metadata,
            global_topics=global_topics,
            outdoor_topics=outdoor_topics,
            rooms=rooms,
            house_areas=house_areas,
            pricing_settings=pricing_settings,
            floor_plans=floor_plans,
        )


def create_empty_project(name: str) -> Project:
    global_topics = {topic.key: TopicState() for topic in GLOBAL_TOPICS}
    outdoor_topics = {topic.key: TopicState() for topic in OUTDOOR_TOPICS}
    return Project(
        metadata=ProjectMetadata(project_name=name),
        global_topics=global_topics,
        outdoor_topics=outdoor_topics,
        rooms={},
        house_areas=[StructureArea(name=OUTDOOR_AREA_NAME)],
        pricing_settings={},
        floor_plans={},
    )


def ordered_room_ids(project: Project) -> List[str]:
    ordered: List[str] = []
    seen: set[str] = set()
    for area in project.house_areas:
        for subarea in area.subareas:
            for room_id in subarea.rooms:
                if room_id in project.rooms and room_id not in seen:
                    ordered.append(room_id)
                    seen.add(room_id)
    for room_id in project.rooms.keys():
        if room_id not in seen:
            ordered.append(room_id)
    return ordered


def floor_scopes(project: Project) -> List[str]:
    scopes: List[str] = []
    for area in project.house_areas:
        if area.name == OUTDOOR_AREA_NAME:
            scopes.append(OUTDOOR_AREA_NAME)
        else:
            for sub in area.subareas:
                if sub.name not in scopes:
                    scopes.append(sub.name)
    if not scopes:
        scopes.append(OUTDOOR_AREA_NAME)
    return scopes


def _parse_house_areas(raw_house_areas: object, rooms: Dict[str, RoomData]) -> List[StructureArea]:
    if isinstance(raw_house_areas, list) and raw_house_areas:
        areas: List[StructureArea] = []
        for area_raw in raw_house_areas:
            if not isinstance(area_raw, dict):
                continue
            area_name = str(area_raw.get("name") or "Bereich")
            subareas: List[StructureSubarea] = []
            for sub_raw in area_raw.get("subareas", []):
                if not isinstance(sub_raw, dict):
                    continue
                sub_name = str(sub_raw.get("name") or "Unterbereich")
                room_ids = [str(room_id) for room_id in sub_raw.get("rooms", []) if isinstance(room_id, str)]
                subareas.append(StructureSubarea(name=sub_name, rooms=room_ids))
            areas.append(StructureArea(name=area_name, subareas=subareas))
        if areas:
            if not any(a.name == OUTDOOR_AREA_NAME for a in areas):
                areas.insert(0, StructureArea(name=OUTDOOR_AREA_NAME))
            return areas

    # Legacy-Fallback aus vorhandenen Räumen, sonst alte FLOORS-Vorlage.
    if rooms:
        grouped: Dict[str, Dict[str, List[str]]] = {}
        for room_id, room in rooms.items():
            grouped.setdefault(room.area or "Innenbereich", {}).setdefault(room.floor or "Allgemein", []).append(room_id)
        areas: List[StructureArea] = []
        if OUTDOOR_AREA_NAME not in grouped:
            areas.append(StructureArea(name=OUTDOOR_AREA_NAME))
        for area_name, subs in grouped.items():
            if area_name == OUTDOOR_AREA_NAME:
                continue
            areas.append(
                StructureArea(
                    name=area_name,
                    subareas=[StructureSubarea(name=sub_name, rooms=room_ids) for sub_name, room_ids in subs.items()],
                )
            )
        if not areas:
            areas.append(StructureArea(name=OUTDOOR_AREA_NAME))
        return areas

    # Fallback für ganz alte leere Daten.
    return [
        StructureArea(name=OUTDOOR_AREA_NAME),
        StructureArea(
            name="Innenbereich",
            subareas=[StructureSubarea(name=floor, rooms=list(room_names)) for floor, room_names in FLOORS.items()],
        ),
    ]


def _ensure_rooms_in_structure(house_areas: List[StructureArea], rooms: Dict[str, RoomData]) -> None:
    referenced: set[str] = set()
    for area in house_areas:
        for sub in area.subareas:
            filtered: List[str] = []
            for room_id in sub.rooms:
                if room_id in rooms and room_id not in referenced:
                    filtered.append(room_id)
                    referenced.add(room_id)
                    rooms[room_id].area = area.name
                    rooms[room_id].floor = sub.name
            sub.rooms = filtered

    if not any(area.name == OUTDOOR_AREA_NAME for area in house_areas):
        house_areas.insert(0, StructureArea(name=OUTDOOR_AREA_NAME))

    unassigned = [room_id for room_id in rooms.keys() if room_id not in referenced]
    if not unassigned:
        return

    indoor = next((a for a in house_areas if a.name != OUTDOOR_AREA_NAME), None)
    if indoor is None:
        indoor = StructureArea(name="Innenbereich")
        house_areas.append(indoor)
    if not indoor.subareas:
        indoor.subareas.append(StructureSubarea(name="Allgemein", rooms=[]))

    target_subarea = indoor.subareas[0]
    for room_id in unassigned:
        target_subarea.rooms.append(room_id)
        rooms[room_id].area = indoor.name
        rooms[room_id].floor = target_subarea.name
