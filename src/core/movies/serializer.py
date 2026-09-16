"""REST DTO serializers for the catalog API."""

from rest_framework import serializers


class PersonSerializer(serializers.Serializer):
    """Serialize a contributor DTO."""

    first_name = serializers.CharField()
    surname = serializers.CharField()


class NameSerializer(serializers.Serializer):
    """Serialize a named catalog DTO."""

    name = serializers.CharField()


class MovieSerializer(serializers.Serializer):
    """Serialize the public movie detail resource."""

    title = serializers.CharField()
    slug = serializers.CharField()
    year = serializers.IntegerField()
    rating = serializers.CharField()
    duration_in_minutes = serializers.IntegerField()
    short_description = serializers.CharField()
    full_description = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    release_date = serializers.DateField(allow_null=True)
    language = NameSerializer()
    genres = NameSerializer(many=True)
    screenplays = PersonSerializer(many=True)
    actors = PersonSerializer(many=True)
    studios = NameSerializer(many=True)
    directors = PersonSerializer(many=True)
    countries = NameSerializer(many=True)


class ProblemDetailSerializer(serializers.Serializer):
    """Document the RFC 7807 error representation returned by the API."""

    type = serializers.URLField()
    title = serializers.CharField()
    status = serializers.IntegerField()
    detail = serializers.CharField()
    errors = serializers.JSONField()
