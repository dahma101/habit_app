"""URL patterns for habit CRUD and check-in endpoints."""

from django.urls import path

from .views import HabitCheckInView, HabitDetailView, HabitListView

urlpatterns = [
    path("", HabitListView.as_view(), name="habit-list"),
    path("<uuid:pk>/", HabitDetailView.as_view(), name="habit-detail"),
    path("<uuid:pk>/check-in/", HabitCheckInView.as_view(), name="habit-checkin"),
]
