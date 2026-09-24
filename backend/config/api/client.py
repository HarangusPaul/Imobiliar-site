"""Client zone: actions performed by an authenticated end user on their own
account.

Authentication endpoints live here rather than in the public zone because they
establish and tear down a session - they are account actions, not website data.
"""

from django.urls import include, path

from apps.accounts.api import urls as accounts_urls

app_name = "client"

urlpatterns = [
    path("auth/", include(accounts_urls.auth_urlpatterns)),
    # Reserved for saved properties, saved searches, alerts and the client's
    # own requests. See docs/architecture.md, "Deferred features".
]
