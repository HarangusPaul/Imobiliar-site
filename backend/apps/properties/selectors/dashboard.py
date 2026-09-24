"""Read-side queries for the dashboard.

Separate from `search.py` because the dashboard sees a different universe:
drafts, archived listings and soft-deleted rows are visible here under the
right capability, and never in the public search.
"""

from __future__ import annotations

from django.db.models import QuerySet

from apps.access.policy import Capability
from apps.access.selectors.roles import has_capability
from apps.properties.models import Property


def dashboard_property_list(user, *, status: str = "", search: str = "") -> QuerySet[Property]:
    """What this staff member or agent is allowed to see in the dashboard.

    An agent sees their own portfolio; somebody with `properties.view_all`
    sees everything. The scoping happens here, not in the view, so no
    endpoint can forget it.
    """
    queryset = Property.objects.select_related("address__city", "agent", "cover_image")

    if not has_capability(user, Capability.PROPERTY_VIEW_ALL):
        queryset = queryset.filter(agent=user)

    if status:
        queryset = queryset.filter(publication_status=status)
    if search:
        queryset = queryset.filter(title__icontains=search) | queryset.filter(
            reference_code__iexact=search
        )

    return queryset.order_by("-updated_at")


def get_for_edit(user, *, uuid: str) -> Property | None:
    """Fetch one listing, scoped to what the caller may edit."""
    queryset = Property.objects.select_related("address", "agent").prefetch_related("features")
    if not has_capability(user, Capability.PROPERTY_EDIT_ANY):
        queryset = queryset.filter(agent=user)
    return queryset.filter(uuid=uuid).first()
