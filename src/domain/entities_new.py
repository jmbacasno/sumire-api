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

class Repeat:
    def __init__(self, frequency: Frequency, interval: int):
        if frequency is None:
            raise InvalidEntityStateException(
                "Frequency cannot be empty. Repeat must have a frequency."
            )

        if interval is None:
            raise InvalidEntityStateException(
                "Interval cannot be empty. Repeat must have an interval."
            )

        if interval < 1:
            raise InvalidEntityStateException(
                f"Invalid interval: {interval}. Interval must be a positive integer."
            )

        self.frequency = frequency
        self.interval = interval

    def get_next_date(self, reference_date: datetime) -> datetime:
        """Get next date."""
        repeat_rrule = rrule(
            dtstart=reference_date,
            freq=self.frequency,
            interval=self.interval,
            wkst=START_WEEKDAY,
        )
        return repeat_rrule.after(reference_date)

class YearlyRepeat(Repeat):
    def __init__(self, interval: int):
        super().__init__(Frequency.YEARLY, interval)

    def __str__(self):
        if self.interval == 1:
            return "Repeat yearly"
        return f"Repeat every {self.interval} years"

class MonthlyRepeat(Repeat):
    def __init__(self, interval: int):
        super().__init__(Frequency.MONTHLY, interval)

    def __str__(self):
        if self.interval == 1:
            return "Repeat monthly"
        return f"Repeat every {self.interval} months"

class WeeklyRepeat(Repeat):
    def __init__(self, interval: int, allowed_weekdays: Set[int] | str):
        super().__init__(Frequency.WEEKLY, interval)
        if allowed_weekdays is None or len(allowed_weekdays) == 0:
            raise InvalidEntityStateException(
                "Allowed weekdays cannot be empty. Repeat must have allowed weekdays."
            )

        for weekday in allowed_weekdays:
            if weekday not in "0123456":
                raise InvalidEntityStateException(
                    f"Invalid allowed weekdays: {allowed_weekdays}. Allowed weekdays must be string of integers from 0 (Monday) to 6 (Sunday)."
                )

        # Get a set of allowed weekdays from string
        self.allowed_weekdays_set = set(map(int, allowed_weekdays))
        # Get a clean string of allowed weekdays from set
        self.allowed_weekdays = "".join(map(str, self.allowed_weekdays_set))

    def __str__(self):
        repeat_description = "Repeat weekly" if self.interval == 1 else f"Repeat every {self.interval} weeks"

        if self.allowed_weekdays == WEEKDAY_WEEKDAYS:
            weekdays_description = "weekdays"
        elif self.allowed_weekdays == WEEKEND_WEEKDAYS:
            weekdays_description = "weekends"
        else:
            weekdays_description = ", ".join(calendar.day_abbr[weekday] for weekday in self.allowed_weekdays_set)

        return f"{repeat_description} on {weekdays_description}"

    def get_next_date(self, reference_date: datetime) -> datetime:
        """Get next date."""
        weekly_repeat_rrule = rrule(
            dtstart=reference_date,
            freq=self.frequency,
            interval=self.interval,
            wkst=START_WEEKDAY,
            byweekday=self.allowed_weekdays_set
        )
        return weekly_repeat_rrule.after(reference_date)

class DailyRepeat(Repeat):
    def __init__(self, interval: int):
        super().__init__(Frequency.DAILY, interval)

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
                raise InvalidEntityStateException(f"Frequency must be from 0 (Yearly) to 3 (Daily).")
