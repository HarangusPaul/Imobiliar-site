"""Notification contract.

Domain apps decide *whether*, *when* and *to whom* a notification is sent.
This contract describes only the act of delivery. It carries no knowledge of
leads, properties or agents — the payload is a rendered message plus a
neutral ``kind`` the implementation may use for routing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable


class NotificationChannel(StrEnum):
    """Transport families an implementation may support."""

    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"


@dataclass(frozen=True, slots=True)
class NotificationRecipient:
    """Where a message goes. Never a domain user object."""

    address: str  # phone number, email address, device token — channel-dependent
    display_name: str = ""


@dataclass(frozen=True, slots=True)
class NotificationMessage:
    """A message the caller has already composed."""

    channel: NotificationChannel
    recipient: NotificationRecipient
    subject: str
    body: str
    kind: str = "generic"  # caller-defined label, e.g. "lead.assigned"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class NotificationResult:
    delivered: bool
    reference: str = ""
    error: str = ""


@runtime_checkable
class NotificationService(Protocol):
    """Implemented in ``services/notifications/``."""

    def supports(self, channel: NotificationChannel) -> bool: ...

    def send(self, message: NotificationMessage) -> NotificationResult: ...
