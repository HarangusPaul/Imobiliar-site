"""Public property endpoints.

GET /api/v1/public/properties/
GET /api/v1/public/properties/{slug}/
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

from apps.properties.api.filters import build_search_query
from apps.properties.api.serializers.public import (
    PropertyCardSerializer,
    PropertyDetailSerializer,
)
from apps.properties.selectors.search import get_published_by_slug, search_published, similar_to


class PublicPropertyListView(ListAPIView):
    """Paginated search over published listings.

    The view parses and delegates. Every decision about what is visible lives
    in the selector.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    serializer_class = PropertyCardSerializer
    pagination_class = DefaultPageNumberPagination

    def get_queryset(self):
        return search_published(build_search_query(self.request), user=self.request.user)


class PublicPropertyDetailView(APIView):
    """One listing, by slug. Slugs are the public identifier in URLs."""

    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def get(self, request: Request, slug: str) -> Response:
        prop = get_published_by_slug(slug)
        if prop is None:
            raise Http404

        data = PropertyDetailSerializer(prop, context={"request": request}).data
        similar = PropertyCardSerializer(
            similar_to(prop), many=True, context={"request": request}
        ).data
        return success(data, meta={"similar": similar})
