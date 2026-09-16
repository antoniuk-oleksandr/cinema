import django.db.models.deletion
from django.db import migrations, models

# Ruff's RUF012 rule does not understand Django migration metadata.
# ruff: noqa: RUF012


class Migration(migrations.Migration):
    """Create cinema locations and their auditoriums."""

    dependencies = [("core", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Cinema",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("address", models.CharField(max_length=500)),
                ("city", models.CharField(max_length=100)),
                ("timezone", models.CharField(max_length=64)),
                ("phone", models.CharField(blank=True, max_length=32)),
                ("email", models.EmailField(blank=True, max_length=254)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("inactive", "Inactive")],
                        default="active",
                        max_length=16,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "indexes": [
                    models.Index(fields=["city"], name="cinema_city_idx"),
                    models.Index(fields=["status"], name="cinema_status_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Hall",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=100)),
                ("capacity", models.PositiveIntegerField()),
                (
                    "hall_type",
                    models.CharField(
                        choices=[
                            ("standard", "Standard"),
                            ("imax", "IMAX"),
                            ("vip", "VIP"),
                            ("3d", "3D"),
                        ],
                        default="standard",
                        max_length=16,
                    ),
                ),
                ("screen_configuration", models.JSONField(blank=True, default=dict)),
                ("accessibility", models.JSONField(blank=True, default=dict)),
                (
                    "cinema",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="halls",
                        to="core.cinema",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
                "indexes": [
                    models.Index(fields=["cinema", "hall_type"], name="hall_cinema_type_idx")
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=["cinema", "slug"], name="unique_hall_slug_per_cinema"
                    )
                ],
            },
        ),
    ]
