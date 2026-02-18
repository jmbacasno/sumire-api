from dataclasses import dataclass, field
from typing import Optional, List, ClassVar
from datetime import datetime
from dateutil.relativedelta import relativedelta, weekday, MO
from uuid import UUID, uuid4

from domain.constants import START_WEEKDAY, WEEKDAYS, DAY_NAMES
from domain.enums import RepeatType, RepeatInterval
from domain.utils import find_next_due_date, get_start_date_of_current_week

from typing import Optional, List, Set

@dataclass
class Step:
    description: str

    # Auto-generated
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """Validate at creation"""

        if not self.description and len(self.description.strip()) == 0:
            raise ValueError(
                "Description cannot be empty. Step must have a description."
            )

    def change_description(self, new_description: str):
        """Change step's description with validation"""
        if not new_description and len(new_description.strip()) == 0:
            raise ValueError(
                "Cannot change description to empty value. Description must contain at least one character."
            )
        self.description = new_description

    def convert_to_task(self):
        """Convert step to task"""
        return Task(description=self.description)
    
    def __str__(self):
        return self.description

@dataclass
class Repeat:
    interval: RepeatInterval
    factor: int
    allowed_weekdays: Set[int] | None = None

    def __post_init__(self):
        """Validate at creation"""

        if self.interval is None:
            raise ValueError(
                "Type cannot be empty. Repeat must have a type."
            )

        if self.factor is None:
            raise ValueError(
                "Factor cannot be empty. Repeat must have a factor."
            )

        if self.factor < 1:
            raise ValueError(
                "Factor cannot be less than 1."
            )

        if self.interval == RepeatInterval.WEEKS and not self.allowed_weekdays:
            raise ValueError(
                "Allowed weekdays cannot be empty for weekly repeats."
            )

    def change_interval(self, new_interval: RepeatInterval):
        """Change repeat's interval with validation"""
        if new_interval is None:
            raise ValueError(
                "Cannot change interval to empty value."
            )
        self.interval = new_interval

    def change_factor(self, new_factor: int):
        """Change repeat's factor with validation"""
        if new_factor is None:
            raise ValueError(
                "Cannot change factor to empty value."
            )

        if new_factor < 1:
            raise ValueError(
                "Cannot change factor to less than 1."
            )

        self.factor = new_factor

    def change_allowed_days(self, new_allowed_weekdays: List[int]):
        """Change repeat's allowed days with validation"""
        if self.interval == RepeatInterval.WEEKS and not new_allowed_weekdays:
            raise ValueError(
                "Cannot change allowed weekdays to empty value for weekly repeats."
            )
        
        self.allowed_weekdays = new_allowed_weekdays

    def find_next_date(
        self,
        reference_date: datetime,
        start_weekday: weekday=START_WEEKDAY
    ) -> datetime:
        """Find the next due date based on repeat configurations"""
        match self.interval:
            case RepeatInterval.DAYS:
                return reference_date + relativedelta(days=self.factor)

            case RepeatInterval.MONTHS:
                return reference_date + relativedelta(months=self.factor)

            case RepeatInterval.YEARS:
                return reference_date + relativedelta(years=self.factor)

            case RepeatInterval.WEEKS:
                start_date_of_current_week = get_start_date_of_current_week(reference_date, start_weekday=start_weekday)
                last_date_of_current_week = start_date_of_current_week + relativedelta(days=6)

                # Scan current week
                for days in range(1, 6 + 1):
                    date_of_current_week = start_date_of_current_week + relativedelta(days=days)
                    if (date_of_current_week.weekday() in self.allowed_weekdays
                            and date_of_current_week > reference_date
                            and date_of_current_week <= last_date_of_current_week):
                        return date_of_current_week

                start_date_of_next_week = start_date_of_current_week + relativedelta(weeks=self.factor)
                last_date_of_next_week = start_date_of_next_week + relativedelta(days=6)

                # Scan next week
                for days in range(1, 6 + 1):
                    date_of_next_week = start_date_of_next_week + relativedelta(days=days)
                    if (date_of_next_week.weekday() in self.allowed_weekdays
                            and date_of_next_week > reference_date
                            and date_of_next_week <= last_date_of_next_week):
                        return date_of_next_week

            case _:
                return None

    def __str__(self):
        match self.interval:
            case RepeatInterval.DAYS:
                if self.factor == 1:
                    return "Daily"
                else:
                    return f"Every {self.factor} days"

            case RepeatInterval.WEEKS:
                interval_description = (
                    "Weekly"
                    if self.factor == 1
                    else f"Every {self.factor} weeks"
                )
                weekdays_description = (
                    "Weekdays"
                    if self.allowed_weekdays == WEEKDAYS
                    else ", ".join([DAY_NAMES[weekday] for weekday in self.allowed_weekdays])
                )
                return f"{interval_description} on {weekdays_description}"

            case RepeatInterval.MONTHS:
                if self.factor == 1:
                    return "Monthly"
                else:
                    return f"Every {self.factor} months"

            case RepeatInterval.YEARS:
                if self.factor == 1:
                    return "Yearly"
                else:
                    return f"Every {self.factor} years"

