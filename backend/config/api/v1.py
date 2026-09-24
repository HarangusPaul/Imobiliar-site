"""Version 1 of the API, split into four access zones.

The zone is part of the URL because it is part of the contract. A resource
exposed publicly and the same resource exposed to the dashboard are different
endpoints with different serializers, different query shapes and different
permissions - never one endpoint that changes behaviour based on who is asking.

    /api/v1/public/    unauthenticated website data
    /api/v1/client/    authenticated end-user account actions
    /api/v1/dashboard/ agent and staff operations
    /api/v1/internal/  restricted internal functions (closed by default)
"""

from django.urls import include, path

app_name = "v1"

urlpatterns = [
    path("public/", include(("config.api.public", "public"), namespace="public")),
    path("client/", include(("config.api.client", "client"), namespace="client")),
    path("dashboard/", include(("config.api.dashboard", "dashboard"), namespace="dashboard")),
    path("internal/", include(("config.api.internal", "internal"), namespace="internal")),
]
