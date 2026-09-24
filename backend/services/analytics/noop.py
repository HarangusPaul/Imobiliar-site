"""No-op analytics sink.

Accepts business events and drops them (logging them at debug level so they
are visible during development). Its purpose is to let domain apps emit events
from day one without any tracking being configured.
"""

from __future__ import annotations

import logging

from core.contracts.analytics import AnalyticsEvent

logger = logging.getLogger("services.analytics")


class NoopAnalyticsService:
    """Satisfies ``core.contracts.analytics.AnalyticsService``."""

    def track(self, event: AnalyticsEvent) -> None:
        logger.debug(
            "analytics.track name=%s actor=%s properties=%s",
            event.name,
            event.actor_id or event.anonymous_id or "-",
            event.properties,
        )

    def flush(self) -> None:
        return None
