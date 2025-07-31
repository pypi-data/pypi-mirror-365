import calendar
import datetime as dt
from dataclasses import dataclass

@dataclass
class MonthRange:
    start: dt.date
    end: dt.date
    month_start: dt.date
    month_end: dt.date

def month_context(year: int, month: int, firstweekday: int = 0):
    cal = calendar.Calendar(firstweekday=firstweekday)  # 0=월요일 시작
    weeks = cal.monthdatescalendar(year, month)
    flat = [d for w in weeks for d in w]
    rng = MonthRange(
        start=flat[0],
        end=flat[-1],
        month_start=dt.date(year, month, 1),
        month_end=dt.date(year, month, calendar.monthrange(year, month)[1]),
    )
    return weeks, rng

