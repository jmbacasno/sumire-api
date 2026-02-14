from datetime import datetime
from dateutil.relativedelta import relativedelta, weekday, MO, TU, WE, TH, FR, SA, SU
from typing import Optional, List

from domain.enums import RepeatInterval
from domain.constants import START_WEEKDAY

def get_start_date_of_current_week(
    reference_date: datetime,
    start_weekday: weekday = START_WEEKDAY
) -> datetime:
    """Get the start date of the current week of the reference date"""
    return reference_date + relativedelta(weekday=start_weekday(-1))

def find_next_due_date(
    due_date: datetime,
    repeat_interval: RepeatInterval,
    repeat_factor: int = 1,
    repeat_allowed_weekdays: List[weekday] = [],
    start_weekday: weekday=SU
) -> datetime:
    """Find the next due date based on repeat configurations"""
    match repeat_interval:
        case RepeatInterval.DAYS:
            return due_date + relativedelta(days=repeat_factor)
        
        case RepeatInterval.MONTHS:
            return due_date + relativedelta(months=repeat_factor)
        
        case RepeatInterval.YEARS:
            return due_date + relativedelta(years=repeat_factor)

        case RepeatInterval.WEEKS:
            # Note: allowed_weekdays is a list of weekdays and must be sorted
            if len(repeat_allowed_weekdays) == 0:
                raise ValueError("Repeat allowed weekdays cannot be empty for weekly repeats")
            
            # Get start of current week
            start_date_of_current_week = get_start_date_of_current_week(due_date, start_weekday=start_weekday)
            last_date_of_current_week = start_date_of_current_week + relativedelta(days=6)

            # Check current week
            for day in repeat_allowed_weekdays:
                allowed_date_of_current_week = start_date_of_current_week + relativedelta(weekday=day)
                if allowed_date_of_current_week > due_date and allowed_date_of_current_week <= last_date_of_current_week:
                    return allowed_date_of_current_week

            # Proceed to the next week
            start_date_of_next_week = start_date_of_current_week + relativedelta(weeks=repeat_factor)
            first_allowed_weekday = repeat_allowed_weekdays[0]
            first_allowed_date_of_next_week = start_date_of_next_week + relativedelta(weekday=first_allowed_weekday)
            return first_allowed_date_of_next_week
        
        case _:
            return None
