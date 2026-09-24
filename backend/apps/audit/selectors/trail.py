"""Read-side queries for the audit trail."""

from __future__ import annotations

from django.db.models import QuerySet

from apps.audit.models import AuditEvent


def for_target(instance) -> QuerySet[AuditEvent]:
    """Everything that happened to one object."""
    meta = instance._meta
    return AuditEvent.objects.filter(
        target_app=meta.app_label,
        target_model=meta.model_name,
        target_uuid=getattr(instance, "uuid", None),
    ).select_related("actor")


def for_actor(user) -> QuerySet[AuditEvent]:
    return AuditEvent.objects.filter(actor=user).order_by("-created_at")


def for_request(request_id: str) -> QuerySet[AuditEvent]:
    """Everything that happened during one request."""
    return AuditEvent.objects.filter(request_id=request_id).order_by("created_at")


def recent(limit: int = 100) -> QuerySet[AuditEvent]:
    return AuditEvent.objects.select_related("actor").order_by("-created_at")[:limit]
