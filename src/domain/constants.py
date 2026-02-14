from dateutil.relativedelta import relativedelta, weekday, MO, TU, WE, TH, FR, SA, SU
from typing import List

START_WEEKDAY: weekday = SU
WEEKDAYS: List[weekday] = [MO, TU, WE, TH, FR]
DAY_NAMES: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
