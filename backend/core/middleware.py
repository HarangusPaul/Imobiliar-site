"""Project-wide middleware.

Domain-neutral only. Anything that needs to know about roles, subscriptions or
listings belongs to the owning app, not here.
"""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from core.logging import (
    REQUEST_ID_HEADER,
    get_request_id,
    new_request_id,
    reset_request_id,
    set_request_id,
)


class RequestIDMiddleware:
    """Assigns (or accepts) a request id and echoes it back on the response.

    Downstream consumers:
      * ``core.logging.RequestIDFilter`` — log correlation.
      * ``core.api.exceptions`` — error envelope.
      * ``apps.audit`` — stores it on every audit event.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        incoming = request.headers.get(REQUEST_ID_HEADER, "").strip()
        # Never trust an arbitrarily long client-supplied value.
        request_id = incoming[:64] if incoming else new_request_id()
        token = set_request_id(request_id)
        request.request_id = request_id  # type: ignore[attr-defined]
        try:
            response = self.get_response(request)
        finally:
            reset_request_id(token)
        response[REQUEST_ID_HEADER] = request_id
        return response


class SecurityHeadersMiddleware:
    """Adds conservative, framework-agnostic response headers.

    Kept minimal and local-friendly; transport/hosting concerns are out of
    scope for this phase.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault("X-Frame-Options", "DENY")
        return response


def current_request_id() -> str:
    """Convenience re-export for app code that has no request object at hand."""
    return get_request_id()
