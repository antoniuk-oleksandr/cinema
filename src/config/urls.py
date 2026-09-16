from django.conf import settings
from django.contrib import admin
from django.urls import include, path  # pyright: ignore[reportUnknownVariableType]
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# URL/view factories in the installed Django/DRF stubs are dynamically typed.

urlpatterns = [
    path("admin/", admin.site.urls),  # pyright: ignore[reportAny]
    path("api/v1/token/", TokenObtainPairView.as_view()),  # pyright: ignore[reportUnknownMemberType]
    path("api/v1/token/refresh/", TokenRefreshView.as_view()),  # pyright: ignore[reportUnknownMemberType]
    path("", include("core.urls")),
    path("api/v1/", include("core.api_urls")),
]
if settings.API_DOCS_ENABLED:  # pyright: ignore[reportAny]
    urlpatterns += [
        path("schema/", SpectacularAPIView.as_view(), name="schema"),  # pyright: ignore[reportUnknownMemberType]
        path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),  # pyright: ignore[reportUnknownMemberType]
    ]
