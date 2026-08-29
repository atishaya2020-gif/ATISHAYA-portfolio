from django.core.management.base import BaseCommand, CommandError

from analytics.geoip_download import GeoIPDownloadError, download_geolite2_country


class Command(BaseCommand):
    help = 'Download GeoLite2-Country.mmdb from MaxMind using account credentials.'

    def handle(self, *args, **options):
        try:
            dest = download_geolite2_country()
        except GeoIPDownloadError as exc:
            raise CommandError(str(exc)) from None

        self.stdout.write(self.style.SUCCESS(f'GeoLite2-Country database written to {dest}'))
