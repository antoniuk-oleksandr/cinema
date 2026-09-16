"""HTTP controllers for the movie catalog."""

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import MovieSerializer, ProblemDetailSerializer
from .service import MovieService


class MovieDetailView(APIView):
    """Return a public movie and its catalog metadata by slug."""

    @extend_schema(
        parameters=[OpenApiParameter("slug", str, location=OpenApiParameter.PATH)],
        responses={
            200: MovieSerializer,
            404: OpenApiResponse(response=ProblemDetailSerializer, description="Movie not found."),
        },
        description="Retrieve movie data and related genres, screenplays, actors, studios, directors, and countries.",
    )
    def get(self, request, slug: str) -> Response:
        """Handle a movie detail GET request."""
        return Response(MovieSerializer(MovieService().get_movie(slug)).data)
