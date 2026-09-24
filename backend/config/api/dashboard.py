"""Dashboard zone: agent and staff operations backing the React dashboard.

Every view in this zone is role-protected via ``apps.access``. Scaffolding in
this phase is intentionally thin, but the permission seam is real from the
start so that adding an endpoint cannot accidentally ship it unguarded.
"""

from django.urls import include, path

from apps.leads.api import urls as leads_urls
from apps.properties.api import urls as properties_urls

app_name = "dashboard"

urlpatterns = [
    path("properties/", include(properties_urls.dashboard_urlpatterns)),
    path("leads/", include(leads_urls.dashboard_urlpatterns)),
]
