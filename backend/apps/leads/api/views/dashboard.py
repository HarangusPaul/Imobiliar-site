"""Dashboard lead endpoints.

GET /api/v1/dashboard/leads/
"""

from __future__ import annotations

from rest_framework.generics import ListAPIView

from core.api.pagination import DefaultPageNumberPagination
from core.permissions import IsAuthenticatedAndActive

from apps.access.permissions import HasCapability, IsDashboardUser
from apps.access.policy import Capability
from apps.leads.api.serializers.dashboard import DashboardLeadListSerializer
from apps.leads.selectors.inbox import dashboard_inbox, status_counts


class DashboardLeadListView(ListAPIView):
    permission_classes = [IsAuthenticatedAndActive, IsDashboardUser, HasCapability]
    required_capability = Capability.LEAD_VIEW_OWN
    serializer_class = DashboardLeadListSerializer
    pagination_class = DefaultPageNumberPagination

    def get_queryset(self):
        return dashboard_inbox(
            self.request.user,
            status=self.request.query_params.get("status", ""),
            assigned=self.request.query_params.get("assigned", ""),
        )

    def paginate_queryset(self, queryset):
        """Attach inbox counts so the dashboard badges need no second call."""
        page = super().paginate_queryset(queryset)
        self.paginator.extra_meta = {"counts": status_counts(self.request.user)}
        return page
