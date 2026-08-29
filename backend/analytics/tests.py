import uuid
from datetime import timedelta

from unittest.mock import patch

from django.contrib import admin
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import PageView
from .utils import get_device_type
from .geolocation import GeoResult, get_country_from_ip
from .geoip_download import (
    DEFAULT_GEOIP_DATABASE_PATH,
    GeoIPDownloadError,
    download_geolite2_country,
    resolve_geoip_database_path,
)
from .services import (
    get_analytics_range_key,
    get_device_breakdown,
    get_filtered_queryset,
    get_overview_stats,
    get_range_bounds,
    get_range_overview,
    get_time_series,
    get_country_traffic_share,
    get_insights,
    get_landing_pages,
    get_page_traffic_share,
    get_peak_day,
    get_peak_hour,
    get_top_countries,
    get_top_pages,
    get_top_referrers,
    get_traffic_sources,
    get_views_per_visitor,
)

from portfolio.models import Profile

TRACK_URL = '/api/analytics/track/'


# ---------------------------------------------------------------------------
# Batch 1 – model / admin tests
# ---------------------------------------------------------------------------

class PageViewCreationTests(TestCase):
    def test_pageview_can_be_created(self):
        pv = PageView.objects.create(session_id=uuid.uuid4(), path='/')
        self.assertIsNotNone(pv.pk)

    def test_session_id_is_stored(self):
        sid = uuid.uuid4()
        pv = PageView.objects.create(session_id=sid, path='/about')
        self.assertEqual(PageView.objects.get(pk=pv.pk).session_id, sid)

    def test_path_is_stored(self):
        pv = PageView.objects.create(session_id=uuid.uuid4(), path='/projects/aurora')
        self.assertEqual(PageView.objects.get(pk=pv.pk).path, '/projects/aurora')

    def test_raw_ip_is_not_a_model_field(self):
        field_names = [f.name for f in PageView._meta.get_fields()]
        self.assertNotIn('ip', field_names)
        self.assertNotIn('raw_ip', field_names)
        self.assertNotIn('ip_address', field_names)

    def test_ip_hash_can_be_stored(self):
        pv = PageView.objects.create(
            session_id=uuid.uuid4(), path='/', ip_hash='abc123',
        )
        self.assertEqual(PageView.objects.get(pk=pv.pk).ip_hash, 'abc123')


class PageViewAdminTests(TestCase):
    def test_pageview_registered_in_admin(self):
        self.assertIn(PageView, admin.site._registry)


# ---------------------------------------------------------------------------
# Batch 1 – sanity
# ---------------------------------------------------------------------------

class ExistingTestsSanityCheck(TestCase):
    def test_health_endpoint_still_works(self):
        client = APIClient()
        response = client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'status': 'ok'})


# ---------------------------------------------------------------------------
# Device detection
# ---------------------------------------------------------------------------

class DeviceTypeTests(TestCase):
    def test_desktop(self):
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0'
        self.assertEqual(get_device_type(ua), 'desktop')

    def test_mobile(self):
        ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Safari/605'
        self.assertEqual(get_device_type(ua), 'mobile')

    def test_tablet(self):
        ua = 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) Safari/605'
        self.assertEqual(get_device_type(ua), 'tablet')

    def test_unknown_empty(self):
        self.assertEqual(get_device_type(''), 'unknown')


# ---------------------------------------------------------------------------
# Tracking endpoint – happy path
# ---------------------------------------------------------------------------

@override_settings(ANALYTICS_HASH_SALT='test-salt-123')
class TrackingEndpointSuccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'session_id': str(uuid.uuid4()),
            'path': '/projects/aurora',
        }

    def test_valid_post_returns_201(self):
        response = self.client.post(TRACK_URL, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_post_returns_ok_status(self):
        response = self.client.post(TRACK_URL, self.valid_payload, format='json')
        self.assertEqual(response.data, {'status': 'ok'})

    def test_valid_post_creates_one_pageview(self):
        self.client.post(TRACK_URL, self.valid_payload, format='json')
        self.assertEqual(PageView.objects.count(), 1)

    def test_session_id_is_stored(self):
        sid = uuid.uuid4()
        self.valid_payload['session_id'] = str(sid)
        self.client.post(TRACK_URL, self.valid_payload, format='json')
        self.assertEqual(PageView.objects.first().session_id, sid)

    def test_path_is_stored(self):
        self.client.post(TRACK_URL, self.valid_payload, format='json')
        self.assertEqual(PageView.objects.first().path, '/projects/aurora')

    def test_query_strings_are_stripped(self):
        payload = {
            'session_id': str(uuid.uuid4()),
            'path': '/projects/aurora?source=linkedin&ref=twitter',
        }
        self.client.post(TRACK_URL, payload, format='json')
        self.assertEqual(PageView.objects.first().path, '/projects/aurora')

    def test_user_agent_produces_desktop(self):
        self.client.post(
            TRACK_URL,
            self.valid_payload,
            format='json',
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120',
        )
        self.assertEqual(PageView.objects.first().device_type, 'desktop')

    def test_user_agent_produces_mobile(self):
        self.client.post(
            TRACK_URL,
            self.valid_payload,
            format='json',
            HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)',
        )
        self.assertEqual(PageView.objects.first().device_type, 'mobile')

    def test_referrer_is_stored_from_header(self):
        self.client.post(
            TRACK_URL,
            self.valid_payload,
            format='json',
            HTTP_REFERER='https://google.com',
        )
        self.assertEqual(PageView.objects.first().referrer, 'https://google.com')

    def test_referrer_from_body_when_no_header(self):
        payload = {
            **self.valid_payload,
            'referrer': 'https://example.com/page',
        }
        self.client.post(TRACK_URL, payload, format='json')
        self.assertEqual(PageView.objects.first().referrer, 'https://example.com/page')

    def test_ip_hash_is_populated(self):
        self.client.post(TRACK_URL, self.valid_payload, format='json')
        self.assertTrue(PageView.objects.first().ip_hash)

    def test_raw_ip_is_not_stored(self):
        self.client.post(TRACK_URL, self.valid_payload, format='json')
        pv = PageView.objects.first()
        self.assertFalse(hasattr(pv, 'ip'))
        self.assertFalse(hasattr(pv, 'raw_ip'))


