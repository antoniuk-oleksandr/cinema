from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

# JWTAuthentication exposes claims dynamically; normalize them at this boundary.


class HasRole(BasePermission):
    """Authorize a request when its trusted JWT contains the required role."""

    required_role = None

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Return whether the authenticated request has the configured role."""
        required = getattr(view, "required_role", self.required_role)
        claims = request.auth or {}  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        roles = claims.get("roles", claims.get("role", []))  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if isinstance(roles, str):
            roles = [roles]
        return bool(required and required in roles)


class IsAdmin(HasRole):
    """Permission class for endpoints restricted to administrators."""

    required_role = "admin"
