"""Authentication endpoints for /api/v1/client/auth/.

Views are thin by rule: validate input, call one service, serialize the
result. Any branching that represents a business decision belongs in the
service, not here.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from core.api.responses import created, no_content, success
from core.permissions import IsAuthenticatedAndActive

from apps.accounts.api.serializers.auth import (
    AccountSerializer,
    LoginSerializer,
    RegisterSerializer,
)
from apps.accounts.services.authentication import login_with_password, logout_session
from apps.accounts.services.registration import RegistrationInput, register_client


class RegisterView(APIView):
    """POST /api/v1/client/auth/register/"""

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = register_client(RegistrationInput(**serializer.validated_data))
        return created(AccountSerializer(user).data)


class LoginView(APIView):
    """POST /api/v1/client/auth/login/"""

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = login_with_password(
            request,
            phone_number=serializer.validated_data["phone_number"],
            password=serializer.validated_data["password"],
        )
        if not serializer.validated_data["remember"]:
            # Expire the session when the browser closes.
            request.session.set_expiry(0)
        return success(AccountSerializer(user).data, status=status.HTTP_200_OK)


class SessionView(APIView):
    """GET /api/v1/client/auth/session/ - the signed-in account."""

    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request: Request) -> Response:
        return success(AccountSerializer(request.user).data)


class LogoutView(APIView):
    """POST /api/v1/client/auth/logout/"""

    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request: Request) -> Response:
        logout_session(request)
        return no_content()
