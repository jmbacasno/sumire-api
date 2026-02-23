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

class Repeat:
    def __init__(self,
        frequency: int,
        interval: int,
        allowed_weekdays: str | None = None
    ) -> None:
        if frequency is None:
            raise InvalidEntityStateException(
                "Frequency cannot be empty."
            )

        if frequency < 0 or frequency > 3:
            raise InvalidEntityStateException(
                "Frequency must be between 0 and 3."
            )

        self.frequency = frequency

        if interval is None:
            raise InvalidEntityStateException(
                "Interval cannot be empty."
            )

        if interval < 1:
            raise InvalidEntityStateException(
                "Interval cannot be less than 1."
            )

        self.interval = interval

        if frequency == RepeatFrequency.WEEKLY:
            if allowed_weekdays is None:
                raise InvalidEntityStateException(
                    "Allowed weekdays cannot be empty for weekly repeats."
                )
            else:
                for weekday in allowed_weekdays:
                    if weekday not in "0123456":
                        raise InvalidEntityStateException(
                            f"Allowed weekdays must be string of integers from 0 to 6."
                        )

            self._allowed_weekdays_set = set(map(int, allowed_weekdays))
            self.allowed_weekdays = "".join(map(str, self._allowed_weekdays_set))
        else:
            self._allowed_weekdays_set = None
            self.allowed_weekdays = None

    def get_next_date(self, reference_date: datetime) -> datetime:
        """Get next date."""
        weekly_repeat_rrule = rrule(
            dtstart=reference_date,
            freq=self.frequency,
            interval=self.interval,
            byweekday=self._allowed_weekdays_set,
            wkst=START_WEEKDAY
        )
        return weekly_repeat_rrule.after(reference_date)

    def __str__(self) -> str:
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
                    weekdays_description = ", ".join(calendar.day_abbr[n] for n in self._allowed_weekdays_set)

                return f"{frequency_description} on {weekdays_description}"

            case RepeatFrequency.DAILY:
                if self.interval == 1:
                    return "Repeat daily"
                else:
                    return f"Repeat every {self.interval} days"

    @classmethod
    def create_repeat(
        cls,
        frequency: int | None = None,
        interval: int | None = None,
        allowed_weekdays: str | None = None
    ) -> Repeat | None:
        # No repeat
        if frequency is None:
            return None
        return Repeat(
            frequency=frequency,
            interval=interval,
            allowed_weekdays=allowed_weekdays
        )

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
            repeat_allowed_weekdays: str | None = None,

            id: int | None = None,
            created_at: datetime | None = None,
            updated_at: datetime | None = None
        ) -> None:

        if description is None or len(description.strip()) == 0:
            raise InvalidEntityStateException("Description cannot be empty.")

        self.description = description
        self.note = note
        self.due_date = due_date
        self.is_completed = is_completed
        self.is_important = is_important

        self.__repeat = Repeat.create_repeat(
            frequency=repeat_frequency,
            interval=repeat_interval,
            allowed_weekdays=repeat_allowed_weekdays
        )
        self.repeat_frequency = self.__repeat.frequency if self.__repeat is not None else None
        self.repeat_interval = self.__repeat.interval if self.__repeat is not None else None
        self.repeat_allowed_weekdays = self.__repeat.allowed_weekdays if self.__repeat is not None else None

        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at

    def change_description(self, new_description: str) -> None:
        """Change description with validation"""
        if not new_description and len(new_description.strip()) == 0:
            raise BusinessRuleViolationException(
                "Description cannot be empty."
            )

    def change_due_date_and_repeat(
        self,
        new_due_date: datetime | None,
        new_repeat_frequency: int | None,
        new_repeat_interval: int | None,
        new_repeat_allowed_weekdays: str | None
    ) -> None:
        new_repeat = Repeat.create_repeat(
            frequency=new_repeat_frequency,
            interval=new_repeat_interval,
            allowed_weekdays=new_repeat_allowed_weekdays
        )

        if new_repeat:
            if not new_due_date:
                raise BusinessRuleViolationException(
                    "Task with repeat must have a due date."
                )
            else:
                if (
                    new_repeat.frequency == RepeatFrequency.WEEKLY
                    and new_due_date.weekday() not in new_repeat._allowed_weekdays_set
                ):
                    raise BusinessRuleViolationException(
                        "Due date must be on one of the allowed weekdays for weekly repeats."
                    )

        self.due_date = new_due_date

        self.__repeat = new_repeat
        self.repeat_frequency = self.__repeat.frequency if self.__repeat is not None else None
        self.repeat_interval = self.__repeat.interval if self.__repeat is not None else None
        self.repeat_allowed_weekdays = self.__repeat.allowed_weekdays if self.__repeat is not None else None

    def create_new_repeating_task(self) -> Task | None:
        """Create a new repeating task with new due date"""
        if self.__repeat:
            return Task(
                description=self.description,
                note=self.note,
                due_date=self.__repeat.get_next_date(self.due_date),
                is_completed=False,
                is_important=self.is_important,

                repeat_frequency=self.repeat_frequency,
                repeat_interval=self.repeat_interval,
                repeat_allowed_weekdays=self.repeat_allowed_weekdays
            )
        else:
            return None

    def __str__(self) -> str:
        if self.due_date:
            return f"{self.description} | due on {self.due_date.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            return self.description
