"""URL patterns for report endpoints."""

from django.urls import path

from .report_views import AllHabitsReportView, GeneralReportView, HabitReportView

urlpatterns = [
    path("general/", GeneralReportView.as_view(), name="report-general"),
    path("all/", AllHabitsReportView.as_view(), name="report-all"),
    path("habit/<uuid:pk>/", HabitReportView.as_view(), name="report-habit"),
]
