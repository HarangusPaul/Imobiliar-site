"""Lead intake: what happens when a contact form is submitted.

This module is the clearest illustration of the apps/services split in the
project. It decides:

  * that a lead has been created,
  * who should hear about it (the listing agent, or nobody yet),
  * what the message says.

It does not decide how that message travels, and contains no provider name.
Delivery goes through core.contracts.notification.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings
from django.db import transaction

from core.contracts.analytics import AnalyticsEvent
from core.contracts.notification import (
    NotificationChannel,
    NotificationMessage,
    NotificationRecipient,
)
from core.contracts.registry import analytics_service, notification_service
from core.logging import get_request_id
from core.validation import normalize_phone

from apps.leads.models import ContactPreference, Lead, LeadKind, LeadStatus


@dataclass(slots=True)
class LeadInput:
    full_name: str
    phone_number: str
    message: str = ""
    email: str = ""
    kind: str = LeadKind.GENERAL
    contact_preference: str = ContactPreference.ANY
    preferred_time: str = ""
    property_id: int | None = None
    development_id: int | None = None
    unit_id: int | None = None
    source_path: str = ""


@transaction.atomic
def submit_lead(data: LeadInput, *, user=None) -> Lead:
    """Record an enquiry and trigger the follow-up it deserves."""
    lead = Lead.objects.create(
        kind=data.kind,
        status=LeadStatus.NEW,
        full_name=data.full_name.strip(),
        phone_number=normalize_phone(
            data.phone_number, default_country_prefix=settings.ACCOUNTS_DEFAULT_PHONE_PREFIX
        ),
        email=data.email.strip().lower(),
        message=data.message.strip(),
        contact_preference=data.contact_preference,
        preferred_time=data.preferred_time.strip(),
        property_id=data.property_id,
        development_id=data.development_id,
        unit_id=data.unit_id,
        user=user if user and user.is_authenticated else None,
        source_path=data.source_path[:255],
        request_id=get_request_id(),
    )

    _auto_assign(lead)
    _notify_owner(lead)

    analytics_service().track(
        AnalyticsEvent(
            name="lead.created",
            actor_id=str(user.uuid) if user and user.is_authenticated else "",
            properties={"kind": lead.kind, "has_property": bool(lead.property_id)},
        )
    )
    return lead


def _auto_assign(lead: Lead) -> None:
    """A property enquiry belongs to that listing's agent.

    Anything else stays in the unassigned queue for staff to triage. This is a
    business rule and it lives here, not in a notification adapter.
    """
    if lead.property_id and lead.property.agent_id:
        from apps.leads.services.workflow import assign_lead

        assign_lead(lead, assignee=lead.property.agent, actor=None, system=True)


def _notify_owner(lead: Lead) -> None:
    """Decide whether to notify, to whom, and with what text."""
    recipient_user = lead.assigned_to
    if recipient_user is None or not recipient_user.phone_number:
        return

    subject = f"New {lead.get_kind_display().lower()}"
    lines = [f"{lead.full_name} ({lead.phone_number})"]
    if lead.subject is not None:
        lines.append(str(lead.subject))
    if lead.message:
        lines.append(lead.message[:280])

    # transaction.on_commit: never notify about a lead that failed to save.
    transaction.on_commit(
        lambda: notification_service().send(
            NotificationMessage(
                channel=NotificationChannel.SMS,
                recipient=NotificationRecipient(
                    address=recipient_user.phone_number,
                    display_name=recipient_user.get_full_name(),
                ),
                subject=subject,
                body="\n".join(lines),
                kind="lead.created",
                metadata={"lead_id": str(lead.uuid)},
            )
        )
    )
