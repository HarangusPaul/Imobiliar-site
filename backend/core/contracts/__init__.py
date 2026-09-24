"""Interfaces between the business domains and replaceable implementations.

A contract lives here when two conditions hold: a domain app needs the
capability, and the capability could plausibly be provided by more than one
implementation. Everything here is domain-neutral by construction.
"""

from core.contracts.registry import (
    analytics_service,
    notification_service,
    storage_service,
    verification_service,
)

__all__ = [
    "analytics_service",
    "notification_service",
    "storage_service",
    "verification_service",
]
