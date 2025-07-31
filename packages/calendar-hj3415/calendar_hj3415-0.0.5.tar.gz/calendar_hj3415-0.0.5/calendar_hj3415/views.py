import datetime as dt
from django.shortcuts import render
from django.views import View
from .models import Event
from .utils import month_context
from . import models

class MonthPartialView(View):
    template_name = "calendar_hj3415/_month.html"

    def get(self, request, year: int, month: int):
        weeks, rng = month_context(year, month, firstweekday=0)  # 한국: 월요일 시작 자연스러움
        qs = (Event.objects
              .filter(start_date__lte=rng.end)
              .filter(models.models.Q(end_date__gte=rng.start) | models.models.Q(end_date__isnull=True)))
        events_by_date = {}
        for ev in qs.distinct():
            cur = max(ev.start_date, rng.start)
            end = min(ev.effective_end, rng.end)
            while cur <= end:
                events_by_date.setdefault(cur, []).append(ev)
                cur += dt.timedelta(days=1)

        ctx = {"weeks": weeks, "range": rng, "events_by_date": events_by_date}
        return render(request, self.template_name, ctx)