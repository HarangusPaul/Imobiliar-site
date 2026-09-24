"""Publication state transitions.

The transition table lives in models/enums.py; enforcing it, stamping
published_at, emitting the audit event and notifying interested parties is
this module's job.

A view never sets publication_status directly.
"""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from core.api.exceptions import ConflictError, NotAllowedError
from core.contracts.analytics import AnalyticsEvent
from core.contracts.registry import analytics_service

from apps.access.policy import Capability
from apps.access.selectors.roles import has_capability
from apps.properties.models import (
    ALLOWED_PUBLICATION_TRANSITIONS,
    Property,
    PublicationStatus,
)


class InvalidTransitionError(ConflictError):
    code = "invalid_publication_transition"


class NotReadyToPublishError(ConflictError):
    code = "property_not_ready"
    message = "This listing is missing information required for publication."


def _assert_transition_allowed(current: str, target: str) -> None:
    if current == target:
        raise InvalidTransitionError(f"The listing is already {target}.")
    if target not in ALLOWED_PUBLICATION_TRANSITIONS.get(current, frozenset()):
        raise InvalidTransitionError(f"Cannot move a listing from {current} to {target}.")


def _assert_publishable(prop: Property) -> None:
    """Completeness rules for a public listing.

    Deliberately strict: an incomplete listing on the public site costs more
    in trust than a delayed one.
    """
    missing = []
    if not prop.title.strip():
        missing.append("title")
    if not prop.short_description.strip():
        missing.append("short_description")
    if prop.price is None:
        missing.append("price")
    if prop.cover_image_id is None:
        missing.append("cover_image")
    if missing:
        raise NotReadyToPublishError(details={"missing": missing})


@transaction.atomic
def transition_publication(prop: Property, *, target: str, actor) -> Property:
    """Move a listing between publication states."""
    if target == PublicationStatus.PUBLISHED and not has_capability(
        actor, Capability.PROPERTY_PUBLISH
    ):
        raise NotAllowedError("Your role cannot publish listings.")
    if target == PublicationStatus.ARCHIVED and not has_capability(
        actor, Capability.PROPERTY_ARCHIVE
    ):
        raise NotAllowedError("Your role cannot archive listings.")

    previous = prop.publication_status
    _assert_transition_allowed(previous, target)

    updated_fields = ["publication_status", "updated_at"]
    if target == PublicationStatus.PUBLISHED:
        _assert_publishable(prop)
        if prop.published_at is None:
            prop.published_at = timezone.now()
            updated_fields.append("published_at")

    prop.publication_status = target
    prop.save(update_fields=updated_fields)

    _record(prop, previous=previous, target=target, actor=actor)
    return prop


def _record(prop: Property, *, previous: str, target: str, actor) -> None:
    from apps.audit.services.recording import record_event

    record_event(
        actor=actor,
        action=f"property.{target}",
        target=prop,
        metadata={"from": previous, "to": target, "reference_code": prop.reference_code},
    )
    analytics_service().track(
        AnalyticsEvent(
            name=f"property.{target}",
            actor_id=str(getattr(actor, "uuid", "")),
            properties={"property_id": str(prop.uuid), "transaction_type": prop.transaction_type},
        )
    )
