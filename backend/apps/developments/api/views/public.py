"""Public development endpoints.

GET /api/v1/public/developments/
GET /api/v1/public/developments/{slug}/
"""

from __future__ import annotations

from django.http import Http404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from core.api.pagination import DefaultPageNumberPagination
from core.api.responses import success

from apps.developments.api.serializers.public import (
    DevelopmentCardSerializer,
    DevelopmentDetailSerializer,
)
from apps.developments.selectors.catalog import (
    get_published_by_slug,
    published_developments,
    unit_availability_summary,
)


class PublicDevelopmentListView(ListAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = DevelopmentCardSerializer
    pagination_class = DefaultPageNumberPagination

    def get_queryset(self):
        queryset = published_developments()
        city = self.request.query_params.get("city")
        status = self.request.query_params.get("status")
        if city:
            queryset = queryset.filter(address__city__slug=city)
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class PublicDevelopmentDetailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def get(self, request: Request, slug: str) -> Response:
        development = get_published_by_slug(slug)
        if development is None:
            raise Http404

        development.availability_summary = unit_availability_summary(development)
        serializer = DevelopmentDetailSerializer(development, context={"request": request})
        return success(serializer.data)
