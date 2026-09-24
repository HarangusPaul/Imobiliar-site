"""URL fragments exported by the properties app, one list per API zone."""

from django.urls import path

from apps.properties.api.views.dashboard import (
    DashboardPropertyCreateView,
    DashboardPropertyListView,
)
from apps.properties.api.views.public import PublicPropertyDetailView, PublicPropertyListView

public_urlpatterns = [
    path("", PublicPropertyListView.as_view(), name="property-list"),
    path("<slug:slug>/", PublicPropertyDetailView.as_view(), name="property-detail"),
]

dashboard_urlpatterns = [
    path("", DashboardPropertyListView.as_view(), name="property-list"),
    path("create/", DashboardPropertyCreateView.as_view(), name="property-create"),
]

client_urlpatterns: list = []
