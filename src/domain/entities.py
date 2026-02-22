from dataclasses import dataclass
from typing import Set
from datetime import datetime
import calendar

from dateutil.rrule import rrule

from domain.constants import START_WEEKDAY, WEEKDAY_WEEKDAYS, WEEKEND_WEEKDAYS
from domain.enums import RepeatFrequency
from domain.exceptions import (
    InvalidEntityStateException,
    BusinessRuleViolationException
)

@dataclass
class Step:
    title: str

    id: int | None = None
    task_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """Validate at creation"""

        if self.task_id is None:
            raise InvalidEntityStateException(
                "Task ID cannot be empty. Step must refer to a task."
            )

        if not self.title and len(self.title.strip()) == 0:
            raise InvalidEntityStateException(
                "Title cannot be empty. Step must have a title."
            )

    def change_title(self, new_title: str | None):
        """Change Step title with validation"""
        if not new_title and len(new_title.strip()) == 0:
            raise BusinessRuleViolationException(
                "Cannot change title to empty. Title must contain at least one character."
            )
        self.title = new_title

    def convert_to_task(self):
        """Convert Step to Task"""
        return Task(title=self.title)

    def __str__(self):
        return self.title

@dataclass
class Repeat:
    frequency: RepeatFrequency
    interval: int
    allowed_weekdays: Set[int] | None = None

    def __post_init__(self):
        """Validate at creation"""

        if self.frequency is None:
            raise InvalidEntityStateException(
                "Frequency cannot be empty. Repeat must have a frequency."
            )

        if self.interval is None:
            raise InvalidEntityStateException(
                "Interval cannot be empty. Repeat must have an interval."
            )

        if self.interval < 1:
            raise InvalidEntityStateException(
                "Interval cannot be less than 1."
            )

        if self.frequency == RepeatFrequency.WEEKLY and not self.allowed_weekdays:
            raise InvalidEntityStateException(
                "Allowed weekdays cannot be empty for Weekly Repeats."
            )
        
        if self.frequency != RepeatFrequency.WEEKLY:
            # Reset allowed weekdays
            self.allowed_weekdays = None

    def change_configurations(self,
        new_frequency: RepeatFrequency | None,
        new_interval: int | None,
        new_allowed_weekdays: Set[int] | None
    ):
        """Change Repeat frequency with validation"""
        if new_frequency is None:
            raise BusinessRuleViolationException(
                "Cannot change frequency to empty."
            )
        self.frequency = new_frequency

        """Change Repeat interval with validation"""
        if new_interval is None:
            raise BusinessRuleViolationException(
                "Cannot change interval to empty."
            )

        if new_interval < 1:
            raise BusinessRuleViolationException(
                "Cannot change interval to less than 1."
            )

        if self.frequency == RepeatFrequency.WEEKLY:
            """Change Repeat interval with validation"""
            if not new_allowed_weekdays:
                raise BusinessRuleViolationException(
                    "Cannot change allowed weekdays to empty for Weekly Repeats."
                )
            self.allowed_weekdays = new_allowed_weekdays
        else:
            # Reset allowed weekdays
            self.allowed_weekdays = None

    def find_next_date(self, reference_date: datetime) -> datetime:
        """Find the next due date based on repeat configurations"""
        repeat_rrule = rrule(
            dtstart=reference_date,
            freq=self.frequency,
            interval=self.interval,
            byweekday=self.allowed_weekdays,
            wkst=START_WEEKDAY,
        )
        next_date = repeat_rrule.after(reference_date)
        return next_date

    @classmethod
    def create_new(
        cls,
        frequency: RepeatFrequency | None = None,
        interval: int | None = None,
        allowed_weekdays: Set[int] | None = None
    ) -> Repeat | None:
        if not frequency and not interval and not allowed_weekdays:
            return None
        return Repeat(
            frequency=frequency,
            interval=interval,
            allowed_weekdays=allowed_weekdays
        )

    def __str__(self):
        match self.frequency:
            case RepeatFrequency.YEARLY:
                if self.interval == 1:
                    return "Repeat yearly"
                else:
                    return f"Repeat every {self.interval} years"
                
            case RepeatFrequency.MONTHLY:
                if self.interval == 1:
                    return "Repeat monthly"
                else:
                    return f"Repeat every {self.interval} months"

            case RepeatFrequency.WEEKLY:
                frequency_description = (
                    "Repeat weekly"
                    if self.interval == 1
                    else f"Repeat every {self.interval} weeks"
                )

                if self.allowed_weekdays == WEEKDAY_WEEKDAYS:
                    weekdays_description = "weekdays"
                elif self.allowed_weekdays == WEEKEND_WEEKDAYS:
                    weekdays_description = "weekends"
                else:
                    weekdays_description = ", ".join(calendar.day_abbr[n] for n in self.allowed_weekdays)
                
                return f"{frequency_description} on {weekdays_description}"

            case RepeatFrequency.DAILY:
                if self.interval == 1:
                    return "Repeat daily"
                else:
                    return f"Repeat every {self.interval} days"

@dataclass
class Task:
    title: str
    note: str | None = None
    due_date: datetime | None = None
    is_completed: bool = False
    is_important: bool = False

    repeat: Repeat | None = None

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate at creation"""

        if not self.title and len(self.title.strip()) == 0:
            raise InvalidEntityStateException(
                "Title cannot be empty. Task must have a title."
            )

        if self.repeat:
            if not self.due_date:
                raise InvalidEntityStateException(
                    "Task with repeat must have a due date."
                )
            # Special case for Weekly Repeats
            else:
                if (
                    self.repeat.frequency == RepeatFrequency.WEEKLY
                    and self.due_date.weekday() not in self.repeat.allowed_weekdays
                ):
                    raise InvalidEntityStateException(
                        "Due date must be on one of the allowed weekdays for Weekly Repeats."
                    )

    def change_title(self, new_title: str | None) -> None:
        """Change Task's title with validation"""
        if not new_title and len(new_title.strip()) == 0:
            raise ValueError(
                "Cannot change title to empty value. Title must contain at least one character."
            )

        self.title = new_title

    def change_due_date_and_repeat(self, new_due_date: datetime | None, new_repeat: Repeat | None) -> None:
        """Change Task's due date with validation"""
        if new_repeat:
            if not new_due_date:
                raise BusinessRuleViolationException(
                    "Task with repeat must have a due date."
                )
            # Special case for Weekly Repeats
            else:
                if (
                    new_repeat == RepeatFrequency.WEEKLY
                    and new_due_date.weekday() not in new_repeat.allowed_weekdays
                ):
                    raise BusinessRuleViolationException(
                        "Due date must be on one of the allowed weekdays for Weekly Repeats."
                    )

        self.due_date = new_due_date
        self.repeat = new_repeat

    def is_due(self) -> bool:
        """Check if the task is due"""
        if not self.due_date:
            return False
        return datetime.now() >= self.due_date

    def create_new_repeating_task(self) -> Task | None:
        """Create a new repeating task with new due date"""
        if self.repeat:
            return Task(
                title=self.title,
                note=self.note,
                due_date=self.repeat.find_next_date(self.due_date),
                is_completed=False,
                is_important=self.is_important,
                repeat=self.repeat
            )
        else:
            return None

    def __str__(self):
        if self.due_date:
            return f"{self.title} | due on {self.due_date.strftime('%Y-%m-%d')}"
        else:
            return self.title