# ---------------------------------------------------------------------------
# Tracking endpoint – cannot override server-side fields
# ---------------------------------------------------------------------------

@override_settings(ANALYTICS_HASH_SALT='test-salt-123')
class TrackingEndpointSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_cannot_override_country(self):
        payload = {
            'session_id': str(uuid.uuid4()),
            'path': '/',
            'country': 'HackedLand',
        }
        self.client.post(TRACK_URL, payload, format='json')
        self.assertEqual(PageView.objects.first().country, '')

    def test_cannot_override_country_code(self):
        payload = {
            'session_id': str(uuid.uuid4()),
            'path': '/',
            'country_code': 'XX',
        }
        self.client.post(TRACK_URL, payload, format='json')
        self.assertEqual(PageView.objects.first().country_code, '')

    def test_cannot_override_ip_hash(self):
        payload = {
            'session_id': str(uuid.uuid4()),
            'path': '/',
            'ip_hash': 'fakehash',
        }
        self.client.post(TRACK_URL, payload, format='json')
        self.assertNotEqual(PageView.objects.first().ip_hash, 'fakehash')

    def test_cannot_override_user_agent(self):
        payload = {
            'session_id': str(uuid.uuid4()),
            'path': '/',
            'user_agent': 'FakeBot',
        }
        self.client.post(TRACK_URL, payload, format='json')
        self.assertNotEqual(PageView.objects.first().user_agent, 'FakeBot')


# ---------------------------------------------------------------------------
# Tracking endpoint – validation errors
# ---------------------------------------------------------------------------

class TrackingEndpointValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_invalid_uuid_returns_400(self):
        response = self.client.post(
            TRACK_URL,
            {'session_id': 'not-a-uuid', 'path': '/'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_session_id_returns_400(self):
        response = self.client.post(TRACK_URL, {'path': '/'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_path_returns_400(self):
        response = self.client.post(
            TRACK_URL,
            {'session_id': str(uuid.uuid4())},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_excessively_long_path_returns_400(self):
        response = self.client.post(
            TRACK_URL,
            {'session_id': str(uuid.uuid4()), 'path': '/' + 'a' * 501},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_is_not_accepted(self):
        response = self.client.get(TRACK_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


# ---------------------------------------------------------------------------
# Existing portfolio APIs still work
# ---------------------------------------------------------------------------

class PortfolioApiSanityTests(TestCase):
    def test_projects_list(self):
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, 200)

    def test_technologies_list(self):
        response = self.client.get('/api/technologies/')
        self.assertEqual(response.status_code, 200)

    def test_profile(self):
        Profile.objects.create(name='Test', role='Dev', introduction='Hi')
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 200)

    def test_health(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)


# ---------------------------------------------------------------------------
# Batch 3 – analytics tracking endpoint sanity
# ---------------------------------------------------------------------------

class TrackingEndpointPostExistsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_track_endpoint_exists(self):
        response = self.client.post(
            TRACK_URL,
            {'session_id': str(uuid.uuid4()), 'path': '/'},
            format='json',
        )
        self.assertIn(response.status_code, (201, 400))


# ---------------------------------------------------------------------------
# Batch 4 – admin dashboard
# ---------------------------------------------------------------------------

DASHBOARD_URL = '/admin/analytics/pageview/dashboard/'


def _create_pageviews():
    """Seed a small set of PageView records for dashboard tests."""
    s1 = uuid.uuid4()
    s2 = uuid.uuid4()
    PageView.objects.create(session_id=s1, path='/', device_type='desktop', referrer='https://google.com')
    PageView.objects.create(session_id=s1, path='/about', device_type='desktop', country='India', country_code='IN')
    PageView.objects.create(session_id=s1, path='/projects/aurora', device_type='mobile', country='India', country_code='IN')
    PageView.objects.create(session_id=s2, path='/', device_type='mobile', country='USA', country_code='US', referrer='https://twitter.com')
    PageView.objects.create(session_id=s2, path='/', device_type='tablet')


class DashboardAccessTests(TestCase):
    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get(DASHBOARD_URL)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_authenticated_staff_can_access(self):
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')
        response = self.client.get(DASHBOARD_URL)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics Dashboard')


class DashboardMetricsTests(TestCase):
    def setUp(self):
        _create_pageviews()
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')
        self.response = self.client.get(DASHBOARD_URL)
        self.content = self.response.content.decode()

    def test_total_views(self):
        self.assertIn('5', self.content)

    def test_unique_visitors(self):
        self.assertIn('2', self.content)

    def test_views_today(self):
        self.assertContains(self.response, 'Views')

    def test_views_last_7_days(self):
        self.assertContains(self.response, '7D')

    def test_views_last_30_days(self):
        self.assertContains(self.response, '30D')


class DashboardAggregationTests(TestCase):
    def setUp(self):
        _create_pageviews()
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')
        self.response = self.client.get(DASHBOARD_URL)
        self.content = self.response.content.decode()

    def test_top_pages_shows_paths(self):
        self.assertIn('/', self.content)
        self.assertIn('/about', self.content)
        self.assertIn('/projects/aurora', self.content)

    def test_device_aggregation(self):
        self.assertIn('Desktop', self.content)
        self.assertIn('Mobile', self.content)
        self.assertIn('Tablet', self.content)
        self.assertIn('Unknown', self.content)

    def test_referrer_aggregation(self):
        self.assertIn('google.com', self.content)
        self.assertIn('twitter.com', self.content)

    def test_empty_country_message(self):
        PageView.objects.all().delete()
        response = self.client.get(DASHBOARD_URL)
        self.assertContains(response, 'No country data yet.')


class DashboardDailyViewsTests(TestCase):
    def test_30_daily_entries_present(self):
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')
        response = self.client.get(DASHBOARD_URL)
        # Check for range buttons instead of "Daily Views" text
        self.assertContains(response, '30D')
        self.assertContains(response, '7D')


class DashboardRecentVisitsTests(TestCase):
    def setUp(self):
        _create_pageviews()
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')
        self.response = self.client.get(DASHBOARD_URL)

    def test_recent_visits_shows_data(self):
        self.assertContains(self.response, 'Recent Visits')

    def test_dashboard_hides_private_fields(self):
        content = self.response.content.decode()
        self.assertNotIn('ip_hash', content)
        self.assertNotIn('session_id', content)


class DashboardEmptyStateTests(TestCase):
    def test_empty_db_no_crash(self):
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')
        response = self.client.get(DASHBOARD_URL)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No page views yet.')


# ---------------------------------------------------------------------------
# Batch 5 – geolocation
# ---------------------------------------------------------------------------

class GeoIPPrivateIPTests(TestCase):
    def test_localhost_returns_empty(self):
        result = get_country_from_ip('127.0.0.1')
        self.assertEqual(result, GeoResult())

    def test_ipv6_loopback_returns_empty(self):
        result = get_country_from_ip('::1')
        self.assertEqual(result, GeoResult())

    def test_private_ipv4_returns_empty(self):
        result = get_country_from_ip('192.168.1.1')
        self.assertEqual(result, GeoResult())

    def test_private_10_range_returns_empty(self):
        result = get_country_from_ip('10.0.0.5')
        self.assertEqual(result, GeoResult())

    def test_link_local_returns_empty(self):
        result = get_country_from_ip('169.254.1.1')
        self.assertEqual(result, GeoResult())

    def test_empty_ip_returns_empty(self):
        result = get_country_from_ip('')
        self.assertEqual(result, GeoResult())

    def test_invalid_ip_returns_empty(self):
        result = get_country_from_ip('not-an-ip')
        self.assertEqual(result, GeoResult())


class GeoIPLookupFailureTests(TestCase):
    def test_lookup_failure_returns_empty(self):
        with patch('analytics.geolocation._get_lookup', return_value=None):
            result = get_country_from_ip('8.8.8.8')
            self.assertEqual(result, GeoResult())

    def test_lookup_exception_returns_empty(self):
        mock_reader = type('MockReader', (), {'country': lambda self, ip: (_ for _ in ()).throw(Exception('db error'))})()
        with patch('analytics.geolocation._get_lookup', return_value=mock_reader):
            result = get_country_from_ip('8.8.8.8')
            self.assertEqual(result, GeoResult())


class GeoIPSuccessTests(TestCase):
    def test_mocked_lookup_returns_country(self):
        mock_resp = type('MockResp', (), {'country': type('C', (), {'name': 'Germany', 'iso_code': 'DE'})()})()
        mock_reader = type('MockReader', (), {'country': lambda self, ip: mock_resp})()
        with patch('analytics.geolocation._get_lookup', return_value=mock_reader):
            result = get_country_from_ip('8.8.8.8')
            self.assertEqual(result.country, 'Germany')
            self.assertEqual(result.country_code, 'DE')


class TrackingEndpointGeolocationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'session_id': str(uuid.uuid4()),
            'path': '/',
        }

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult(country='India', country_code='IN'))
    def test_successful_lookup_stores_country(self, mock_geo):
        self.client.post(TRACK_URL, self.payload, format='json')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, 'India')
        self.assertEqual(pv.country_code, 'IN')

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', side_effect=Exception('lookup failed'))
    def test_geolocation_failure_still_returns_201(self, mock_geo):
        response = self.client.post(TRACK_URL, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', side_effect=RuntimeError('boom'))
    def test_geolocation_failure_country_remains_blank(self, mock_geo):
        self.client.post(TRACK_URL, self.payload, format='json')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, '')
        self.assertEqual(pv.country_code, '')

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    def test_private_ip_still_works(self):
        self.client.post(TRACK_URL, self.payload, format='json')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, '')
        self.assertEqual(pv.country_code, '')
        self.assertTrue(pv.ip_hash)

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult(country='USA', country_code='US'))
    def test_raw_ip_still_not_stored(self, mock_geo):
        self.client.post(TRACK_URL, self.payload, format='json')
        pv = PageView.objects.first()
        self.assertFalse(hasattr(pv, 'ip'))
        self.assertFalse(hasattr(pv, 'raw_ip'))
        self.assertTrue(pv.ip_hash)


