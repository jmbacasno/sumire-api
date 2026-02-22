from typing import Set
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime
import calendar

from dateutil.rrule import rrule

from domain.constants import START_WEEKDAY, WEEKDAY_WEEKDAYS, WEEKEND_WEEKDAYS
from domain.exceptions import (
    InvalidEntityStateException,
    BusinessRuleViolationException
)

class Frequency(IntEnum):
    YEARLY = 0
    MONTHLY = 1
    WEEKLY = 2
    DAILY = 3

@dataclass
class Repeat:
    frequency: Frequency
    interval: int

    def __post_init__(self):
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
                "Interval must be a positive integer."
            )

    def get_next_date(self, reference_date: datetime) -> datetime:
        """Get next date."""
        repeat_rrule = rrule(
            dtstart=reference_date,
            freq=self.frequency,
            interval=self.interval,
            wkst=START_WEEKDAY,
        )
        return repeat_rrule.after(reference_date)

@dataclass
class YearlyRepeat(Repeat):
    frequency: Frequency = field(default=Frequency.YEARLY, init=False)

    def __str__(self):
        if self.interval == 1:
            return "Repeat yearly"
        return f"Repeat every {self.interval} years"

@dataclass
class MonthlyRepeat(Repeat):
    frequency: Frequency = field(default=Frequency.MONTHLY, init=False)

    def __str__(self):
        if self.interval == 1:
            return "Repeat monthly"
        return f"Repeat every {self.interval} months"

@dataclass
class WeeklyRepeat(Repeat):
    frequency: Frequency = field(default=Frequency.WEEKLY, init=False)
    allowed_weekdays: Set[int] | str

    def __post_init__(self):
        super().__post_init__()
        if self.allowed_weekdays is None or len(self.allowed_weekdays) == 0:
            raise InvalidEntityStateException(
                "Allowed weekdays cannot be empty. Weekly repeat must have allowed weekdays."
            )

        # Convert string to set
        if isinstance(self.allowed_weekdays, str):
            try:
                self.allowed_weekdays = set(map(int, self.allowed_weekdays))
            except ValueError:
                raise InvalidEntityStateException(
                    "Cannot convert string to set of integers. Allowed weekdays must contain only integers."
                )

        # Check if all weekdays are valid
        for weekday in self.allowed_weekdays:
            if weekday < 0 or weekday > 6:
                raise InvalidEntityStateException(
                    "Allowed weekdays must be from 0 (Monday) to 6 (Sunday)."
                )

    def __str__(self):
        repeat_description = "Repeat weekly" if self.interval == 1 else f"Repeat every {self.interval} weeks"
        
        if self.allowed_weekdays == WEEKDAY_WEEKDAYS:
            weekdays_description = "weekdays"
        elif self.allowed_weekdays == WEEKEND_WEEKDAYS:
            weekdays_description = "weekends"
        else:
            weekdays_description = ", ".join(calendar.day_abbr[weekday] for weekday in self.allowed_weekdays)

        return f"{repeat_description} on {weekdays_description}"

    def get_next_date(self, reference_date: datetime) -> datetime:
        """Get next date."""
        weekly_repeat_rrule = rrule(
            dtstart=reference_date,
            freq=self.frequency,
            interval=self.interval,
            wkst=START_WEEKDAY,
            byweekday=self.allowed_weekdays
        )
        return weekly_repeat_rrule.after(reference_date)

@dataclass
class DailyRepeat(Repeat):
    frequency: Frequency = field(default=Frequency.DAILY, init=False)

    def __str__(self):
        if self.interval == 1:
            return "Repeat daily"
        return f"Repeat every {self.interval} days"

class RepeatFactory:
    @staticmethod
    def create_repeat(
        frequency: Frequency | None = None,
        interval: int | None = None,
        allowed_weekdays: Set[int] | str | None = None
    ) -> Repeat | None:
        """Create repeat based on configurations."""
        # No repeat
        if frequency is None and interval is None and allowed_weekdays is None:
            return None

        match frequency:
            case Frequency.YEARLY:
                return YearlyRepeat(interval=interval)
            case Frequency.MONTHLY:
                return MonthlyRepeat(interval=interval)
            case Frequency.WEEKLY:
                return WeeklyRepeat(interval=interval, allowed_weekdays=allowed_weekdays)
            case Frequency.DAILY:
                return DailyRepeat(interval=interval)
            case _:
                raise BusinessRuleViolationException(f"Frequency must be from 0 (Yearly) to 3 (Daily).")
