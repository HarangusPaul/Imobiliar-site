"""URL fragments exported by the leads app."""

from django.urls import path

from apps.leads.api.views.dashboard import DashboardLeadListView
from apps.leads.api.views.public import PublicLeadCreateView

public_urlpatterns = [
    path("", PublicLeadCreateView.as_view(), name="lead-create"),
]

dashboard_urlpatterns = [
    path("", DashboardLeadListView.as_view(), name="lead-list"),
]

client_urlpatterns: list = []