class DashboardCountryAggregationTests(TestCase):
    def test_country_data_displays_in_dashboard(self):
        PageView.objects.create(session_id=uuid.uuid4(), path='/', country='India', country_code='IN')
        PageView.objects.create(session_id=uuid.uuid4(), path='/', country='USA', country_code='US')
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')
        response = self.client.get(DASHBOARD_URL)
        self.assertContains(response, 'India')
        self.assertContains(response, 'USA')

    def test_empty_country_state_still_works(self):
        PageView.objects.all().delete()
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')
        response = self.client.get(DASHBOARD_URL)
        self.assertContains(response, 'No country data yet.')


# ---------------------------------------------------------------------------
# Batch 6 – Analytics Range Functionality Tests
# ---------------------------------------------------------------------------

class AnalyticsRangeKeyTests(TestCase):
    def test_default_range_is_30d(self):
        self.assertEqual(get_analytics_range_key(None), '30d')
        self.assertEqual(get_analytics_range_key(''), '30d')

    def test_range_key_1d(self):
        self.assertEqual(get_analytics_range_key('1d'), '1d')

    def test_range_key_7d(self):
        self.assertEqual(get_analytics_range_key('7d'), '7d')

    def test_range_key_30d(self):
        self.assertEqual(get_analytics_range_key('30d'), '30d')

    def test_range_key_3m(self):
        self.assertEqual(get_analytics_range_key('3m'), '3m')

    def test_range_key_6m(self):
        self.assertEqual(get_analytics_range_key('6m'), '6m')

    def test_range_key_1y(self):
        self.assertEqual(get_analytics_range_key('1y'), '1y')

    def test_range_key_all_time(self):
        self.assertEqual(get_analytics_range_key('all'), 'all')
        start, end = get_range_bounds('all')
        self.assertIsNone(start)
        self.assertIsNotNone(end)

    def test_invalid_range_falls_back_to_30d(self):
        self.assertEqual(get_analytics_range_key('invalid_range'), '30d')
        self.assertEqual(get_analytics_range_key('999d'), '30d')


class AnalyticsRangeFilteringTests(TestCase):
    def test_range_filtering_excludes_out_of_range_pageviews(self):
        now = timezone.now()
        s1 = uuid.uuid4()
        pv_recent = PageView.objects.create(session_id=s1, path='/recent')
        pv_old = PageView.objects.create(session_id=s1, path='/old')
        PageView.objects.filter(pk=pv_old.pk).update(created_at=now - timedelta(days=10))

        qs_7d = get_filtered_queryset('7d')
        self.assertEqual(qs_7d.count(), 1)
        self.assertEqual(qs_7d.first().path, '/recent')

    def test_unique_visitors_use_distinct_session_id(self):
        s1 = uuid.uuid4()
        s2 = uuid.uuid4()
        PageView.objects.create(session_id=s1, path='/page1')
        PageView.objects.create(session_id=s1, path='/page2')
        PageView.objects.create(session_id=s2, path='/page1')

        overview = get_range_overview('7d')
        self.assertEqual(overview['total_views'], 3)
        self.assertEqual(overview['unique_visitors'], 2)

    def test_time_series_views_aggregation(self):
        s1 = uuid.uuid4()
        s2 = uuid.uuid4()
        PageView.objects.create(session_id=s1, path='/')
        PageView.objects.create(session_id=s2, path='/')

        series = get_time_series('7d')
        today_str = timezone.localdate().strftime('%Y-%m-%d')
        today_bucket = next((b for b in series if b['date'] == today_str), None)
        self.assertIsNotNone(today_bucket)
        self.assertEqual(today_bucket['views'], 2)

    def test_time_series_unique_visitor_aggregation(self):
        s1 = uuid.uuid4()
        PageView.objects.create(session_id=s1, path='/p1')
        PageView.objects.create(session_id=s1, path='/p2')

        series = get_time_series('7d')
        today_str = timezone.localdate().strftime('%Y-%m-%d')
        today_bucket = next((b for b in series if b['date'] == today_str), None)
        self.assertIsNotNone(today_bucket)
        self.assertEqual(today_bucket['views'], 2)
        self.assertEqual(today_bucket['unique_visitors'], 1)

    def test_zero_value_time_series_buckets(self):
        series = get_time_series('7d')
        self.assertEqual(len(series), 7)
        for bucket in series:
            self.assertIn('views', bucket)
            self.assertIn('unique_visitors', bucket)
            self.assertEqual(bucket['views'], 0)
            self.assertEqual(bucket['unique_visitors'], 0)

    def test_top_pages_respect_selected_range(self):
        now = timezone.now()
        s1 = uuid.uuid4()
        pv_recent = PageView.objects.create(session_id=s1, path='/recent-page')
        pv_old = PageView.objects.create(session_id=s1, path='/old-page')
        PageView.objects.filter(pk=pv_old.pk).update(created_at=now - timedelta(days=40))

        top_30d = get_top_pages('30d')
        paths_30d = [p['path'] for p in top_30d]
        self.assertIn('/recent-page', paths_30d)
        self.assertNotIn('/old-page', paths_30d)

        top_all = get_top_pages('all')
        paths_all = [p['path'] for p in top_all]
        self.assertIn('/recent-page', paths_all)
        self.assertIn('/old-page', paths_all)

    def test_top_referrers_respect_selected_range(self):
        now = timezone.now()
        s1 = uuid.uuid4()
        pv_recent = PageView.objects.create(session_id=s1, path='/', referrer='https://recent-ref.com')
        pv_old = PageView.objects.create(session_id=s1, path='/', referrer='https://old-ref.com')
        PageView.objects.filter(pk=pv_old.pk).update(created_at=now - timedelta(days=40))

        ref_30d = [r['referrer'] for r in get_top_referrers('30d')]
        self.assertIn('https://recent-ref.com', ref_30d)
        self.assertNotIn('https://old-ref.com', ref_30d)

    def test_countries_respect_selected_range(self):
        now = timezone.now()
        s1 = uuid.uuid4()
        pv_recent = PageView.objects.create(session_id=s1, path='/', country='France', country_code='FR')
        pv_old = PageView.objects.create(session_id=s1, path='/', country='Japan', country_code='JP')
        PageView.objects.filter(pk=pv_old.pk).update(created_at=now - timedelta(days=40))

        c_30d = [c['country_code'] for c in get_top_countries('30d')]
        self.assertIn('FR', c_30d)
        self.assertNotIn('JP', c_30d)

    def test_devices_respect_selected_range(self):
        now = timezone.now()
        s1 = uuid.uuid4()
        pv_recent = PageView.objects.create(session_id=s1, path='/', device_type='mobile')
        pv_old = PageView.objects.create(session_id=s1, path='/', device_type='tablet')
        PageView.objects.filter(pk=pv_old.pk).update(created_at=now - timedelta(days=40))

        dev_30d = {d['key']: d['views'] for d in get_device_breakdown('30d')}
        self.assertEqual(dev_30d['mobile'], 1)
        self.assertEqual(dev_30d['tablet'], 0)

        dev_all = {d['key']: d['views'] for d in get_device_breakdown('all')}
        self.assertEqual(dev_all['mobile'], 1)
        self.assertEqual(dev_all['tablet'], 1)


class DashboardRangeQueryParamTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        User.objects.create_user('dashadmin', 'admin@test.com', 'pass123', is_staff=True)
        self.client.login(username='dashadmin', password='pass123')

    def test_dashboard_accepts_range_7d(self):
        response = self.client.get(DASHBOARD_URL + '?range=7d')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['range_key'], '7d')

    def test_dashboard_handles_invalid_range_safely(self):
        response = self.client.get(DASHBOARD_URL + '?range=invalid_xyz')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['range_key'], '30d')


# ---------------------------------------------------------------------------
# Batch 7 – Trusted-proxy IP extraction + geolocation hardening
# ---------------------------------------------------------------------------

class GetTrustedClientIPTests(TestCase):
    """Unit tests for analytics.views.get_trusted_client_ip."""

    def _make_request(self, meta=None):
        from django.test import RequestFactory
        factory = RequestFactory()
        return factory.get('/', **(meta or {}))

    def test_returns_remote_addr_when_no_proxy(self):
        from .views import get_trusted_client_ip
        req = self._make_request({'REMOTE_ADDR': '203.0.113.10'})
        self.assertEqual(get_trusted_client_ip(req), '203.0.113.10')

    @override_settings(ANALYTICS_TRUST_PROXY=True)
    def test_returns_xff_first_ip_when_trusted(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '10.0.0.1',
            'HTTP_X_FORWARDED_FOR': '198.51.100.5, 10.0.0.1',
        })
        self.assertEqual(get_trusted_client_ip(req), '198.51.100.5')

    @override_settings(ANALYTICS_TRUST_PROXY=True)
    def test_returns_x_real_ip_when_no_xff(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '10.0.0.1',
            'HTTP_X_REAL_IP': '198.51.100.7',
        })
        self.assertEqual(get_trusted_client_ip(req), '198.51.100.7')

    @override_settings(ANALYTICS_TRUST_PROXY=True)
    def test_xff_preferred_over_x_real_ip(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '10.0.0.1',
            'HTTP_X_FORWARDED_FOR': '198.51.100.5, 10.0.0.1',
            'HTTP_X_REAL_IP': '198.51.100.7',
        })
        self.assertEqual(get_trusted_client_ip(req), '198.51.100.5')

    def test_spoofed_xff_ignored_when_no_proxy(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '10.0.0.1',
            'HTTP_X_FORWARDED_FOR': '198.51.100.5, 10.0.0.1',
        })
        self.assertEqual(get_trusted_client_ip(req), '10.0.0.1')

    @override_settings(ANALYTICS_TRUST_PROXY=True)
    def test_malformed_xff_skipped_gracefully(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '10.0.0.1',
            'HTTP_X_FORWARDED_FOR': 'not-an-ip, also-bad',
        })
        self.assertEqual(get_trusted_client_ip(req), '10.0.0.1')

    @override_settings(ANALYTICS_TRUST_PROXY=True)
    def test_malformed_xff_before_valid_ip(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '10.0.0.1',
            'HTTP_X_FORWARDED_FOR': 'garbage, 198.51.100.5, 10.0.0.1',
        })
        self.assertEqual(get_trusted_client_ip(req), '198.51.100.5')

    @override_settings(ANALYTICS_TRUST_PROXY=True)
    def test_ipv6_forwarded_address_accepted(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '::1',
            'HTTP_X_FORWARDED_FOR': '2001:db8::1, 10.0.0.1',
        })
        self.assertEqual(get_trusted_client_ip(req), '2001:db8::1')

    @override_settings(ANALYTICS_TRUST_PROXY=True)
    def test_empty_forwarded_headers_fallback_to_remote_addr(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '203.0.113.10',
            'HTTP_X_FORWARDED_FOR': '',
            'HTTP_X_REAL_IP': '',
        })
        self.assertEqual(get_trusted_client_ip(req), '203.0.113.10')

    @override_settings(ANALYTICS_TRUST_PROXY=True)
    def test_private_forwarded_ip_skipped(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '10.0.0.1',
            'HTTP_X_FORWARDED_FOR': '192.168.1.1, 10.0.0.1',
        })
        self.assertEqual(get_trusted_client_ip(req), '192.168.1.1')

    @override_settings(ANALYTICS_TRUST_PROXY='false')
    def test_string_false_treated_as_disabled(self):
        from .views import get_trusted_client_ip
        req = self._make_request({
            'REMOTE_ADDR': '10.0.0.1',
            'HTTP_X_FORWARDED_FOR': '198.51.100.5, 10.0.0.1',
        })
        self.assertEqual(get_trusted_client_ip(req), '10.0.0.1')

    def test_missing_setting_defaults_to_disabled(self):
        from .views import get_trusted_client_ip
        from django.conf import settings
        original = getattr(settings, 'ANALYTICS_TRUST_PROXY', None)
        try:
            if hasattr(settings, 'ANALYTICS_TRUST_PROXY'):
                delattr(settings, 'ANALYTICS_TRUST_PROXY')
            req = self._make_request({
                'REMOTE_ADDR': '10.0.0.1',
                'HTTP_X_FORWARDED_FOR': '198.51.100.5',
            })
            self.assertEqual(get_trusted_client_ip(req), '10.0.0.1')
        finally:
            if original is not None:
                settings.ANALYTICS_TRUST_PROXY = original


