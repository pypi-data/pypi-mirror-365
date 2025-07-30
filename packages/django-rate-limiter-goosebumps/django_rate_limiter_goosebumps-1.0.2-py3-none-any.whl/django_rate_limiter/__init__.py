"""
Django Rate Limiter

A comprehensive Django rate limiter with multiple algorithms and storage backends.
Supports sliding window, token bucket, and fixed window rate limiting with
thread-safe, deadlock-safe implementation.
"""

__version__ = "1.0.2"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .algorithms import (
    FixedWindowRateLimiter,
    SlidingWindowRateLimiter,
    TokenBucketRateLimiter,
)
from .backends import DatabaseBackend, MemoryBackend, RedisBackend
from .decorators import rate_limit
from .exceptions import RateLimitExceeded
from .middleware import RateLimitMiddleware

__all__ = [
    "rate_limit",
    "RateLimitMiddleware",
    "SlidingWindowRateLimiter",
    "TokenBucketRateLimiter",
    "FixedWindowRateLimiter",
    "MemoryBackend",
    "DatabaseBackend",
    "RedisBackend",
    "RateLimitExceeded",
]
