"""DRF transport serializers for cinemas."""

from rest_framework import serializers

# DRF field descriptors are dynamically assigned by its serializer metaclass.


class HallSerializer(serializers.Serializer):
    """Serialize a public hall summary."""

    name = serializers.CharField()
    slug = serializers.CharField()
    type = serializers.CharField()
    capacity = serializers.IntegerField()
    accessibility = serializers.JSONField()


class CinemaListSerializer(serializers.Serializer):
    """Serialize a cinema item in a paginated list response."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    city = serializers.CharField()
    address = serializers.CharField()
    timezone = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.EmailField()
    status = serializers.CharField()
    hall_count = serializers.IntegerField()
    hall_types = serializers.ListField(child=serializers.CharField())


class CinemaListPageSerializer(serializers.Serializer):
    """Serialize the paginated cinema list response envelope."""

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = CinemaListSerializer(many=True)


class CinemaSerializer(CinemaListSerializer):
    """Serialize a public cinema representation, including hall summaries."""

    halls = HallSerializer(many=True)


class CinemaFilterSerializer(serializers.Serializer):
    """Validate supported cinema list query parameters."""

    query = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    city = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    hall_type = serializers.ChoiceField(
        required=False,
        allow_blank=True,
        choices=("standard", "imax", "vip", "3d"),
    )
    status = serializers.ChoiceField(
        required=False,
        allow_blank=True,
        choices=("active", "inactive"),
    )
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)


class CinemaProblemDetailSerializer(serializers.Serializer):
    """Serialize the standard API error envelope."""

    type = serializers.URLField()
    title = serializers.CharField()
    status = serializers.IntegerField()
    detail = serializers.CharField()
    errors = serializers.JSONField()  # pyright: ignore[reportAssignmentType]
