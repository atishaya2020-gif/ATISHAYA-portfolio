from django.core.management.base import BaseCommand

from analytics.anomaly import detect_analytics_anomalies


class Command(BaseCommand):
    help = 'Detect unusual hourly traffic patterns in analytics.'

    def add_arguments(self, parser):
        parser.add_argument('--lookback-days', type=int, default=14)
        parser.add_argument('--no-pages', action='store_true')

    def handle(self, *args, **options):
        anomalies = detect_analytics_anomalies(
            lookback_days=max(1, options['lookback_days']),
            include_pages=not options['no_pages'],
        )
        if not anomalies:
            self.stdout.write(self.style.SUCCESS('No new analytics anomalies detected.'))
            return
        self.stdout.write(self.style.WARNING(f'Detected {len(anomalies)} new analytics anomalies.'))
        for anomaly in anomalies:
            target = anomaly.dimension or 'all traffic'
            self.stdout.write(
                f'  [{anomaly.severity:>3}] {anomaly.get_kind_display()} · {target} · '
                f'{anomaly.current_value:g} vs {anomaly.baseline_value:g} '
                f'({anomaly.deviation_percent:+.1f}%)'
            )
