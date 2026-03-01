from datetime import datetime

from domain.value_objects import RepeatManager

class Task:
    def __init__(
        self,
        description: str,
        note: str | None = None,
        due_date: datetime | None = None,
        is_completed: bool = False,
        is_important: bool = False,
        repeat_frequency: int | None = None,
        repeat_interval: int | None = None,
        repeat_weekdays: str | None = None,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ) -> None:
        if description is None or len(description.strip()) == 0:
            raise ValueError("Description cannot be empty.")

        self.description = description
        self.note = note
        self.due_date = due_date
        self.is_completed = is_completed
        self.is_important = is_important

        self.repeat_manager = RepeatManager(due_date, repeat_frequency, repeat_interval, repeat_weekdays)

        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at

    def change_description(self, description: str) -> None:
        if description is None or len(description.strip()) == 0:
            raise ValueError("Description cannot be empty.")

        self.description = description

    def change_repeat_manager(self,
        due_date: datetime | None,
        frequency: int | None,
        interval: int | None,
        weekdays_str: str | None
    ) -> None:
        self.repeat_manager = RepeatManager(
            due_date=due_date,
            frequency=frequency,
            interval=interval,
            weekdays_str=weekdays_str
        )

    def create_new_repeating_task(self) -> Task | None:
        next_due_date = self.repeat_manager.get_next_due_date()
        if next_due_date is None:
            return None
        return Task(
            description=self.description,
            note=self.note,
            due_date=next_due_date,
            is_completed=self.is_completed,
            is_important=self.is_important,
            repeat_frequency=self.repeat_manager.repeat.frequency,
            repeat_interval=self.repeat_manager.repeat.interval,
            repeat_weekdays=self.repeat_manager.repeat.weekdays_str,
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def __str__(self) -> str:
        return f"{self.description} | {self.repeat_manager}"
