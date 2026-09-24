"""Pagination primitives shared by every list endpoint.

Defined once here so ``apps/properties`` never ships its own paginator. The
page metadata lives under ``meta`` to match ``core.api.responses``.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any

from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response


class DefaultPageNumberPagination(PageNumberPagination):
    """Offset pagination for browsable, jump-to-page result sets.

    This is what the public property grid uses: visitors expect page numbers
    and a total count.
    """

    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: Any) -> Response:
        return Response(
            {
                "data": data,
                "meta": OrderedDict(
                    [
                        ("count", self.page.paginator.count),
                        ("page", self.page.number),
                        ("pages", self.page.paginator.num_pages),
                        ("page_size", self.get_page_size(self.request)),
                        ("next", self.get_next_link()),
                        ("previous", self.get_previous_link()),
                    ]
                ),
            }
        )


class TimelineCursorPagination(CursorPagination):
    """Cursor pagination for large append-only feeds (audit events, lead history).

    Chosen where deep offsets would degrade and where a total count is not
    worth a second query.
    """

    page_size = 50
    max_page_size = 200
    page_size_query_param = "page_size"
    ordering = "-created_at"

    def get_paginated_response(self, data: Any) -> Response:
        return Response(
            {
                "data": data,
                "meta": {"next": self.get_next_link(), "previous": self.get_previous_link()},
            }
        )
