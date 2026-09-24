"""Lead-scoped object permissions."""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.access.policy import Capability
from apps.access.selectors.roles import has_capability
from apps.leads.models import Lead


class CanHandleLead(BasePermission):
    message = "This lead is not yours to handle."

    def has_object_permission(self, request: Request, view: APIView, obj: Lead) -> bool:
        if has_capability(request.user, Capability.LEAD_VIEW_ALL):
            return True
        return obj.assigned_to_id == request.user.pk or (
            obj.property_id is not None and obj.property.agent_id == request.user.pk
        )
