"""URL patterns for habit list endpoints."""

from django.urls import path

from .views import ListDetailView, ListListView

urlpatterns = [
    path("", ListListView.as_view(), name="list-list"),
    path("<uuid:pk>/", ListDetailView.as_view(), name="list-detail"),
]
