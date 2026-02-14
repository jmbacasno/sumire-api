from enum import IntEnum

class RepeatType(IntEnum):
    DAILY = 1
    WEEKDAYS = 2
    WEEKLY = 3
    MONTHLY = 4
    YEARLY = 5
    CUSTOM = 6

class RepeatInterval(IntEnum):
    DAYS = 1
    WEEKS = 2
    MONTHS = 3
    YEARS = 4
