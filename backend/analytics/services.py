from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from .models import PageView


def get_overview_stats() -> dict:
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=6)
    month_start = today_start - timedelta(days=29)

    return {
        'total_views': PageView.objects.count(),
        'unique_visitors': PageView.objects.values('session_id').distinct().count(),
        'views_today': PageView.objects.filter(created_at__gte=today_start).count(),
        'views_last_7_days': PageView.objects.filter(created_at__gte=week_start).count(),
        'views_last_30_days': PageView.objects.filter(created_at__gte=month_start).count(),
    }


def get_top_pages(limit: int = 10) -> list[dict]:
    rows = (
        PageView.objects
        .values('path')
        .annotate(views=Count('id'))
        .order_by('-views', 'path')[:limit]
    )
    return [{'path': row['path'], 'views': row['views']} for row in rows]


def get_top_countries(limit: int = 10) -> list[dict]:
    rows = (
        PageView.objects
        .exclude(country_code='')
        .values('country_code', 'country')
        .annotate(views=Count('id'))
        .order_by('-views')[:limit]
    )
    return [
        {'country_code': row['country_code'], 'country': row['country'], 'views': row['views']}
        for row in rows
    ]


def get_device_breakdown() -> list[dict]:
    counts = dict(
        PageView.objects
        .values('device_type')
        .annotate(total=Count('id'))
        .values_list('device_type', 'total')
    )
    return [
        {'device': label, 'key': key, 'views': counts.get(key, 0)}
        for key, label in (
            ('desktop', 'Desktop'),
            ('mobile', 'Mobile'),
            ('tablet', 'Tablet'),
            ('unknown', 'Unknown'),
        )
    ]


def get_top_referrers(limit: int = 10) -> list[dict]:
    rows = (
        PageView.objects
        .exclude(referrer='')
        .values('referrer')
        .annotate(views=Count('id'))
        .order_by('-views')[:limit]
    )
    return [{'referrer': row['referrer'], 'views': row['views']} for row in rows]


def get_daily_views(days: int = 30) -> list[dict]:
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)

    counts_by_day = dict(
        PageView.objects
        .filter(created_at__date__gte=start_date)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(views=Count('id'))
        .values_list('day', 'views')
    )

    daily = []
    for offset in range(days):
        date = start_date + timedelta(days=offset)
        daily.append({'date': date, 'views': counts_by_day.get(date, 0)})
    return daily


def get_recent_visits(limit: int = 20) -> list[dict]:
    rows = PageView.objects.order_by('-created_at')[:limit]
    return [
        {
            'time': row.created_at,
            'path': row.path,
            'country': row.country,
            'device': row.device_type or '—',
            'referrer': row.referrer,
        }
        for row in rows
    ]
