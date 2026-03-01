from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from domain.entities import Task

def strip_whitespace(v: str | None) -> str | None:
    """Strip whitespace from string values."""
    return v.strip() if isinstance(v, str) else v

class CreateTaskDTO(BaseModel):
    """DTO for creating a task."""
    description: Annotated[str, BeforeValidator(strip_whitespace), Field(min_length=1)]
    due_date: datetime | None = None
    repeat_frequency: int | None = None
    repeat_interval: int | None = None
    repeat_weekdays: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Finish Anki decks",
                "due_date": "2026-01-01",
                "repeat_frequency": 3, # Daily
                "repeat_interval": 1, # Every day
                "repeat_weekdays": None
            }
        }
    )

class UpdateTaskDTO(CreateTaskDTO):
    """DTO for updating a task."""
    description: Annotated[str, BeforeValidator(strip_whitespace), Field(min_length=1)]
    note: str | None = None
    due_date: datetime | None = None
    is_important: bool = False
    repeat_frequency: int | None = None
    repeat_interval: int | None = None
    repeat_weekdays: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "description": "Finish Anki decks",
                "note": "Open AnkiDroid app to start",
                "due_date": "2026-01-01",
                "is_important": True,
                "repeat_frequency": 2, # Weekly
                "repeat_interval": 1, # Every week
                "repeat_weekdays": "01234" # Monday to Friday
            }
        }
    )

class TaskDTO(BaseModel):
    """DTO for a task."""
    id: int
    description: str
    note: str | None = None
    due_date: datetime | None = None
    is_completed: bool = False
    is_important: bool = False
    repeat_frequency: int | None = None
    repeat_interval: int | None = None
    repeat_weekdays: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, task: Task) -> TaskDTO:
        """Convert a PERSISTED task entity to a TaskDTO."""
        # Validate precondition: task entity must be persisted
        if task.id is None:
            raise ValueError(
                "Cannot create TaskDTO from non-persisted task entity: missing id."
                "Ensure task entity has been saved via repository before converting to TaskDTO."
            )

        if task.created_at is None:
            raise ValueError(
                "Cannot create TaskDTO from non-persisted task entity: missing created_at."
                "Ensure task entity has been saved via repository before converting to TaskDTO."
            )

        if task.updated_at is None:
            raise ValueError(
                "Cannot create TaskDTO from non-persisted task entity: missing updated_at."
                "Ensure task entity has been saved via repository before converting to TaskDTO."
            )

        return cls(
            id=task.id,
            description=task.description,
            note=task.note,
            due_date=task.repeat_manager.due_date,
            is_completed=task.is_completed,
            is_important=task.is_important,
            repeat_frequency=task.repeat_manager.repeat.frequency,
            repeat_interval=task.repeat_manager.repeat.interval,
            repeat_weekdays=task.repeat_manager.repeat.weekdays_str,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
