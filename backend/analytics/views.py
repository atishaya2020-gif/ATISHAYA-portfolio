from rest_framework import permissions, status, throttling
from rest_framework.response import Response
from rest_framework.views import APIView

from .geolocation import GeoResult, get_country_from_ip
from .models import PageView
from .serializers import PageViewCreateSerializer
from .utils import get_device_type


class AnalyticsTrackingThrottle(throttling.AnonRateThrottle):
    scope = 'analytics_tracking'


class PageViewCreateView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnalyticsTrackingThrottle]

    def post(self, request):
        serializer = PageViewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        ip = self._get_client_ip(request)
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

    @staticmethod
    def _get_client_ip(request) -> str:
        return request.META.get('REMOTE_ADDR', '')
