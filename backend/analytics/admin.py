from django.contrib import admin
from django.urls import path
from django.utils.html import format_html

from .models import PageView
from .services import (
    get_daily_views,
    get_device_breakdown,
    get_overview_stats,
    get_recent_visits,
    get_top_countries,
    get_top_pages,
    get_top_referrers,
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

        context = {
            **self.admin_site.each_context(request),
            'title': 'Analytics Dashboard',
            'stats': get_overview_stats(),
            'top_pages': get_top_pages(),
            'top_countries': get_top_countries(),
            'devices': get_device_breakdown(),
            'top_referrers': get_top_referrers(),
            'daily_views': get_daily_views(),
            'recent_visits': get_recent_visits(),
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
