"""Analytics contract.

Domain apps emit business events they consider meaningful
(``property.viewed``, ``lead.created``). This contract describes the sink.
It has no opinion about which events exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class AnalyticsEvent:
    name: str  # dotted business event name, owned by the emitting app
    properties: dict[str, Any] = field(default_factory=dict)
    actor_id: str = ""  # opaque user reference; never a model instance
    anonymous_id: str = ""
    occurred_at: datetime | None = None


@runtime_checkable
class AnalyticsService(Protocol):
    """Implemented in ``services/analytics/``."""

    def track(self, event: AnalyticsEvent) -> None: ...

    def flush(self) -> None: ...
