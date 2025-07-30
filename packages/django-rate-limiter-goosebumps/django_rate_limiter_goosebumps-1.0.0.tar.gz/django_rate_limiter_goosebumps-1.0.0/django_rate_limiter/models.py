"""
Django models for rate limiting storage.
"""

from django.db import models
from django.utils import timezone


class RateLimitEntry(models.Model):
    """Model to store rate limiting data in the database."""

    key = models.CharField(max_length=255, unique=True, db_index=True)
    data = models.TextField(help_text="JSON data for rate limiting")
    expires_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "django_rate_limiter_entry"
        indexes = [
            models.Index(fields=["key", "expires_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"RateLimitEntry(key={self.key}, expires_at={self.expires_at})"

    def is_expired(self):
        """Check if the entry is expired."""
        return timezone.now() > self.expires_at

    @classmethod
    def cleanup_expired(cls):
        """Remove expired entries."""
        return cls.objects.filter(expires_at__lt=timezone.now()).delete()
