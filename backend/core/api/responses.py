"""The single response envelope used by every API zone.

Views never hand-build response dictionaries. Success and failure share one
shape so the Next.js client can parse both without branching per endpoint.

Success::

    {"data": <payload>, "meta": {...}}

Failure (see ``core.api.exceptions``)::

    {"error": {"code": "...", "message": "...", "details": {...},
               "request_id": "..."}}
"""

from __future__ import annotations

from typing import Any

from rest_framework import status as http_status
from rest_framework.response import Response


def success(data: Any, *, meta: dict[str, Any] | None = None, status: int = http_status.HTTP_200_OK) -> Response:
    """Wrap a serialized payload in the standard envelope."""
    body: dict[str, Any] = {"data": data}
    if meta:
        body["meta"] = meta
    return Response(body, status=status)


def created(data: Any, *, meta: dict[str, Any] | None = None) -> Response:
    return success(data, meta=meta, status=http_status.HTTP_201_CREATED)


def no_content() -> Response:
    return Response(status=http_status.HTTP_204_NO_CONTENT)
