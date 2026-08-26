from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate, TruncHour, TruncMonth, TruncWeek
from django.utils import timezone

from .models import PageView

VALID_RANGES = {
    '1d': '1D',
    '7d': '7D',
    '30d': '30D',
    '3m': '3M',
    '6m': '6M',
    '1y': '1Y',
    'all': 'ALL',
}


def get_analytics_range_key(range_key: str | None = None) -> str:
    if not range_key:
        return '30d'
    key = str(range_key).strip().lower()
    return key if key in VALID_RANGES else '30d'


def get_range_bounds(range_key: str = '30d'):
    key = get_analytics_range_key(range_key)
    now = timezone.now()
    if key == '1d':
        return now - timedelta(hours=24), now
    if key == '7d':
        return now - timedelta(days=7), now
    if key == '30d':
        return now - timedelta(days=30), now
    if key == '3m':
        return now - timedelta(days=90), now
    if key == '6m':
        return now - timedelta(days=180), now
    if key == '1y':
        return now - timedelta(days=365), now
    if key == 'all':
        return None, now
    return now - timedelta(days=30), now


def get_filtered_queryset(range_key: str = '30d'):
    qs = PageView.objects.all()
    start_time, _ = get_range_bounds(range_key)
    if start_time:
        qs = qs.filter(created_at__gte=start_time)
    return qs


def get_range_overview(range_key: str = '30d') -> dict:
    key = get_analytics_range_key(range_key)
    qs = get_filtered_queryset(key)
    total_views = qs.count()
    unique_visitors = qs.values('session_id').distinct().count()

    start_time, end_time = get_range_bounds(key)
    if start_time:
        days = max(1, (end_time - start_time).days or 1)
    else:
        first_pv = PageView.objects.order_by('created_at').first()
        if first_pv:
            days = max(1, (end_time - first_pv.created_at).days or 1)
        else:
            days = 1

    avg_views_per_day = round(total_views / days, 1)

    top_page_row = (
        qs.values('path')
        .annotate(views=Count('id'))
        .order_by('-views', 'path')
        .first()
    )
    top_page = top_page_row['path'] if top_page_row else '—'

    return {
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'avg_views_per_day': avg_views_per_day,
        'top_page': top_page,
    }


def get_overview_stats(range_key: str = '30d') -> dict:
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=6)
    month_start = today_start - timedelta(days=29)

    overview = get_range_overview(range_key)
    overview.update({
        'views_today': PageView.objects.filter(created_at__gte=today_start).count(),
        'views_last_7_days': PageView.objects.filter(created_at__gte=week_start).count(),
        'views_last_30_days': PageView.objects.filter(created_at__gte=month_start).count(),
    })
    return overview


def get_top_pages(range_key: str = '30d', limit: int = 10) -> list[dict]:
    qs = get_filtered_queryset(range_key)
    rows = (
        qs.values('path')
        .annotate(views=Count('id'))
        .order_by('-views', 'path')[:limit]
    )
    return [{'path': row['path'], 'views': row['views']} for row in rows]


def get_top_countries(range_key: str = '30d', limit: int = 10) -> list[dict]:
    qs = get_filtered_queryset(range_key)
    rows = (
        qs.exclude(country_code='')
        .values('country_code', 'country')
        .annotate(views=Count('id'))
        .order_by('-views')[:limit]
    )
    return [
        {'country_code': row['country_code'], 'country': row['country'], 'views': row['views']}
        for row in rows
    ]


