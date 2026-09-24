"""Verification-code delivery contract.

The split is deliberate and load-bearing:

* ``apps/accounts`` owns the code's lifecycle — generation policy, hashing,
  expiry, attempt counting, lockout, and what a successful verification means
  for the account.
* An implementation of this contract owns *delivery only*. It must not decide
  whether a code is valid, how long it lives, or how many tries a user gets.

This is what lets SMS or WhatsApp be added later as a pure services change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol, runtime_checkable


class VerificationChannel(StrEnum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    VOICE = "voice"


@dataclass(frozen=True, slots=True)
class VerificationRequest:
    """A code the domain has already generated and persisted."""

    channel: VerificationChannel
    destination: str  # E.164 phone number
    code: str
    purpose: str = "account_verification"  # caller-defined label
    ttl_seconds: int = 300  # informational: for message copy only, not policy
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VerificationDispatchResult:
    dispatched: bool
    reference: str = ""
    error: str = ""


@runtime_checkable
class VerificationService(Protocol):
    """Implemented in ``services/verification/``."""

    def supports(self, channel: VerificationChannel) -> bool: ...

    def dispatch(self, request: VerificationRequest) -> VerificationDispatchResult: ...
