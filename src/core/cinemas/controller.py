"""HTTP controllers for cinemas."""

from typing import cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Cinema
from .mapper import cinema_to_dto
from .serializer import (
    CinemaFilterSerializer,
    CinemaListPageSerializer,
    CinemaListSerializer,
    CinemaProblemDetailSerializer,
    CinemaSerializer,
)
from .service import CinemaService

# DRF's generic view stubs do not describe pagination's dynamically typed queryset.


class CinemaPagination(PageNumberPagination):
    """Pagination defaults for the public cinema collection."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CinemaListView(APIView):
    """List public cinemas with supported filters."""

    @extend_schema(
        operation_id="cinemas_list",
        parameters=[CinemaFilterSerializer],
        responses={
            200: OpenApiResponse(response=CinemaListPageSerializer),
            (400, "application/problem+json"): OpenApiResponse(
                response=CinemaProblemDetailSerializer
            ),
        },
        description="List active cinemas, optionally filtered by text, city, hall type, or status.",
    )
    def get(self, request: Request) -> Response:
        """Handle a paginated cinema search request."""
        filters = CinemaFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        validated_filters = cast(dict[str, str], filters.validated_data)
        validated_filters.pop("page", None)
        validated_filters.pop("page_size", None)

        paginator = CinemaPagination()
        data = CinemaService().list_cinema_entities(**validated_filters)
        page = cast(list[Cinema] | None, paginator.paginate_queryset(data, request, view=self))  # pyright: ignore[reportUnknownMemberType]
        return paginator.get_paginated_response(  # pyright: ignore[reportUnknownMemberType]
            CinemaListSerializer([cinema_to_dto(cinema) for cinema in (page or [])], many=True).data
        )


class CinemaDetailView(APIView):
    """Return an active cinema and its halls."""

    @extend_schema(
        operation_id="cinema_retrieve",
        responses={
            200: CinemaSerializer,
            (404, "application/problem+json"): OpenApiResponse(
                response=CinemaProblemDetailSerializer
            ),
        },
    )
    def get(self, request: Request, slug: str) -> Response:
        """Handle a cinema detail request."""
        return Response(CinemaSerializer(CinemaService().get_cinema(slug)).data)