def get_device_breakdown(range_key: str = '30d') -> list[dict]:
    qs = get_filtered_queryset(range_key)
    counts = dict(
        qs.values('device_type')
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


def get_top_referrers(range_key: str = '30d', limit: int = 10) -> list[dict]:
    qs = get_filtered_queryset(range_key)
    rows = (
        qs.exclude(referrer='')
        .values('referrer')
        .annotate(views=Count('id'))
        .order_by('-views')[:limit]
    )
    return [{'referrer': row['referrer'], 'views': row['views']} for row in rows]


def _normalize_bucket_date(bucket):
    if bucket is None:
        return None
    if isinstance(bucket, str):
        bucket = timezone.datetime.fromisoformat(bucket)
    if hasattr(bucket, 'date') and callable(bucket.date):
        if timezone.is_aware(bucket):
            bucket = timezone.localtime(bucket)
        return bucket.date()
    return bucket


def get_time_series(range_key: str = '30d') -> list[dict]:
    key = get_analytics_range_key(range_key)
    qs = get_filtered_queryset(key)

    if key == '1d':
        now = timezone.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        rows = (
            qs.annotate(bucket=TruncHour('created_at'))
            .values('bucket')
            .annotate(views=Count('id'), unique_visitors=Count('session_id', distinct=True))
        )
        counts_map = {}
        for r in rows:
            b = r['bucket']
            if b is None:
                continue
            if timezone.is_aware(b):
                b = timezone.localtime(b)
            lbl = b.strftime('%H:00')
            counts_map[lbl] = {'views': r['views'], 'unique_visitors': r['unique_visitors']}

        series = []
        for i in range(23, -1, -1):
            h_dt = current_hour - timedelta(hours=i)
            if timezone.is_aware(h_dt):
                h_dt = timezone.localtime(h_dt)
            lbl = h_dt.strftime('%H:00')
            val = counts_map.get(lbl, {'views': 0, 'unique_visitors': 0})
            series.append({
                'label': lbl,
                'date': h_dt.strftime('%Y-%m-%d %H:00'),
                'views': val['views'],
                'unique_visitors': val['unique_visitors'],
            })
        return series

    if key in ('7d', '30d', '3m'):
        days_count = 7 if key == '7d' else (30 if key == '30d' else 90)
        today = timezone.localdate()
        start_date = today - timedelta(days=days_count - 1)

        rows = (
            qs.annotate(bucket=TruncDate('created_at'))
            .values('bucket')
            .annotate(views=Count('id'), unique_visitors=Count('session_id', distinct=True))
        )
        counts_map = {}
        for r in rows:
            b = _normalize_bucket_date(r['bucket'])
            if b is None:
                continue
            k = b.strftime('%Y-%m-%d')
            counts_map[k] = {'views': r['views'], 'unique_visitors': r['unique_visitors']}

        series = []
        for i in range(days_count):
            d = start_date + timedelta(days=i)
            k = d.strftime('%Y-%m-%d')
            val = counts_map.get(k, {'views': 0, 'unique_visitors': 0})
            series.append({
                'label': k,
                'date': k,
                'views': val['views'],
                'unique_visitors': val['unique_visitors'],
            })
        return series

    if key == '6m':
        today = timezone.localdate()
        start_of_current_week = today - timedelta(days=today.weekday())
        start_week = start_of_current_week - timedelta(weeks=25)

        rows = (
            qs.annotate(bucket=TruncWeek('created_at'))
            .values('bucket')
            .annotate(views=Count('id'), unique_visitors=Count('session_id', distinct=True))
        )
        counts_map = {}
        for r in rows:
            b = _normalize_bucket_date(r['bucket'])
            if b is None:
                continue
            k = b.strftime('%Y-%m-%d')
            counts_map[k] = {'views': r['views'], 'unique_visitors': r['unique_visitors']}

        series = []
        for i in range(26):
            w = start_week + timedelta(weeks=i)
            k = w.strftime('%Y-%m-%d')
            val = counts_map.get(k, {'views': 0, 'unique_visitors': 0})
            series.append({
                'label': w.strftime('%b %d'),
                'date': k,
                'views': val['views'],
                'unique_visitors': val['unique_visitors'],
            })
        return series

    today = timezone.localdate()
    if key == '1y':
        months_count = 12
    else:
        first_pv = PageView.objects.order_by('created_at').first()
        if first_pv:
            first_date = timezone.localtime(first_pv.created_at).date()
            months_count = max(
                12,
                (today.year - first_date.year) * 12 + (today.month - first_date.month) + 1,
            )
        else:
            months_count = 12

    rows = (
        qs.annotate(bucket=TruncMonth('created_at'))
        .values('bucket')
        .annotate(views=Count('id'), unique_visitors=Count('session_id', distinct=True))
    )
    counts_map = {}
    for r in rows:
        b = r['bucket']
        if b is None:
            continue
        if timezone.is_aware(b):
            b = timezone.localtime(b)
        k = b.strftime('%Y-%m')
        counts_map[k] = {'views': r['views'], 'unique_visitors': r['unique_visitors']}

    year = today.year
    month = today.month
    month_keys = []
    for _ in range(months_count):
        m_key = f'{year:04d}-{month:02d}'
        m_dt = timezone.datetime(year, month, 1)
        month_keys.append((m_key, m_dt.strftime('%b %Y')))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    month_keys.reverse()

    series = []
    for m_key, m_lbl in month_keys:
        val = counts_map.get(m_key, {'views': 0, 'unique_visitors': 0})
        series.append({
            'label': m_lbl,
            'date': m_key,
            'views': val['views'],
            'unique_visitors': val['unique_visitors'],
        })
    return series


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


def get_recent_visits(range_key: str = '30d', limit: int = 20) -> list[dict]:
    qs = get_filtered_queryset(range_key)
    rows = qs.order_by('-created_at')[:limit]
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
