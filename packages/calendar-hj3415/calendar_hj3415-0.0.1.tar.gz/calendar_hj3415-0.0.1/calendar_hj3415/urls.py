from django.urls import path
from .views import MonthPartialView

app_name = "calendar_hj3415"

urlpatterns = [
    path("month/<int:year>/<int:month>/", MonthPartialView.as_view(), name="month"),
]