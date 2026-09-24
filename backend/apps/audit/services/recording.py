"""Recording audit events.

Every domain app calls `record_event`. Nothing writes AuditEvent directly, so
the shape of an event stays consistent and the request-id stamping cannot be
forgotten.

The import is done lazily at the call site in each app (a local import inside
the function that records) to keep the dependency one-directional and obvious.
"""

from __future__ import annotations

import logging
from typing import Any

from core.logging import get_request_id

from apps.audit.models import AuditEvent

logger = logging.getLogger(__name__)


def record_event(
    *,
    action: str,
    target: Any = None,
    actor: Any = None,
    metadata: dict[str, Any] | None = None,
    request_id: str = "",
) -> AuditEvent | None:
    """Write one immutable event.

    Never raises. An audit failure must not roll back the business operation
    it was describing - it is logged loudly instead.
    """
    try:
        target_app = target_model = target_label = ""
        target_uuid = None
        if target is not None:
            meta = target._meta
            target_app, target_model = meta.app_label, meta.model_name
            target_uuid = getattr(target, "uuid", None)
            target_label = str(target)[:255]

        return AuditEvent.objects.create(
            action=action,
            actor=actor if getattr(actor, "pk", None) else None,
            actor_label=_actor_label(actor),
            target_app=target_app,
            target_model=target_model,
            target_uuid=target_uuid,
            target_label=target_label,
            request_id=request_id or get_request_id(),
            metadata=metadata or {},
        )
    except Exception:
        logger.exception("audit.record_failed action=%s", action)
        return None


def _actor_label(actor: Any) -> str:
    if actor is None:
        return "system"
    getter = getattr(actor, "get_full_name", None)
    return (getter() if callable(getter) else str(actor))[:160]
