"""Public lead submission.

POST /api/v1/public/leads/
"""

from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from core.api.responses import created

from apps.leads.api.serializers.public import LeadReceiptSerializer, LeadSubmissionSerializer
from apps.leads.services.intake import LeadInput, submit_lead


class PublicLeadCreateView(APIView):
    """The contact form endpoint.

    Unauthenticated and therefore rate-limited by its own scope - a contact
    form is the most abused endpoint on a property site.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "lead-submit"

    def post(self, request: Request) -> Response:
        serializer = LeadSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lead = submit_lead(
            LeadInput(**serializer.validated_data),
            user=request.user if request.user.is_authenticated else None,
        )
        return created(LeadReceiptSerializer(lead).data)
