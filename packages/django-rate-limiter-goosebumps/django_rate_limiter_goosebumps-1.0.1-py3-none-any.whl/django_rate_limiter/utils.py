"""
Utility functions for Django Rate Limiter.
"""

import hashlib
import time
from typing import Any, Dict, List

from django.conf import settings

from .algorithms import get_rate_limiter
from .backends import get_backend
from .exceptions import RateLimitExceeded


def check_rate_limit(
    identifier: str,
    limit: int,
    window: int,
    algorithm: str = "sliding_window",
    backend: str = "memory",
    scope: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    """
    Utility function to check rate limit programmatically.

    Args:
        identifier: Unique identifier for the client
        limit: Maximum number of requests allowed
        window: Time window in seconds
        algorithm: Rate limiting algorithm
        backend: Storage backend
        scope: Scope for grouping
        **kwargs: Additional arguments

    Returns:
        Dictionary containing rate limit information

    Raises:
        RateLimitExceeded: If rate limit is exceeded
    """
    backend_instance = get_backend(backend)
    rate_limiter = get_rate_limiter(algorithm=algorithm, backend=backend_instance)

    allowed, metadata = rate_limiter.is_allowed(identifier, limit, window, scope)

    if not allowed:
        raise RateLimitExceeded(
            f"Rate limit exceeded for {identifier}",
            retry_after=metadata.get("retry_after"),
            limit=limit,
            window=window,
        )

    return metadata


def is_rate_limited(
    identifier: str,
    limit: int,
    window: int,
    algorithm: str = "sliding_window",
    backend: str = "memory",
    scope: str = "default",
    **kwargs,
) -> bool:
    """
    Check if an identifier is currently rate limited without raising an exception.

    Args:
        identifier: Unique identifier for the client
        limit: Maximum number of requests allowed
        window: Time window in seconds
        algorithm: Rate limiting algorithm
        backend: Storage backend
        scope: Scope for grouping
        **kwargs: Additional arguments

    Returns:
        True if rate limited, False otherwise
    """
    try:
        check_rate_limit(identifier, limit, window, algorithm, backend, scope, **kwargs)
        return False
    except RateLimitExceeded:
        return True


def get_rate_limit_status(
    identifier: str,
    limit: int,
    window: int,
    algorithm: str = "sliding_window",
    backend: str = "memory",
    scope: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    """
    Get rate limit status without affecting the count.

    Args:
        identifier: Unique identifier for the client
        limit: Maximum number of requests allowed
        window: Time window in seconds
        algorithm: Rate limiting algorithm
        backend: Storage backend
        scope: Scope for grouping
        **kwargs: Additional arguments

    Returns:
        Dictionary containing rate limit status
    """
    backend_instance = get_backend(backend)
    rate_limiter = get_rate_limiter(algorithm=algorithm, backend=backend_instance)

    # Get current status without incrementing
    key = rate_limiter._get_key(identifier, scope)
    current_data = backend_instance.get(key)

    if current_data is None:
        return {
            "current_count": 0,
            "remaining": limit,
            "limit": limit,
            "window": window,
            "reset_time": time.time() + window,
            "is_limited": False,
        }

    # This is simplified - actual implementation depends on algorithm
    current_count = current_data.get("count", 0)
    remaining = max(0, limit - current_count)

    return {
        "current_count": current_count,
        "remaining": remaining,
        "limit": limit,
        "window": window,
        "reset_time": time.time() + window,
        "is_limited": current_count >= limit,
    }


def clear_rate_limit(
    identifier: str,
    scope: str = "default",
    algorithm: str = "sliding_window",
    backend: str = "memory",
):
    """
    Clear rate limit data for a specific identifier.

    Args:
        identifier: Unique identifier for the client
        scope: Scope for grouping
        algorithm: Rate limiting algorithm (used for key generation)
        backend: Storage backend
    """
    backend_instance = get_backend(backend)
    rate_limiter = get_rate_limiter(algorithm=algorithm, backend=backend_instance)
    key = rate_limiter._get_key(identifier, scope)
    backend_instance.delete(key)


def generate_api_key_hash(api_key: str) -> str:
    """
    Generate a hash for API key to use as identifier.

    Args:
        api_key: The API key to hash

    Returns:
        Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()[:32]


def get_request_fingerprint(request) -> str:
    """
    Generate a unique fingerprint for a request based on multiple factors.

    Args:
        request: Django HttpRequest object

    Returns:
        Unique fingerprint string
    """
    from .decorators import get_client_ip

    # Combine multiple request attributes for fingerprinting
    components = [
        get_client_ip(request),
        request.META.get("HTTP_USER_AGENT", ""),
        request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
        request.META.get("HTTP_ACCEPT_ENCODING", ""),
    ]

    fingerprint_string = "|".join(components)
    return hashlib.md5(fingerprint_string.encode()).hexdigest()


def parse_rate_string(rate_string: str) -> tuple:
    """
    Parse rate string into limit and window.

    Args:
        rate_string: Rate in format "limit/period" (e.g., "100/hour", "10/minute")

    Returns:
        Tuple of (limit, window_seconds)
    """
    try:
        limit_str, period_str = rate_string.split("/")
        limit = int(limit_str)

        period_multipliers = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
            "week": 604800,
            "month": 2592000,  # 30 days
        }

        if period_str not in period_multipliers:
            raise ValueError(f"Invalid period: {period_str}")

        window = period_multipliers[period_str]
        return limit, window

    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Invalid rate format: {rate_string}. Use 'limit/period' format."
        ) from e


def cleanup_expired_entries():
    """
    Utility function to clean up expired entries from database backend.
    """
    try:
        from .models import RateLimitEntry

        deleted_count, _ = RateLimitEntry.cleanup_expired()
        return deleted_count
    except ImportError:
        # Database backend not available
        return 0


def get_rate_limit_config() -> Dict[str, Any]:
    """
    Get rate limiting configuration from Django settings.

    Returns:
        Rate limiting configuration dictionary
    """
    return getattr(settings, "RATE_LIMIT_SETTINGS", {})


def validate_rate_limit_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate rate limiting configuration.

    Args:
        config: Configuration dictionary to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check backend
    backend = config.get("BACKEND", "memory")
    if backend not in ["memory", "database", "redis"]:
        errors.append(f"Invalid backend: {backend}")

    # Check rules
    rules = config.get("RULES", [])
    for i, rule in enumerate(rules):
        if "path_pattern" not in rule:
            errors.append(f"Rule {i}: missing 'path_pattern'")
        if "limit" not in rule:
            errors.append(f"Rule {i}: missing 'limit'")
        if "window" not in rule:
            errors.append(f"Rule {i}: missing 'window'")

        # Validate algorithm
        algorithm = rule.get("algorithm", "sliding_window")
        if algorithm not in [
            "sliding_window",
            "token_bucket",
            "fixed_window",
            "sliding_counter",
        ]:
            errors.append(f"Rule {i}: invalid algorithm '{algorithm}'")

    return errors
