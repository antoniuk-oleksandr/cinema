from django.apps import AppConfig

# Django's AppConfig metaclass replaces this declarative class attribute.


class CoreConfig(AppConfig):
    """Configure the core Django application."""

    default_auto_field = "django.db.models.BigAutoField"  # pyright: ignore[reportAssignmentType]
    name = "core"
