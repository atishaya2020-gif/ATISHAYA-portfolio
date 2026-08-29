from django.contrib import admin
from django.urls import path
from django.utils.html import format_html

from .models import PageView
from .services import (
    VALID_RANGES,
    get_analytics_range_key,
    get_country_traffic_share,
    get_daily_views,
    get_device_breakdown,
    get_insights,
    get_landing_pages,
    get_overview_stats,
    get_page_traffic_share,
    get_recent_visits,
    get_time_series,
    get_top_countries,
    get_top_pages,
    get_top_referrers,
    get_traffic_sources,
    get_views_per_visitor,
)


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'path',
        'country',
        'country_code',
        'device_type',
        'referrer',
        'dashboard_link',
    )
    list_filter = ('country_code', 'device_type', 'created_at')
    search_fields = ('path', 'country', 'country_code', 'referrer')
    ordering = ('-created_at',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'dashboard/',
                self.admin_site.admin_view(self.dashboard_view),
                name='analytics_pageview_dashboard',
            ),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        from django.shortcuts import render

        range_param = request.GET.get('range', '30d')
        range_key = get_analytics_range_key(range_param)

        context = {
            **self.admin_site.each_context(request),
            'title': 'Analytics Dashboard',
            'range_key': range_key,
            'valid_ranges': VALID_RANGES,
            'stats': get_overview_stats(range_key),
            'views_per_visitor': get_views_per_visitor(range_key),
            'time_series': get_time_series(range_key),
            'top_pages': get_page_traffic_share(range_key),
            'top_countries': get_country_traffic_share(range_key),
            'devices': get_device_breakdown(range_key),
            'top_referrers': get_top_referrers(range_key),
            'traffic_sources': get_traffic_sources(range_key),
            'landing_pages': get_landing_pages(range_key),
            'insights': get_insights(range_key),
            'daily_views': get_daily_views(),
            'recent_visits': get_recent_visits(range_key),
        }
        return render(
            request,
            'admin/analytics/pageview_dashboard.html',
            context,
        )

    @admin.display(description='Dashboard')
    def dashboard_link(self, obj):
        return format_html(
            '<a href="{}">View analytics</a>',
            '/admin/analytics/pageview/dashboard/',
        )
