"""Public zone: unauthenticated, cacheable, deliberately narrow.

Only published data is reachable here, and only through serializers designed
for public consumption. Anything whose answer depends on who is asking belongs
in the client or dashboard zone instead.
"""

from django.urls import include, path

from apps.developments.api import urls as developments_urls
from apps.leads.api import urls as leads_urls
from apps.properties.api import urls as properties_urls

app_name = "public"

urlpatterns = [
    path("properties/", include(properties_urls.public_urlpatterns)),
    path("developments/", include(developments_urls.public_urlpatterns)),
    path("leads/", include(leads_urls.public_urlpatterns)),
]