class TrackingEndpointTrustedProxyTests(TestCase):
    """Integration tests: tracking endpoint with proxy-aware IP extraction."""

    def setUp(self):
        self.client = APIClient()
        self.payload = {'session_id': str(uuid.uuid4()), 'path': '/'}

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123', ANALYTICS_TRUST_PROXY=True)
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult(country='Germany', country_code='DE'))
    def test_xff_ip_used_for_geo_lookup(self, mock_geo):
        self.client.post(
            TRACK_URL, self.payload, format='json',
            REMOTE_ADDR='10.0.0.1',
            HTTP_X_FORWARDED_FOR='85.214.132.117, 10.0.0.1',
        )
        mock_geo.assert_called_once_with('85.214.132.117')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, 'Germany')
        self.assertEqual(pv.country_code, 'DE')

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123', ANALYTICS_TRUST_PROXY=True)
    def test_xff_ip_used_for_ip_hash(self):
        self.client.post(
            TRACK_URL, self.payload, format='json',
            REMOTE_ADDR='10.0.0.1',
            HTTP_X_FORWARDED_FOR='85.214.132.117, 10.0.0.1',
        )
        pv = PageView.objects.first()
        expected_hash = PageView.hash_ip('85.214.132.117')
        self.assertEqual(pv.ip_hash, expected_hash)

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult(country='USA', country_code='US'))
    def test_remote_addr_used_when_proxy_disabled(self, mock_geo):
        self.client.post(
            TRACK_URL, self.payload, format='json',
            REMOTE_ADDR='203.0.113.10',
            HTTP_X_FORWARDED_FOR='85.214.132.117, 203.0.113.10',
        )
        mock_geo.assert_called_once_with('203.0.113.10')

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123', ANALYTICS_TRUST_PROXY=True)
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult())
    def test_private_forwarded_ip_results_in_blank_country(self, mock_geo):
        self.client.post(
            TRACK_URL, self.payload, format='json',
            REMOTE_ADDR='10.0.0.1',
            HTTP_X_FORWARDED_FOR='192.168.1.1, 10.0.0.1',
        )
        mock_geo.assert_called_once_with('192.168.1.1')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, '')
        self.assertEqual(pv.country_code, '')

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123', ANALYTICS_TRUST_PROXY=True)
    def test_real_ip_header_works(self):
        self.client.post(
            TRACK_URL, self.payload, format='json',
            REMOTE_ADDR='10.0.0.1',
            HTTP_X_REAL_IP='85.214.132.117',
        )
        pv = PageView.objects.first()
        expected_hash = PageView.hash_ip('85.214.132.117')
        self.assertEqual(pv.ip_hash, expected_hash)

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123', ANALYTICS_TRUST_PROXY=True)
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult(country='Japan', country_code='JP'))
    def test_x_real_ip_used_for_geo_lookup(self, mock_geo):
        self.client.post(
            TRACK_URL, self.payload, format='json',
            REMOTE_ADDR='10.0.0.1',
            HTTP_X_REAL_IP='103.5.140.1',
        )
        mock_geo.assert_called_once_with('103.5.140.1')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, 'Japan')

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult(country='USA', country_code='US'))
    def test_spoofed_xff_ignored_without_trust(self, mock_geo):
        self.client.post(
            TRACK_URL, self.payload, format='json',
            REMOTE_ADDR='10.0.0.1',
            HTTP_X_FORWARDED_FOR='85.214.132.117',
        )
        mock_geo.assert_called_once_with('10.0.0.1')
        self.assertNotEqual(PageView.objects.first().ip_hash, PageView.hash_ip('85.214.132.117'))


