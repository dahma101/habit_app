"""Standard pagination configuration for all list endpoints."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsPagination(PageNumberPagination):
    """Page-number pagination with configurable page size.

    Clients may override the page size via the `page_size` query parameter
    up to the configured maximum.
    """

    page_size: int = 20
    page_size_query_param: str = "page_size"
    max_page_size: int = 100

    def get_paginated_response(self, data: object) -> Response:
        """Return paginated response with count and navigation links."""
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
