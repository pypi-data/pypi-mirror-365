"""
Django management commands for rate limiter maintenance.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from django_rate_limiter.models import RateLimitEntry


class Command(BaseCommand):
    """Clean up expired rate limit entries from the database."""

    help = "Clean up expired rate limit entries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Count expired entries
        expired_count = RateLimitEntry.objects.filter(
            expires_at__lt=timezone.now()
        ).count()

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Would delete {expired_count} expired rate limit entries"
                )
            )
        else:
            # Delete expired entries
            deleted_count, _ = RateLimitEntry.objects.filter(
                expires_at__lt=timezone.now()
            ).delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {deleted_count} expired rate limit entries"
                )
            )
