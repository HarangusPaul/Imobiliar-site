"""Property-scoped object permissions.

Capability checks come from apps.access. This module only adds the
object-level question that app cannot answer: is this particular listing mine?
"""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.access.policy import Capability
from apps.access.selectors.roles import has_capability
from apps.properties.models import Property


class CanEditProperty(BasePermission):
    message = "You cannot edit this listing."

    def has_object_permission(self, request: Request, view: APIView, obj: Property) -> bool:
        if has_capability(request.user, Capability.PROPERTY_EDIT_ANY):
            return True
        return (
            has_capability(request.user, Capability.PROPERTY_EDIT_OWN)
            and obj.agent_id == request.user.pk
        )