@dataclass
class Task:
    description: str

    note: str | None = None
    due_date: datetime | None = None
    is_completed: bool = False
    is_important: bool = False

    repeat: Repeat | None = None

    # Auto-generated
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """Validate at creation"""

        if not self.description and len(self.description.strip()) == 0:
            raise ValueError(
                "Title cannot be empty. Task must have a title."
            )

        # Update due date if repeat is enabled
        if self.repeat:
            self.set_repeat(self.repeat)

    def change_description(self, new_description: str):
        """Change task's description with validation"""
        if not new_description and len(new_description.strip()) == 0:
            raise ValueError(
                "Cannot change description to empty value. Description must contain at least one character."
            )
        
        self.description = new_description
    
    def is_due(self):
        """Check if the task is due"""
        if not self.due_date:
            return False
        return datetime.now() >= self.due_date
    
    def set_due_date(self, due_date: datetime | None = None):
        """Set the due date"""
        if due_date is None:
            self.due_date = None
            self.repeat = None
            return
        
        self.due_date = due_date

        if self.repeat:
            # Special cases for Week Repeats
            if self.repeat.interval == RepeatInterval.WEEKS:
                # WEEKLY - SINGLE DAY
                if len(self.repeat.allowed_weekdays) == 1:
                    self.repeat.allowed_weekdays = [self.due_date.weekday()]
                    print("Set allowed weekdays to: ", self.repeat.allowed_weekdays)
                
                else:
                    # WEEKLY - WEEKDAYS (Monday to Friday)
                    if self.repeat.allowed_weekdays == WEEKDAYS:
                        self.due_date = self.repeat.find_next_date(self.due_date)
                        print("Set due date to: ", self.due_date)
                    # WEEKLY - MULTIPLE DAYS (Unspecified)
                    else:
                        due_date_weekday = self.due_date.weekday()
                        if due_date_weekday not in self.repeat.allowed_weekdays:
                            self.repeat.change_allowed_days(
                                self.repeat.allowed_weekdays | {due_date_weekday}
                            )
                            print("Set allowed weekdays to: ", self.repeat.allowed_weekdays)

    def set_repeat(self, repeat: Repeat | None = None):
        self.repeat = repeat

        if not self.due_date:
            self.due_date = datetime.now()
            print("Set due date to: ", self.due_date)

        if self.repeat:
            # Special cases for Week Repeats
            if self.repeat.interval == RepeatInterval.WEEKS:
                if self.due_date.weekday() in self.repeat.allowed_weekdays:
                    return
                
                # Get Repeat where factor is 1
                repeat = Repeat(
                    interval=self.repeat.interval,
                    factor=1,
                    allowed_weekdays=self.repeat.allowed_weekdays
                )
                self.due_date = repeat.find_next_date(self.due_date)
                print("Set due date to: ", self.due_date)
    
    def complete(self):
        """Mark task as completed"""
        self.is_completed = True
        new_repeating_task = None

        # Create duplicate task if repeat is enabled
        if self.repeat:
            new_repeating_task = Task(
                description=self.description,
                note=self.note,
                due_date=self.repeat.find_next_date(self.due_date),
                is_completed=False,
                is_important=self.is_important,
                repeat=self.repeat
            )
        
        self.repeat = None
        return new_repeating_task

    def __str__(self):
        if self.due_date:
            return f"{self.description} (Due: {self.due_date.strftime('%Y-%m-%d')})"
        else:
            return self.description