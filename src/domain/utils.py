from typing import Set

from domain.enums import RepeatFrequency

def num_to_frequency(n: int | None) -> RepeatFrequency | None:
    if n is None:
        return None
    return RepeatFrequency(n)

def str_weekdays_to_set_weekdays(str_weekdays: str | None) -> Set[int] | None:
    if str_weekdays is None or len(str_weekdays) == 0:
        return None
    return set(map(int, str_weekdays))

def set_weekdays_to_str_weekdays(set_weekdays: Set[int] | None) -> str | None:
    if set_weekdays is None or len(set_weekdays) == 0:
        return None
    return ",".join(map(str, set_weekdays))