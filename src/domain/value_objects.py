from enum import IntEnum
from typing import Set, Generator
from datetime import datetime
import calendar

from dateutil.rrule import rrule

class Frequency(IntEnum):
    YEARLY = 0
    MONTHLY = 1
    WEEKLY = 2
    DAILY = 3

class Weekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

START_WEEKDAY: Set[Weekday] = Weekday.SUNDAY
WEEKDAY_WEEKDAYS: Set[Weekday] = {Weekday.MONDAY, Weekday.TUESDAY, Weekday.WEDNESDAY, Weekday.THURSDAY, Weekday.FRIDAY}
WEEKEND_WEEKDAYS: Set[Weekday] = {Weekday.SATURDAY, Weekday.SUNDAY}

class Weekdays:
    def __init__(self, weekdays: Set[int]) -> None:
        if weekdays is None or len(weekdays) == 0:
            raise ValueError("Weekdays cannot be empty.")

        for weekday in weekdays:
            if weekday < Weekday.MONDAY or weekday > Weekday.SUNDAY:
                raise ValueError("Weekdays must be integers from 0 (Monday) to 6 (Sunday).")

        self.__weekdays = weekdays

    def is_weekdays(self) -> bool:
        return self.__weekdays == WEEKDAY_WEEKDAYS

    def is_weekends(self) -> bool:
        return self.__weekdays == WEEKEND_WEEKDAYS

    def to_string(self) -> str:
        return "".join(map(str, self.__weekdays))

    @classmethod
    def from_string(cls, weekdays_str: str) -> Weekdays:
        return cls(weekdays=set(map(int, weekdays_str)))

    def __iter__(self) -> Generator[int]:
        return iter(self.__weekdays)

    def __contains__(self, value: int) -> bool:
        return value in self.__weekdays

    def __str__(self) -> str:
        return ", ".join(calendar.day_abbr[weekday] for weekday in self.__weekdays)

class BaseRepeat:
    def __init__(self, frequency: Frequency, interval: int, weekdays_str: str | None = None) -> None:
        self.frequency = frequency
        self.interval = interval
        self.weekdays = Weekdays.from_string(weekdays_str) if weekdays_str is not None else None
        self.weekdays_str = self.weekdays.to_string() if self.weekdays is not None else None

    def get_next_date(self, reference_date: datetime) -> datetime:
        repeat_rrule = rrule(
            dtstart=reference_date,
            freq=self.frequency,
            interval=self.interval,
            wkst=START_WEEKDAY,
            byweekday=self.weekdays
        )
        return repeat_rrule.after(reference_date)

class NoRepeat(BaseRepeat):
    def __init__(self) -> None:
        super().__init__(frequency=None, interval=None, weekdays_str=None)

    def get_next_date(self, reference_date: datetime) -> None:
        return None

    def __str__(self) -> str:
        return "No repeat"

class Repeat(BaseRepeat):
    def __init__(self, frequency: int, interval: int, weekdays_str: str | None = None) -> None:
        if interval is None:
            raise ValueError("Interval cannot be empty.")
        if interval < 1:
            raise ValueError("Interval must be a positive integer.")

        super().__init__(frequency=frequency, interval=interval, weekdays_str=weekdays_str)

class YearlyRepeat(Repeat):
    def __init__(self, interval: int) -> None:
        super().__init__(frequency=Frequency.YEARLY, interval=interval, weekdays_str=None)

    def __str__(self) -> str:
        return "Repeat yearly" if self.interval == 1 else f"Repeat every {self.interval} years"

class MonthlyRepeat(Repeat):
    def __init__(self, interval: int) -> None:
        super().__init__(frequency=Frequency.MONTHLY, interval=interval, weekdays_str=None)

    def __str__(self) -> str:
        return "Repeat monthly" if self.interval == 1 else f"Repeat every {self.interval} months"

class WeeklyRepeat(Repeat):
    def __init__(self, interval: int, weekdays_str: str) -> None:
        if weekdays_str is None:
            raise ValueError("Weekdays cannot be empty.")

        super().__init__(frequency=Frequency.WEEKLY, interval=interval, weekdays_str=weekdays_str)

    def __str__(self) -> str:
        if self.interval == 1:
            repeat_description = "Repeat weekly"
        else:
            repeat_description = f"Repeat every {self.interval} weeks"

        if self.weekdays.is_weekdays():
            weekdays_description = "weekdays"
        elif self.weekdays.is_weekends():
            weekdays_description = "weekends"
        else:
            weekdays_description = str(self.weekdays)

        return f"{repeat_description} on {weekdays_description}"

class DailyRepeat(Repeat):
    def __init__(self, interval: int) -> None:
        super().__init__(frequency=Frequency.DAILY, interval=interval, weekdays_str=None)

    def __str__(self) -> str:
        return "Repeat daily" if self.interval == 1 else f"Repeat every {self.interval} days"

class RepeatManager:
    def __init__(self, due_date: datetime, frequency: int, interval: int, weekdays_str: str | None = None) -> None:
        if frequency is None:
            repeat = NoRepeat()
        else:
            if due_date is None:
                raise ValueError("Due date cannot be empty for repeats.") 

            match frequency:
                case Frequency.YEARLY:
                    repeat = YearlyRepeat(interval=interval)
                case Frequency.MONTHLY:
                    repeat = MonthlyRepeat(interval=interval)
                case Frequency.WEEKLY:
                    repeat = WeeklyRepeat(interval=interval, weekdays_str=weekdays_str)

                    if due_date.weekday() not in repeat.weekdays:
                        raise ValueError("Due date must be on one of the weekdays.")
                case Frequency.DAILY:
                    repeat = DailyRepeat(interval=interval)
                case _:
                    raise ValueError(f"Frequency must be integer from 0 (Yearly) to 3 (Daily).")

        self.repeat = repeat
        self.due_date = due_date

    def get_next_due_date(self) -> datetime | None:
        return self.repeat.get_next_date(self.due_date)

    def __str__(self) -> str:
        repeat_description = str(self.repeat)
        due_date_description = f"due on {self.due_date.strftime('%Y-%m-%d %H:%M:%S')}" if self.due_date else ""
        return " | ".join((repeat_description, due_date_description))
