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
class Task:
    title: str = None
    
    note: Optional[str] = None
    steps: List[Step] = field(default_factory=list)
    due_date: Optional[datetime] = None
    is_completed: bool = False
    is_important: bool = False
    
    repeat_type: Optional[RepeatType] = None
    repeat_interval: Optional[RepeatInterval] = None
    repeat_factor: Optional[int] = None
    repeat_allowed_days: List[weekday] = field(default_factory=list)

    # Auto-generated
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def is_due(self):
        """Check if the task is due"""
        if not self.due_date:
            return False
        return datetime.now() >= self.due_date
    
    def set_due_date(self, due_date: Optional[datetime] = None):
        """Set the due date"""
        if due_date is None:
            self.due_date = None
            self.clear_repeat_config()
            return
        
        self.due_date = due_date

        if self.repeat_type:
            self.set_repeat(
                self.repeat_type,
                self.repeat_interval,
                self.repeat_factor,
                self.repeat_allowed_days
            )
    
    def clear_repeat_config(self):
        """Clear repeat configurations"""
        self.repeat_type = None
        self.repeat_interval = None
        self.repeat_factor = None
        self.repeat_allowed_days = None

    def set_repeat_config(self, repeat_interval: RepeatInterval, repeat_factor: int, repeat_allowed_days: List[weekday] = None):
        """Set repeat configurations"""
        if repeat_interval:
            self.repeat_interval = repeat_interval
        else:
            raise ValueError("Custom repeat interval cannot be empty for repeats")
        
        if repeat_factor:
            self.repeat_factor = repeat_factor
        else:
            raise ValueError("Custom repeat factor cannot be empty for repeats")
        
        if repeat_interval == RepeatInterval.WEEKS:
            if not repeat_allowed_days:
                raise ValueError("Custom repeat allowed days cannot be empty for weekly repeats")
            self.repeat_allowed_days = repeat_allowed_days
        else:
            self.repeat_allowed_days = None
    
    def set_repeat(
        self,
        repeat_type: RepeatType,
        repeat_interval: Optional[RepeatInterval] = None,
        repeat_factor: Optional[int] = None,
        repeat_allowed_days: Optional[List[int]] = None
    ):
        """Set repeat"""

        # Set due date to current date if not set
        if not self.due_date:
            self.due_date = datetime.now()

        self.repeat_type = repeat_type
        
        match self.repeat_type:
            case RepeatType.DAILY:
                self.set_repeat_config(RepeatInterval.DAYS, 1)
            
            case RepeatType.WEEKDAYS:
                self.set_repeat_config(RepeatInterval.WEEKS, 1, WEEKDAYS)

                # Set due date to a Monday if due date is not a weekday
                if self.due_date.weekday() not in WEEKDAYS:
                    self.due_date = find_next_due_date(
                        self.due_date, RepeatInterval.WEEKS,
                        1,
                        [MO],
                        start_weekday=START_WEEKDAY
                    )
            
            case RepeatType.WEEKLY:
                current_weekday = weekday(self.due_date.weekday())
                self.set_repeat_config(RepeatInterval.WEEKS, 1, [current_weekday])
            
            case RepeatType.MONTHLY:
                self.set_repeat_config(RepeatInterval.MONTHS, 1)
            
            case RepeatType.YEARLY:
                self.set_repeat_config(RepeatInterval.YEARS, 1)
            
            case RepeatType.CUSTOM:
                self.set_repeat_config(repeat_interval, repeat_factor, repeat_allowed_days)
    
    def complete(self):
        """Mark task as completed"""
        self.is_completed = True
        new_repeating_task = None

        # Create duplicate recurring task if repeat is enabled
        if self.repeat_type:
            next_due_date = find_next_due_date(
                self.due_date,
                self.repeat_interval,
                self.repeat_factor,
                self.repeat_allowed_days,
            )

            new_repeating_task = Task(
                title=self.title,
                note=self.note,
                due_date=next_due_date,
                is_completed=False,
                is_important=self.is_important,
                repeat_type=self.repeat_type,
                repeat_interval=self.repeat_interval,
                repeat_factor=self.repeat_factor,
                repeat_allowed_days=self.repeat_allowed_days
            )
        
        self.clear_repeat_config()
        return new_repeating_task
    
    def uncomplete(self):
        """Mark task as uncompleted"""
        self.is_completed = False
    
    def get_repeat_description(self):
        """Get repeat description"""
        if not self.repeat_type:
            return None
        
        match self.repeat_interval:
            case RepeatInterval.DAYS:
                if self.repeat_factor == 1:
                    return "Daily"
                else:
                    return f"Every {self.repeat_factor} days"
            
            case RepeatInterval.WEEKS:
                interval_description = (
                    "Weekly"
                    if self.repeat_factor == 1
                    else f"Every {self.repeat_factor} weeks"
                )
                days_description = (
                    "Weekdays"
                    if self.repeat_allowed_days == WEEKDAYS
                    else ", ".join([DAY_NAMES[weekday.weekday] for weekday in self.repeat_allowed_days])
                )
                return f"{interval_description} on {days_description}"
            
            case RepeatInterval.MONTHS:
                if self.repeat_factor == 1:
                    return "Monthly"
                else:
                    return f"Every {self.repeat_factor} months"
            
            case RepeatInterval.YEARS:
                if self.repeat_factor == 1:
                    return "Yearly"
                else:
                    return f"Every {self.repeat_factor} years"
    
    def add_step(self, step: Step):
        """Add step to task"""
        self.steps.append(step)

    def remove_step(self, step_id: UUID):
        """Remove step from task"""
        pass

    def update_step(self, step_id: UUID, step_data: dict):
        """Update step in task"""
        pass
