"""Request-scoped logging context.

Owns the request-id contextvar and the logging filter that stamps it onto
every record. ``core.middleware`` sets it; ``core.api.exceptions`` reads it so
a client-visible error can be traced back to a server log line.
"""

from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar

_request_id: ContextVar[str] = ContextVar("request_id", default="")

REQUEST_ID_HEADER = "X-Request-ID"


def new_request_id() -> str:
    return uuid.uuid4().hex


def set_request_id(value: str) -> object:
    return _request_id.set(value)


def reset_request_id(token: object) -> None:
    _request_id.reset(token)  # type: ignore[arg-type]


def get_request_id() -> str:
    return _request_id.get()


class RequestIDFilter(logging.Filter):
    """Adds ``%(request_id)s`` to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True
