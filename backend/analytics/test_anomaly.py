import uuid
from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from .anomaly import detect_analytics_anomalies
from .models import AnalyticsAnomaly, PageView


class AnalyticsAnomalyDetectionTests(TestCase):
    def setUp(self):
        self.window_end = timezone.now().replace(minute=0, second=0, microsecond=0)
        self.window_start = self.window_end - timedelta(hours=1)

    def _seed_hour(self, hours_ago, count, path='/'):
        timestamp = self.window_start - timedelta(hours=hours_ago)
        for _ in range(count):
            pv = PageView.objects.create(session_id=uuid.uuid4(), path=path)
            PageView.objects.filter(pk=pv.pk).update(created_at=timestamp)

    def test_requires_enough_history(self):
        for hours_ago in (24, 48, 72):
            self._seed_hour(hours_ago, 5)
        self.assertEqual(detect_analytics_anomalies(window_end=self.window_end), [])

    def test_detects_global_spike(self):
        for hours_ago in range(24, 24 * 11, 24):
            self._seed_hour(hours_ago, 2)
        for _ in range(10):
            pv = PageView.objects.create(session_id=uuid.uuid4(), path='/')
            PageView.objects.filter(pk=pv.pk).update(created_at=self.window_start)
        anomalies = detect_analytics_anomalies(window_end=self.window_end)
        self.assertTrue(any(a.kind == AnalyticsAnomaly.TRAFFIC_SPIKE for a in anomalies))

    def test_detects_page_drop(self):
        for hours_ago in range(24, 24 * 11, 24):
            self._seed_hour(hours_ago, 5, path='/contact')
        anomalies = detect_analytics_anomalies(window_end=self.window_end)
        self.assertTrue(any(a.kind == AnalyticsAnomaly.PAGE_DROP and a.dimension == '/contact' for a in anomalies))

    def test_detector_is_idempotent_for_same_window(self):
        for hours_ago in range(24, 24 * 11, 24):
            self._seed_hour(hours_ago, 2)
        for _ in range(10):
            pv = PageView.objects.create(session_id=uuid.uuid4(), path='/')
            PageView.objects.filter(pk=pv.pk).update(created_at=self.window_start)
        self.assertGreaterEqual(len(detect_analytics_anomalies(window_end=self.window_end)), 1)
        self.assertEqual(detect_analytics_anomalies(window_end=self.window_end), [])

    def test_management_command_runs(self):
        call_command('detect_analytics_anomalies', verbosity=0)
