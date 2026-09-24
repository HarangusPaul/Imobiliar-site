"""Catalogue of the implementations this repository ships.

This module is a *declaration*, not a resolver. ``config`` reads it to build
``settings.SERVICE_PROVIDERS``; ``core.contracts.registry`` performs the actual
lookup at call time. Domain apps import neither.

Adding an implementation is a two-step change with no domain impact:
  1. write the adapter under ``services/<contract>/``
  2. register its dotted path here and select it in settings/env
"""

from __future__ import annotations

from types import MappingProxyType

from core.contracts.registry import ANALYTICS, NOTIFICATIONS, STORAGE, VERIFICATION

#: contract -> {alias: dotted path}
AVAILABLE_IMPLEMENTATIONS = MappingProxyType(
    {
        NOTIFICATIONS: MappingProxyType(
            {"console": "services.notifications.console.ConsoleNotificationService"}
        ),
        VERIFICATION: MappingProxyType(
            {"console": "services.verification.console.ConsoleVerificationService"}
        ),
        STORAGE: MappingProxyType({"local": "services.storage.local.LocalFileStorageService"}),
        ANALYTICS: MappingProxyType({"noop": "services.analytics.noop.NoopAnalyticsService"}),
    }
)

#: What an unconfigured environment gets. All local, all provider-agnostic.
DEFAULT_IMPLEMENTATIONS = MappingProxyType(
    {
        NOTIFICATIONS: AVAILABLE_IMPLEMENTATIONS[NOTIFICATIONS]["console"],
        VERIFICATION: AVAILABLE_IMPLEMENTATIONS[VERIFICATION]["console"],
        STORAGE: AVAILABLE_IMPLEMENTATIONS[STORAGE]["local"],
        ANALYTICS: AVAILABLE_IMPLEMENTATIONS[ANALYTICS]["noop"],
    }
)


def resolve(contract: str, selection: str | None) -> str:
    """Translate an alias (``"console"``) or a dotted path into a dotted path."""
    if not selection:
        return DEFAULT_IMPLEMENTATIONS[contract]
    if "." in selection:
        return selection
    try:
        return AVAILABLE_IMPLEMENTATIONS[contract][selection]
    except KeyError:
        known = ", ".join(AVAILABLE_IMPLEMENTATIONS[contract])
        raise ValueError(
            f"Unknown {contract} implementation {selection!r}. Known aliases: {known}."
        ) from None
