import ipaddress

from django.conf import settings
from rest_framework import permissions, status, throttling
from rest_framework.response import Response
from rest_framework.views import APIView

from .geolocation import GeoResult, get_country_from_ip
from .models import PageView
from .serializers import PageViewCreateSerializer
from .utils import get_device_type


class AnalyticsTrackingThrottle(throttling.AnonRateThrottle):
    scope = 'analytics_tracking'


def get_trusted_client_ip(request) -> str:
    """Return the client IP, honoring a configured reverse-proxy trust boundary.

    - When ANALYTICS_TRUST_PROXY is configured, the proxy is expected to set
      X-Forwarded-For (a comma-separated list, leftmost = original client) and
      optionally X-Real-IP. Those headers are only trusted because the request
      is known to arrive from the trusted proxy.
    - When no trusted proxy is configured, forwarded headers are ignored and
      REMOTE_ADDR is used.
    - Every candidate is validated with ipaddress; malformed values are ignored.
    - Never raises. Never returns a raw IP for persistence.
    """
    if _is_trusted_proxy(request):
        candidate = _first_valid_ip(request.META.get('HTTP_X_FORWARDED_FOR', ''))
        if not candidate:
            candidate = _first_valid_ip(request.META.get('HTTP_X_REAL_IP', ''))
        if candidate:
            return candidate
    return _first_valid_ip(request.META.get('REMOTE_ADDR', ''))


def _is_trusted_proxy(request) -> bool:
    try:
        val = getattr(settings, 'ANALYTICS_TRUST_PROXY', False)
        if isinstance(val, bool):
            return val
        return str(val).lower() in ('true', '1', 'yes', 'on')
    except Exception:
        return False


def _first_valid_ip(raw: str) -> str:
    for part in str(raw).split(','):
        candidate = part.strip()
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            continue
        return candidate
    return ''


class PageViewCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnalyticsTrackingThrottle]

    def post(self, request):
        serializer = PageViewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        ip = get_trusted_client_ip(request)
        referrer = request.META.get('HTTP_REFERER', '')[:1000] or data.get('referrer', '')

        try:
            geo = get_country_from_ip(ip)
        except Exception:
            geo = GeoResult()

        PageView.objects.create(
            session_id=data['session_id'],
            path=data['path'],
            referrer=referrer,
            country=geo.country,
            country_code=geo.country_code,
            device_type=get_device_type(user_agent),
            user_agent=user_agent,
            ip_hash=PageView.hash_ip(ip) if ip else '',
        )

        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)
