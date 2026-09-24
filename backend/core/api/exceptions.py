"""Uniform API error format.

Every failure — DRF validation, permission denial, 404, or an unhandled
exception — leaves the process in the same JSON shape. Domain apps raise
``DomainError`` subclasses; they never format HTTP payloads themselves.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from core.logging import get_request_id

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Base class for business-rule violations raised inside app services.

    Apps subclass this (``LeadTransitionError``, ``OTPExpiredError``, ...).
    ``core`` stays unaware of what those rules are.
    """

    code = "domain_error"
    message = "The request could not be completed."
    status_code = 400

    def __init__(self, message: str | None = None, *, details: dict[str, Any] | None = None) -> None:
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)


class ConflictError(DomainError):
    code = "conflict"
    message = "The resource is in a state that conflicts with this request."
    status_code = 409


class NotAllowedError(DomainError):
    code = "not_allowed"
    message = "This action is not allowed for the current actor."
    status_code = 403


def _envelope(code: str, message: str, details: Any = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message, "request_id": get_request_id()}
    if details:
        error["details"] = details
    return {"error": error}


_DRF_CODE_MAP = {
    drf_exceptions.NotAuthenticated: "not_authenticated",
    drf_exceptions.AuthenticationFailed: "authentication_failed",
    drf_exceptions.PermissionDenied: "permission_denied",
    drf_exceptions.NotFound: "not_found",
    drf_exceptions.Throttled: "throttled",
    drf_exceptions.MethodNotAllowed: "method_not_allowed",
    drf_exceptions.ValidationError: "validation_error",
}


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Wired in ``REST_FRAMEWORK['EXCEPTION_HANDLER']``."""
    if isinstance(exc, DomainError):
        return Response(_envelope(exc.code, exc.message, exc.details), status=exc.status_code)

    if isinstance(exc, DjangoValidationError):
        exc = drf_exceptions.ValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
    elif isinstance(exc, Http404):
        exc = drf_exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = drf_exceptions.PermissionDenied()

    response = drf_exception_handler(exc, context)
    if response is None:
        logger.exception("Unhandled API exception", extra={"view": str(context.get("view"))})
        return Response(_envelope("server_error", "An unexpected error occurred."), status=500)

    code = next((c for k, c in _DRF_CODE_MAP.items() if isinstance(exc, k)), "error")
    if isinstance(exc, drf_exceptions.ValidationError):
        message = "The submitted data is invalid."
        details = response.data
    else:
        detail = response.data.get("detail") if isinstance(response.data, dict) else None
        message = str(detail) if detail else "The request could not be completed."
        details = None

    response.data = _envelope(code, message, details)
    return response
