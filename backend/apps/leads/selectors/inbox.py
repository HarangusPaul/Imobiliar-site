"""Read-side queries for the lead inbox."""

from __future__ import annotations

from django.db.models import Count, QuerySet

from apps.access.policy import Capability
from apps.access.selectors.roles import has_capability
from apps.leads.models import Lead, LeadStatus


def dashboard_inbox(user, *, status: str = "", assigned: str = "") -> QuerySet[Lead]:
    """The inbox as this user is allowed to see it.

    An agent sees leads assigned to them or attached to their own listings;
    somebody with leads.view_all sees everything. Scoping happens here so no
    view can leak another agent's pipeline.
    """
    queryset = Lead.objects.select_related(
        "property", "development", "assigned_to", "user"
    )

    if not has_capability(user, Capability.LEAD_VIEW_ALL):
        queryset = queryset.filter(assigned_to=user) | queryset.filter(property__agent=user)
        queryset = queryset.distinct()

    if status:
        queryset = queryset.filter(status=status)
    if assigned == "me":
        queryset = queryset.filter(assigned_to=user)
    elif assigned == "none":
        queryset = queryset.filter(assigned_to__isnull=True)

    return queryset.order_by("-created_at")


def get_for_user(user, *, uuid: str) -> Lead | None:
    return dashboard_inbox(user).prefetch_related("notes__author").filter(uuid=uuid).first()


def status_counts(user) -> dict[str, int]:
    """Badge counts for the dashboard navigation."""
    rows = dashboard_inbox(user).values("status").annotate(total=Count("id"))
    counts = {row["status"]: row["total"] for row in rows}
    counts["open"] = sum(
        counts.get(s, 0) for s in (LeadStatus.NEW, LeadStatus.CONTACTED, LeadStatus.QUALIFIED)
    )
    return counts


def leads_for_property(prop) -> QuerySet[Lead]:
    return Lead.objects.filter(property=prop).select_related("assigned_to").order_by("-created_at")
