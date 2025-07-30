"""
Django app configuration for rate limiter.
"""

from django.apps import AppConfig


class DjangoRateLimiterConfig(AppConfig):
    """Configuration for Django Rate Limiter app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_rate_limiter"
    verbose_name = "Django Rate Limiter"

    def ready(self):
        """Initialize app when Django starts."""
        # Import signal handlers or other initialization code here
        pass
