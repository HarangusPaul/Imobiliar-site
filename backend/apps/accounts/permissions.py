"""Account-scoped permissions.

Product roles are not decided here - see apps.access. This module only covers
rules that are about the account itself.
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAnonymousOnly(BasePermission):
    """Register and login are meaningless for an authenticated session."""

    message = "You are already signed in."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return not request.user.is_authenticated


class IsPhoneVerified(BasePermission):
    """Gate for flows that will require a verified number once OTP is live."""

    message = "Your phone number must be verified for this action."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return bool(request.user.is_authenticated and request.user.is_phone_verified)
