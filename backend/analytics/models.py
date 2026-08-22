import hashlib
import hmac

from django.conf import settings
from django.db import models


class PageView(models.Model):
    session_id = models.UUIDField(db_index=True)
    path = models.CharField(max_length=500)
    referrer = models.URLField(max_length=1000, blank=True)
    country = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    device_type = models.CharField(max_length=30, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    ip_hash = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.path} @ {self.created_at}'

    @staticmethod
    def hash_ip(ip: str) -> str:
        salt = getattr(settings, 'ANALYTICS_HASH_SALT', '')
        return hmac.new(
            salt.encode(),
            ip.encode(),
            hashlib.sha256,
        ).hexdigest()
