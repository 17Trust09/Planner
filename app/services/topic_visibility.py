from __future__ import annotations

from app.models.definitions import TopicDefinition
from app.models.project import Project, RoomData


def is_room_topic_applicable(project: Project, room: RoomData, topic: TopicDefinition) -> bool:
    del project  # reserved for future global-condition rules
    if not topic.applicable_room_types:
        return True
    return room.room_type in topic.applicable_room_types
