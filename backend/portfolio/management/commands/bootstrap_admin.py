import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create a Django superuser from environment variables (idempotent).'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME', '')
        email = os.getenv('ADMIN_EMAIL', '')
        password = os.getenv('ADMIN_PASSWORD', '')

        if not all([username, email, password]):
            self.stdout.write(
                self.style.NOTICE(
                    'Admin bootstrap skipped — ADMIN_USERNAME, ADMIN_EMAIL, '
                    'and ADMIN_PASSWORD environment variables are not all configured.'
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.NOTICE(
                    f'Admin bootstrap — user "{username}" already exists. '
                    'No changes made.'
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Admin bootstrap — superuser "{username}" created successfully.'
            )
        )
