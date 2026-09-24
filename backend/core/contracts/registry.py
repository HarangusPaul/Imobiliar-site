"""Contract resolution — how an app reaches an implementation it may not import.

``apps`` must never import ``services``. But ``apps/leads`` still has to send a
notification. This module closes that gap:

    settings.SERVICE_PROVIDERS  ->  dotted path  ->  instance

Resolution happens at call time via ``import_string``, so there is no static
import edge from ``core`` (or from ``apps``) to ``services``. ``config`` is the
only place that decides which dotted path is active.

Usage from a domain app::

    from core.contracts.registry import notification_service

    notification_service().send(message)
"""

from __future__ import annotations

import threading
from typing import Any, TypeVar

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from core.contracts.analytics import AnalyticsService
from core.contracts.notification import NotificationService
from core.contracts.storage import FileStorageService
from core.contracts.verification import VerificationService

NOTIFICATIONS = "notifications"
VERIFICATION = "verification"
STORAGE = "storage"
ANALYTICS = "analytics"

_CONTRACT_PROTOCOLS: dict[str, type] = {
    NOTIFICATIONS: NotificationService,
    VERIFICATION: VerificationService,
    STORAGE: FileStorageService,
    ANALYTICS: AnalyticsService,
}

_cache: dict[str, Any] = {}
_lock = threading.Lock()

T = TypeVar("T")


def get_provider(contract: str) -> Any:
    """Return the configured singleton implementation for ``contract``."""
    if contract not in _CONTRACT_PROTOCOLS:
        raise ImproperlyConfigured(f"Unknown service contract: {contract!r}")

    if contract in _cache:
        return _cache[contract]

    with _lock:
        if contract in _cache:
            return _cache[contract]

        providers = getattr(settings, "SERVICE_PROVIDERS", {})
        dotted = providers.get(contract)
        if not dotted:
            raise ImproperlyConfigured(
                f"settings.SERVICE_PROVIDERS is missing an entry for {contract!r}."
            )

        try:
            implementation = import_string(dotted)()
        except ImportError as exc:
            raise ImproperlyConfigured(
                f"Cannot import service implementation {dotted!r} for {contract!r}."
            ) from exc

        protocol = _CONTRACT_PROTOCOLS[contract]
        if not isinstance(implementation, protocol):
            raise ImproperlyConfigured(
                f"{dotted!r} does not satisfy the {protocol.__name__} contract."
            )

        _cache[contract] = implementation
        return implementation


def reset_providers() -> None:
    """Clear the cache. Used by tests that swap implementations."""
    with _lock:
        _cache.clear()


def notification_service() -> NotificationService:
    return get_provider(NOTIFICATIONS)


def verification_service() -> VerificationService:
    return get_provider(VERIFICATION)


def storage_service() -> FileStorageService:
    return get_provider(STORAGE)


def analytics_service() -> AnalyticsService:
    return get_provider(ANALYTICS)
