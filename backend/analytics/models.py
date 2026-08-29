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


class AnalyticsAnomaly(models.Model):
    TRAFFIC_SPIKE = 'traffic_spike'
    TRAFFIC_DROP = 'traffic_drop'
    PAGE_SPIKE = 'page_spike'
    PAGE_DROP = 'page_drop'

    KIND_CHOICES = (
        (TRAFFIC_SPIKE, 'Traffic spike'),
        (TRAFFIC_DROP, 'Traffic drop'),
        (PAGE_SPIKE, 'Page spike'),
        (PAGE_DROP, 'Page drop'),
    )

    kind = models.CharField(max_length=32, choices=KIND_CHOICES)
    severity = models.PositiveSmallIntegerField(default=0)
    metric = models.CharField(max_length=64, default='views')
    dimension = models.CharField(max_length=500, blank=True)
    current_value = models.FloatField(default=0)
    baseline_value = models.FloatField(default=0)
    deviation_percent = models.FloatField(default=0)
    z_score = models.FloatField(default=0)
    window_start = models.DateTimeField(db_index=True)
    window_end = models.DateTimeField(db_index=True)
    fingerprint = models.CharField(max_length=255, unique=True)
    details = models.JSONField(default=dict, blank=True)
    acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-window_end', '-severity', '-created_at']
        indexes = [
            models.Index(fields=['window_end', '-severity'], name='analytics_a_window__idx'),
            models.Index(fields=['kind', 'window_end'], name='analytics_a_kind_6e7d5c_idx'),
        ]

    def __str__(self) -> str:
        label = self.get_kind_display()
        target = f' · {self.dimension}' if self.dimension else ''
        return f'{label}{target} · {self.severity}/100'
