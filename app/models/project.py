from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List

from app.models.definitions import FLOORS, GLOBAL_TOPICS, ROOM_TOPICS


@dataclass
class TopicState:
    selections: List[str] = field(default_factory=list)
    notes: str = ""
    assignee: str = ""
    display_image: str = ""
    documents: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class RoomData:
    name: str
    floor: str
    topics: Dict[str, TopicState] = field(default_factory=dict)


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
    rooms: Dict[str, RoomData]

    def touch(self) -> None:
        self.metadata.updated_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> "Project":
        metadata_data = data["metadata"].copy()
        metadata_data.pop("display_image", None)
        metadata_data.pop("documents", None)
        metadata = ProjectMetadata(**metadata_data)
        global_topics = {k: TopicState(**v) for k, v in data.get("global_topics", {}).items()}
        rooms: Dict[str, RoomData] = {}
        for name, room_data in data.get("rooms", {}).items():
            topics = {k: TopicState(**v) for k, v in room_data.get("topics", {}).items()}
            rooms[name] = RoomData(name=room_data["name"], floor=room_data["floor"], topics=topics)
        return Project(metadata=metadata, global_topics=global_topics, rooms=rooms)


def create_empty_project(name: str) -> Project:
    global_topics = {topic.key: TopicState() for topic in GLOBAL_TOPICS}
    rooms: Dict[str, RoomData] = {}
    for floor, room_names in FLOORS.items():
        for room_name in room_names:
            rooms[room_name] = RoomData(
                name=room_name,
                floor=floor,
                topics={topic.key: TopicState() for topic in ROOM_TOPICS},
            )
    return Project(metadata=ProjectMetadata(project_name=name), global_topics=global_topics, rooms=rooms)