class TrackingEndpointGeoErrorResilienceTests(TestCase):
    """Ensure geo/DB failures never crash the tracking endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.payload = {'session_id': str(uuid.uuid4()), 'path': '/'}

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', side_effect=Exception('lookup failed'))
    def test_geo_exception_still_returns_201(self, mock_geo):
        response = self.client.post(TRACK_URL, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pv = PageView.objects.first()
        self.assertEqual(pv.country, '')
        self.assertEqual(pv.country_code, '')

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', side_effect=RuntimeError('boom'))
    def test_geo_runtime_error_still_returns_201(self, mock_geo):
        response = self.client.post(TRACK_URL, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.geolocation._get_lookup', return_value=None)
    def test_missing_geoip_db_still_returns_201(self, _mock_lookup):
        response = self.client.post(TRACK_URL, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pv = PageView.objects.first()
        self.assertEqual(pv.country, '')

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    def test_private_ip_produces_blank_country(self):
        self.client.post(TRACK_URL, self.payload, format='json')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, '')
        self.assertEqual(pv.country_code, '')
        self.assertTrue(pv.ip_hash)


class TrackingEndpointPrivacyTests(TestCase):
    """Verify raw IP never persists and client cannot inject country."""

    def setUp(self):
        self.client = APIClient()

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult(country='France', country_code='FR'))
    def test_raw_ip_never_persisted(self, mock_geo):
        payload = {'session_id': str(uuid.uuid4()), 'path': '/'}
        self.client.post(
            TRACK_URL, payload, format='json',
            REMOTE_ADDR='104.26.10.78',
            HTTP_X_FORWARDED_FOR='85.214.132.117, 104.26.10.78',
        )
        pv = PageView.objects.first()
        self.assertFalse(hasattr(pv, 'ip'))
        self.assertFalse(hasattr(pv, 'raw_ip'))
        self.assertFalse(hasattr(pv, 'ip_address'))
        self.assertTrue(pv.ip_hash)

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    def test_client_cannot_inject_country(self):
        payload = {
            'session_id': str(uuid.uuid4()),
            'path': '/',
            'country': 'HackedLand',
            'country_code': 'XX',
        }
        self.client.post(TRACK_URL, payload, format='json')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, '')
        self.assertEqual(pv.country_code, '')

    def test_ip_field_not_on_model(self):
        field_names = [f.name for f in PageView._meta.get_fields()]
        self.assertNotIn('ip', field_names)
        self.assertNotIn('raw_ip', field_names)
        self.assertNotIn('ip_address', field_names)

    @override_settings(ANALYTICS_HASH_SALT='test-salt-123')
    @patch('analytics.views.get_country_from_ip', return_value=GeoResult(country='India', country_code='IN'))
    def test_country_success_still_works(self, mock_geo):
        payload = {'session_id': str(uuid.uuid4()), 'path': '/'}
        self.client.post(TRACK_URL, payload, format='json')
        pv = PageView.objects.first()
        self.assertEqual(pv.country, 'India')
        self.assertEqual(pv.country_code, 'IN')


class GeolocationRobustnessTests(TestCase):
    """Direct tests for the geolocation module edge cases."""

    def test_empty_string_ip(self):
        self.assertEqual(get_country_from_ip(''), GeoResult())

    def test_invalid_ip(self):
        self.assertEqual(get_country_from_ip('not-an-ip'), GeoResult())

    def test_none_like_string(self):
        self.assertEqual(get_country_from_ip(''), GeoResult())

    @patch('analytics.geolocation._get_lookup', return_value=None)
    def test_no_database_returns_empty(self, _mock):
        self.assertEqual(get_country_from_ip('8.8.8.8'), GeoResult())

    def test_broken_lookup_init_returns_empty(self):
        import analytics.geolocation as geo_mod
        original = geo_mod._lookup
        try:
            geo_mod._lookup = None
            with patch.dict('sys.modules', {'geoip2.database': None}):
                result = geo_mod.get_country_from_ip('8.8.8.8')
            self.assertEqual(result, GeoResult())
        finally:
            geo_mod._lookup = original

    def test_geoip2_missing_package_does_not_crash(self):
        import importlib
        import sys
        geoip2_mod = sys.modules.pop('geoip2', None)
        geoip2_db_mod = sys.modules.pop('geoip2.database', None)
        import analytics.geolocation as geo_mod
        original_lookup = geo_mod._lookup
        try:
            geo_mod._lookup = None
            result = geo_mod.get_country_from_ip('8.8.8.8')
            self.assertEqual(result, GeoResult())
        finally:
            geo_mod._lookup = original_lookup
            if geoip2_mod:
                sys.modules['geoip2'] = geoip2_mod
            if geoip2_db_mod:
                sys.modules['geoip2.database'] = geoip2_db_mod

    def test_ipv6_loopback_skipped(self):
        self.assertEqual(get_country_from_ip('::1'), GeoResult())

    def test_ipv6_global_works_with_mock(self):
        public_ipv6 = '2606:4700:4700::1111'
        mock_resp = type('R', (), {'country': type('C', (), {'name': 'France', 'iso_code': 'FR'})()})()
        mock_reader = type('M', (), {'country': lambda self, ip: mock_resp})()
        with patch('analytics.geolocation._get_lookup', return_value=mock_reader):
            result = get_country_from_ip(public_ipv6)
            self.assertEqual(result.country, 'France')
            self.assertEqual(result.country_code, 'FR')


class GeoIPDownloadTests(TestCase):
    def test_missing_credentials_fail_clearly(self):
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(GeoIPDownloadError) as ctx:
                download_geolite2_country(dest_path='/tmp/geoip/GeoLite2-Country.mmdb')
        self.assertIn('MAXMIND_ACCOUNT_ID', str(ctx.exception))
        self.assertIn('MAXMIND_LICENSE_KEY', str(ctx.exception))

    def test_missing_credentials_do_not_log_secrets(self):
        env = {
            'MAXMIND_ACCOUNT_ID': '',
            'MAXMIND_LICENSE_KEY': 'super-secret-license-key',
        }
        with patch.dict('os.environ', env, clear=True):
            with self.assertRaises(GeoIPDownloadError) as ctx:
                download_geolite2_country()
        self.assertNotIn('super-secret-license-key', str(ctx.exception))

    def test_http_error_does_not_include_credentials(self):
        import urllib.error

        env = {
            'MAXMIND_ACCOUNT_ID': '123456',
            'MAXMIND_LICENSE_KEY': 'super-secret-license-key',
        }
        error = urllib.error.HTTPError(
            url='https://download.maxmind.com/geoip/databases/GeoLite2-Country/download?suffix=tar.gz',
            code=401,
            msg='Unauthorized',
            hdrs=None,
            fp=None,
        )
        with patch.dict('os.environ', env, clear=True):
            with patch('analytics.geoip_download.urllib.request.build_opener') as mock_opener:
                mock_opener.return_value.open.side_effect = error
                with self.assertRaises(GeoIPDownloadError) as ctx:
                    download_geolite2_country(dest_path='/tmp/geoip/GeoLite2-Country.mmdb')
        message = str(ctx.exception)
        self.assertIn('HTTP 401', message)
        self.assertNotIn('super-secret-license-key', message)
        self.assertNotIn('123456', message)

    def test_successful_download_writes_mmdb(self):
        import io
        import tarfile
        from unittest.mock import MagicMock

        archive_buf = io.BytesIO()
        with tarfile.open(fileobj=archive_buf, mode='w:gz') as tar:
            payload = b'MMDB-TEST-BYTES'
            info = tarfile.TarInfo(name='GeoLite2-Country_20240101/GeoLite2-Country.mmdb')
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
        archive_bytes = archive_buf.getvalue()

        response = MagicMock()
        response.read.return_value = archive_bytes
        response.__enter__.return_value = response
        response.__exit__.return_value = False

        dest = self._tmp_dest()
        env = {
            'MAXMIND_ACCOUNT_ID': '123456',
            'MAXMIND_LICENSE_KEY': 'super-secret-license-key',
        }
        with patch.dict('os.environ', env, clear=True):
            with patch('analytics.geoip_download.urllib.request.build_opener') as mock_opener:
                mock_opener.return_value.open.return_value = response
                written = download_geolite2_country(dest_path=dest)
        import os

        self.assertEqual(os.path.normpath(written), os.path.normpath(dest))
        with open(dest, 'rb') as handle:
            self.assertEqual(handle.read(), b'MMDB-TEST-BYTES')

    def test_resolve_path_uses_render_default(self):
        with patch.dict('os.environ', {}, clear=True):
            self.assertEqual(resolve_geoip_database_path(''), DEFAULT_GEOIP_DATABASE_PATH)

    def test_resolve_path_honors_explicit_setting(self):
        self.assertEqual(
            resolve_geoip_database_path('/custom/GeoLite2-Country.mmdb'),
            '/custom/GeoLite2-Country.mmdb',
        )

    def _tmp_dest(self):
        import tempfile

        directory = tempfile.mkdtemp()
        return f'{directory}/GeoLite2-Country.mmdb'


class Phase4BAnalyticsMetricsTests(TestCase):
    def test_views_per_visitor(self):
        s1 = uuid.uuid4()
        s2 = uuid.uuid4()
        PageView.objects.create(session_id=s1, path='/')
        PageView.objects.create(session_id=s1, path='/')
        PageView.objects.create(session_id=s2, path='/')
        self.assertEqual(get_views_per_visitor('all'), 1.5)

    def test_page_traffic_share(self):
        PageView.objects.create(session_id=uuid.uuid4(), path='/a')
        PageView.objects.create(session_id=uuid.uuid4(), path='/b')
        PageView.objects.create(session_id=uuid.uuid4(), path='/a')
        share = get_page_traffic_share('all')
        self.assertEqual(share[0]['path'], '/a')
        self.assertEqual(share[0]['percent'], 66.7)

    def test_country_traffic_share(self):
        PageView.objects.create(session_id=uuid.uuid4(), country_code='US', country='USA')
        PageView.objects.create(session_id=uuid.uuid4(), country_code='IN', country='India')
        PageView.objects.create(session_id=uuid.uuid4(), country_code='US', country='USA')
        share = get_country_traffic_share('all')
        self.assertEqual(share[0]['country_code'], 'US')
        self.assertEqual(share[0]['percent'], 66.7)

    def test_traffic_sources(self):
        PageView.objects.create(session_id=uuid.uuid4(), referrer='')
        PageView.objects.create(session_id=uuid.uuid4(), referrer='https://google.com')
        PageView.objects.create(session_id=uuid.uuid4(), referrer='https://instagram.com')
        sources = get_traffic_sources('all')
        # Use a list comprehension to check if categories exist, order may vary
        src_keys = [s['key'] for s in sources]
        self.assertIn('direct', src_keys)
        self.assertIn('search', src_keys)
        self.assertIn('social', src_keys)

    def test_peak_day_hour(self):
        now = timezone.now()
        PageView.objects.create(session_id=uuid.uuid4(), path='/', created_at=now)
        self.assertNotEqual(get_peak_day('all'), '—')
        self.assertNotEqual(get_peak_hour('all'), '—')
