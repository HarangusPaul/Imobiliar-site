"""Lead status flow and assignment.

The transition table below is the whole reason this module exists. A lead
marked spam is terminal; a closed lead can be reopened only by moving it back
to qualified; nothing skips straight from new to closed without a record.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from core.api.exceptions import ConflictError, NotAllowedError
from core.contracts.analytics import AnalyticsEvent
from core.contracts.notification import (
    NotificationChannel,
    NotificationMessage,
    NotificationRecipient,
)
from core.contracts.registry import analytics_service, notification_service

from apps.access.policy import Capability
from apps.access.selectors.roles import has_capability
from apps.leads.models import Lead, LeadNote, LeadStatus

ALLOWED_STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    LeadStatus.NEW: frozenset({LeadStatus.CONTACTED, LeadStatus.QUALIFIED,
                               LeadStatus.CLOSED, LeadStatus.SPAM}),
    LeadStatus.CONTACTED: frozenset({LeadStatus.QUALIFIED, LeadStatus.CLOSED, LeadStatus.SPAM}),
    LeadStatus.QUALIFIED: frozenset({LeadStatus.CONTACTED, LeadStatus.CLOSED}),
    LeadStatus.CLOSED: frozenset({LeadStatus.QUALIFIED}),
    LeadStatus.SPAM: frozenset(),
}


class InvalidLeadTransitionError(ConflictError):
    code = "invalid_lead_transition"


@transaction.atomic
def change_status(lead: Lead, *, target: str, actor, note: str = "") -> Lead:
    previous = lead.status
    if previous == target:
        return lead
    if target not in ALLOWED_STATUS_TRANSITIONS.get(previous, frozenset()):
        raise InvalidLeadTransitionError(f"A lead cannot move from {previous} to {target}.")

    lead.status = target
    fields = ["status", "updated_at"]

    if target == LeadStatus.CONTACTED and lead.first_response_at is None:
        lead.first_response_at = timezone.now()
        fields.append("first_response_at")
    if target == LeadStatus.CLOSED:
        lead.closed_at = timezone.now()
        fields.append("closed_at")

    lead.save(update_fields=fields)

    LeadNote.objects.create(
        lead=lead,
        author=actor,
        body=note or f"Status changed from {previous} to {target}.",
        is_system=not note,
    )
    _record(lead, action=f"lead.{target}", actor=actor,
            metadata={"from": previous, "to": target})
    analytics_service().track(
        AnalyticsEvent(name=f"lead.{target}", properties={"lead_id": str(lead.uuid)})
    )
    return lead


@transaction.atomic
def assign_lead(lead: Lead, *, assignee, actor, system: bool = False, note: str = "") -> Lead:
    """Hand a lead to somebody.

    `system=True` is the automatic path taken at intake, which has no human
    actor and therefore skips the capability check.
    """
    if not system and not has_capability(actor, Capability.LEAD_ASSIGN):
        raise NotAllowedError("Your role cannot assign leads.")

    previous = lead.assigned_to
    if previous == assignee:
        return lead

    lead.assigned_to = assignee
    lead.assigned_at = timezone.now() if assignee else None
    lead.save(update_fields=["assigned_to", "assigned_at", "updated_at"])

    LeadNote.objects.create(
        lead=lead,
        author=actor,
        body=note or f"Assigned to {assignee.get_full_name() if assignee else 'nobody'}.",
        is_system=system or not note,
    )
    _record(lead, action="lead.assigned", actor=actor,
            metadata={"assignee": str(getattr(assignee, "uuid", "")) if assignee else None})

    if assignee and not system:
        _notify_assignee(lead, assignee)
    return lead


@transaction.atomic
def add_note(lead: Lead, *, body: str, actor) -> LeadNote:
    if not has_capability(actor, Capability.LEAD_RESPOND):
        raise NotAllowedError("Your role cannot respond to leads.")
    return LeadNote.objects.create(lead=lead, author=actor, body=body.strip())


def _notify_assignee(lead: Lead, assignee) -> None:
    """This app decides a notification is warranted; delivery is a contract."""
    if not assignee.phone_number:
        return
    transaction.on_commit(
        lambda: notification_service().send(
            NotificationMessage(
                channel=NotificationChannel.SMS,
                recipient=NotificationRecipient(
                    address=assignee.phone_number, display_name=assignee.get_full_name()
                ),
                subject="A lead was assigned to you",
                body=f"{lead.full_name} ({lead.phone_number}) - {lead.get_kind_display()}",
                kind="lead.assigned",
                metadata={"lead_id": str(lead.uuid)},
            )
        )
    )


def _record(lead: Lead, *, action: str, actor, metadata: dict) -> None:
    from apps.audit.services.recording import record_event

    record_event(actor=actor, action=action, target=lead, metadata=metadata)
