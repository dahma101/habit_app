"""URL patterns for dashboard endpoints."""

from django.urls import path

from .dashboard_views import DashboardListView, DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("<uuid:list_id>/", DashboardListView.as_view(), name="dashboard-list"),
]
