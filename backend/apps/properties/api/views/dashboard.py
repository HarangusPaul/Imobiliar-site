"""Dashboard property endpoints.

GET  /api/v1/dashboard/properties/
POST /api/v1/dashboard/properties/

Scaffolding for this phase. The permission seam is real from the start: every
view states the capability it needs, and HasCapability fails closed when a
view forgets to.
"""

from __future__ import annotations

from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.pagination import DefaultPageNumberPagination
from core.api.responses import created
from core.permissions import IsAuthenticatedAndActive

from apps.access.permissions import HasCapability, IsDashboardUser
from apps.access.policy import Capability
from apps.properties.api.serializers.dashboard import (
    DashboardPropertyListSerializer,
    DashboardPropertyWriteSerializer,
)
from apps.properties.selectors.dashboard import dashboard_property_list
from apps.properties.services.listing import PropertyInput, create_property


class DashboardPropertyListView(ListAPIView):
    permission_classes = [IsAuthenticatedAndActive, IsDashboardUser]
    serializer_class = DashboardPropertyListSerializer
    pagination_class = DefaultPageNumberPagination

    def get_queryset(self):
        return dashboard_property_list(
            self.request.user,
            status=self.request.query_params.get("status", ""),
            search=self.request.query_params.get("q", "").strip(),
        )


class DashboardPropertyCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive, IsDashboardUser, HasCapability]
    required_capability = Capability.PROPERTY_CREATE

    def post(self, request: Request) -> Response:
        serializer = DashboardPropertyWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prop = create_property(PropertyInput(**serializer.validated_data), actor=request.user)
        return created(DashboardPropertyListSerializer(prop).data)
