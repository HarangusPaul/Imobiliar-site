"""URL fragments exported by the developments app."""

from django.urls import path

from apps.developments.api.views.public import (
    PublicDevelopmentDetailView,
    PublicDevelopmentListView,
)

public_urlpatterns = [
    path("", PublicDevelopmentListView.as_view(), name="development-list"),
    path("<slug:slug>/", PublicDevelopmentDetailView.as_view(), name="development-detail"),
]

# Dashboard development management is scaffolded in the next phase; Django
# Admin covers it meanwhile.
dashboard_urlpatterns: list = []
client_urlpatterns: list = []
