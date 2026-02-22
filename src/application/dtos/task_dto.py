from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from domain.entities import Task
from domain.utils import set_weekdays_to_str_weekdays

def strip_whitespace(v: str | None) -> str | None:
    """Strip whitespace from string values."""
    return v.strip() if isinstance(v, str) else v

class CreateTaskDTO(BaseModel):
    """DTO for creating a task."""
    title: Annotated[str, BeforeValidator(strip_whitespace), Field(min_length=1)]
    note: str | None = None
    due_date: datetime | None = None
    #is_completed: bool = False
    is_important: bool = False

    repeat_frequency: int | None = None
    repeat_interval: int | None = None
    repeat_allowed_weekdays: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Task title",
                "note": "Task note",
                "due_date": "2025-01-01T00:00:00",
                #"is_completed": False,
                "is_important": True,
                "repeat_frequency": 1,
                "repeat_interval": 1,
                "repeat_allowed_weekdays": "12345"
            }
        }
    )

class UpdateTaskDTO(CreateTaskDTO):
    """DTO for updating a task."""
    title: Annotated[str, BeforeValidator(strip_whitespace), Field(min_length=1)]
    note: str | None = None
    due_date: datetime | None = None
    #is_completed: bool = False
    is_important: bool = False

    repeat_frequency: int | None = None
    repeat_interval: int | None = None
    repeat_allowed_weekdays: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Task title",
                "note": "Task note",
                "due_date": "2025-01-01T00:00:00",
                #"is_completed": False,
                "is_important": True,
                "repeat_frequency": 1,
                "repeat_interval": 1,
                "repeat_allowed_weekdays": "12345"
            }
        }
    )

class TaskDTO(BaseModel):
    """DTO for a task."""
    id: int
    title: str
    note: str | None = None
    due_date: datetime | None = None
    is_completed: bool = False
    is_important: bool = False

    repeat_frequency: int | None = None
    repeat_interval: int | None = None
    repeat_allowed_weekdays: str | None = None

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
        
        if task.repeat:
            repeat_frequency = task.repeat.frequency.value
            repeat_interval = task.repeat.interval
            repeat_allowed_weekdays = set_weekdays_to_str_weekdays(task.repeat.allowed_weekdays)
        else:
            repeat_frequency = None
            repeat_interval = None
            repeat_allowed_weekdays = None

        return cls(
            id=task.id,
            title=task.title,
            note=task.note,
            due_date=task.due_date,
            is_completed=task.is_completed,
            is_important=task.is_important,

            repeat_frequency=repeat_frequency,
            repeat_interval=repeat_interval,
            repeat_allowed_weekdays=repeat_allowed_weekdays,
            
            created_at=task.created_at,
            updated_at=task.updated_at
        )
