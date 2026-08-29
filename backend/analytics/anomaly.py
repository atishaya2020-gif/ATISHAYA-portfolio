from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from statistics import mean, pstdev

from django.db.models import Count
from django.db.models.functions import TruncHour
from django.utils import timezone

from .models import AnalyticsAnomaly, PageView

DEFAULT_LOOKBACK_DAYS = 14
MIN_BASELINE_SAMPLES = 5
MIN_SPIKE_BASELINE = 1.0
MIN_DROP_BASELINE = 3.0
MIN_SPIKE_CURRENT = 5
SPIKE_RELATIVE_THRESHOLD = 200.0
DROP_RELATIVE_THRESHOLD = -70.0
Z_THRESHOLD = 3.0


def _hour_start(value):
    value = timezone.localtime(value)
    return value.replace(minute=0, second=0, microsecond=0)


def _safe_percent(current: float, baseline: float) -> float:
    if baseline <= 0:
        return 0.0
    return round(((current - baseline) / baseline) * 100, 1)


def _score(current: float, samples: list[float]):
    if len(samples) < MIN_BASELINE_SAMPLES:
        return None
    baseline = mean(samples)
    deviation = _safe_percent(current, baseline)
    spread = pstdev(samples)
    z_score = (current - baseline) / spread if spread > 0 else 0.0
    is_spike = (
        baseline >= MIN_SPIKE_BASELINE
        and current >= MIN_SPIKE_CURRENT
        and (z_score >= Z_THRESHOLD or deviation >= SPIKE_RELATIVE_THRESHOLD)
    )
    is_drop = (
        baseline >= MIN_DROP_BASELINE
        and (z_score <= -Z_THRESHOLD or deviation <= DROP_RELATIVE_THRESHOLD)
    )
    if not (is_spike or is_drop):
        return None
    severity = 50 + abs(z_score) * 12 + min(abs(deviation), 1000) / 10
    return {
        'baseline': round(baseline, 2),
        'deviation': deviation,
        'z_score': round(z_score, 2),
        'severity': max(1, min(100, round(severity))),
        'direction': 'spike' if is_spike else 'drop',
    }


def _hourly_counts(queryset):
    rows = queryset.annotate(bucket=TruncHour('created_at')).values('bucket').annotate(views=Count('id'))
    return {
        _hour_start(row['bucket']): row['views']
        for row in rows if row['bucket'] is not None
    }


def _page_hourly_counts(queryset):
    rows = (
        queryset.annotate(bucket=TruncHour('created_at'))
        .values('bucket', 'path')
        .annotate(views=Count('id'))
    )
    counts = defaultdict(dict)
    for row in rows:
        if row['bucket'] is not None:
            counts[row['path']][_hour_start(row['bucket'])] = row['views']
    return counts


def _record(kind, dimension, current, result, window_start, window_end, lookback_days):
    fingerprint = f'{kind}:{dimension}:{window_start.isoformat()}'
    anomaly, created = AnalyticsAnomaly.objects.get_or_create(
        fingerprint=fingerprint,
        defaults={
            'kind': kind,
            'severity': result['severity'],
            'metric': 'views',
            'dimension': dimension,
            'current_value': current,
            'baseline_value': result['baseline'],
            'deviation_percent': result['deviation'],
            'z_score': result['z_score'],
            'window_start': window_start,
            'window_end': window_end,
            'details': {
                'lookback_days': lookback_days,
                'window_hours': 1,
                'baseline_samples': MIN_BASELINE_SAMPLES,
            },
        },
    )
    return anomaly, created


def detect_analytics_anomalies(*, window_end=None, lookback_days=DEFAULT_LOOKBACK_DAYS, include_pages=True):
    if window_end is None:
        window_end = _hour_start(timezone.now())
    window_start = window_end - timedelta(hours=1)
    baseline_start = window_start - timedelta(days=lookback_days)
    history_qs = PageView.objects.filter(created_at__gte=baseline_start, created_at__lt=window_end)
    target_hour = window_start.hour
    global_counts = _hourly_counts(history_qs)
    baseline_samples = [v for bucket, v in global_counts.items() if bucket.hour == target_hour]
    current_count = PageView.objects.filter(created_at__gte=window_start, created_at__lt=window_end).count()
    created = []
    result = _score(current_count, baseline_samples)
    if result:
        kind = AnalyticsAnomaly.TRAFFIC_SPIKE if result['direction'] == 'spike' else AnalyticsAnomaly.TRAFFIC_DROP
        anomaly, was_created = _record(kind, '', current_count, result, window_start, window_end, lookback_days)
        if was_created:
            created.append(anomaly)
    if include_pages:
        page_counts = _page_hourly_counts(history_qs)
        current_rows = (
            PageView.objects.filter(created_at__gte=window_start, created_at__lt=window_end)
            .values('path').annotate(views=Count('id'))
        )
        current_by_page = {row['path']: row['views'] for row in current_rows}
        for path, history in page_counts.items():
            samples = [v for bucket, v in history.items() if bucket.hour == target_hour]
            result = _score(current_by_page.get(path, 0), samples)
            if not result:
                continue
            kind = AnalyticsAnomaly.PAGE_SPIKE if result['direction'] == 'spike' else AnalyticsAnomaly.PAGE_DROP
            anomaly, was_created = _record(kind, path, current_by_page.get(path, 0), result, window_start, window_end, lookback_days)
            if was_created:
                created.append(anomaly)
    return created


def get_recent_anomalies(limit=50):
    return AnalyticsAnomaly.objects.order_by('-window_end', '-severity', '-created_at')[:limit]
