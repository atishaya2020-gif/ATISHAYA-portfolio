from urllib.parse import urlparse

from rest_framework import serializers


class PageViewCreateSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    path = serializers.CharField(max_length=500)
    referrer = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    def validate_path(self, value: str) -> str:
        parsed = urlparse(value)
        return parsed.path or '/'
