"""
Rate limiting algorithms implementation.

Provides thread-safe, deadlock-safe implementations of various
rate limiting algorithms including sliding window, token bucket,
and fixed window approaches.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from .backends import BaseBackend, get_backend
from .exceptions import RateLimitExceeded


class BaseRateLimiter(ABC):
    """Abstract base class for rate limiters."""

    def __init__(
        self, backend: Optional[BaseBackend] = None, key_prefix: str = "rate_limit"
    ):
        self.backend = backend or get_backend("memory")
        self.key_prefix = key_prefix

    def _get_key(self, identifier: str, scope: str = "") -> str:
        """Generate a cache key for rate limiting."""
        parts = [self.key_prefix, self.__class__.__name__.lower()]
        if scope:
            parts.append(scope)
        parts.append(identifier)
        return ":".join(parts)

    @abstractmethod
    def is_allowed(
        self, identifier: str, limit: int, window: int, scope: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is allowed.

        Args:
            identifier: Unique identifier for the client
            limit: Maximum number of requests allowed
            window: Time window in seconds
            scope: Optional scope for grouping (e.g., endpoint name)

        Returns:
            Tuple of (is_allowed, metadata)
        """
        pass

    def enforce(
        self, identifier: str, limit: int, window: int, scope: str = ""
    ) -> Dict[str, Any]:
        """
        Enforce rate limiting, raising exception if limit exceeded.

        Args:
            identifier: Unique identifier for the client
            limit: Maximum number of requests allowed
            window: Time window in seconds
            scope: Optional scope for grouping

        Returns:
            Metadata about the rate limiting

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        allowed, metadata = self.is_allowed(identifier, limit, window, scope)
        if not allowed:
            raise RateLimitExceeded(
                f"Rate limit exceeded for {identifier}",
                retry_after=metadata.get("retry_after"),
                limit=limit,
                window=window,
            )
        return metadata


class SlidingWindowRateLimiter(BaseRateLimiter):
    """
    Sliding window rate limiter using a log of timestamps.

    Maintains a precise sliding window by storing individual request timestamps.
    More memory intensive but provides exact rate limiting.
    """

    def is_allowed(
        self, identifier: str, limit: int, window: int, scope: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed using sliding window algorithm."""
        key = self._get_key(identifier, scope)
        current_time = time.time()
        window_start = current_time - window

        def update_window(current_data):
            if current_data is None:
                current_data = {"requests": []}

            # Remove requests outside the window
            requests = [
                req_time
                for req_time in current_data.get("requests", [])
                if req_time > window_start
            ]

            # Check if we can add a new request
            if len(requests) < limit:
                requests.append(current_time)
                allowed = True
            else:
                allowed = False

            return {
                "requests": requests,
                "allowed": allowed,
                "count": len(requests),
                "oldest_request": min(requests) if requests else None,
            }

        result = self.backend.atomic_update(key, update_window, window + 10)

        if result and result.get("allowed", False):
            return True, {
                "remaining": limit - result["count"],
                "reset_time": current_time + window,
                "current_count": result["count"],
            }
        else:
            # Calculate retry after
            oldest_request = result.get("oldest_request") if result else None
            retry_after = (
                max(0, int((oldest_request + window) - current_time))
                if oldest_request
                else window
            )

            return False, {
                "remaining": 0,
                "reset_time": current_time + retry_after,
                "current_count": result.get("count", limit) if result else limit,
                "retry_after": retry_after,
            }


class TokenBucketRateLimiter(BaseRateLimiter):
    """
    Token bucket rate limiter.

    Allows burst requests up to the bucket capacity while maintaining
    a steady rate of token replenishment.
    """

    def is_allowed(
        self,
        identifier: str,
        limit: int,
        window: int,
        scope: str = "",
        tokens_per_request: int = 1,
        burst_capacity: Optional[int] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed using token bucket algorithm.

        Args:
            identifier: Unique identifier for the client
            limit: Number of tokens to replenish per window
            window: Time window for replenishment in seconds
            scope: Optional scope for grouping
            tokens_per_request: Number of tokens required per request
            burst_capacity: Maximum bucket capacity (defaults to limit)
        """
        if burst_capacity is None:
            burst_capacity = limit

        key = self._get_key(identifier, scope)
        current_time = time.time()
        tokens_per_second = limit / window

        def update_bucket(current_data):
            if current_data is None:
                current_data = {"tokens": burst_capacity, "last_refill": current_time}

            # Calculate tokens to add based on elapsed time
            time_elapsed = current_time - current_data.get("last_refill", current_time)
            tokens_to_add = time_elapsed * tokens_per_second

            # Update token count (capped at burst capacity)
            current_tokens = min(
                burst_capacity, current_data.get("tokens", 0) + tokens_to_add
            )

            # Check if we have enough tokens
            if current_tokens >= tokens_per_request:
                current_tokens -= tokens_per_request
                allowed = True
            else:
                allowed = False

            return {
                "tokens": current_tokens,
                "last_refill": current_time,
                "allowed": allowed,
            }

        result = self.backend.atomic_update(key, update_bucket, window * 2)

        if result and result.get("allowed", False):
            return True, {
                "remaining_tokens": int(result["tokens"]),
                "burst_capacity": burst_capacity,
                "refill_rate": tokens_per_second,
            }
        else:
            # Calculate retry after (time to get enough tokens)
            current_tokens = result.get("tokens", 0) if result else 0
            tokens_needed = tokens_per_request - current_tokens
            retry_after = max(1, int(tokens_needed / tokens_per_second))

            return False, {
                "remaining_tokens": int(current_tokens),
                "burst_capacity": burst_capacity,
                "refill_rate": tokens_per_second,
                "retry_after": retry_after,
            }


class FixedWindowRateLimiter(BaseRateLimiter):
    """
    Fixed window rate limiter.

    Divides time into fixed windows and counts requests within each window.
    Simple and memory efficient but can allow bursts at window boundaries.
    """

    def is_allowed(
        self, identifier: str, limit: int, window: int, scope: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed using fixed window algorithm."""
        key = self._get_key(identifier, scope)
        current_time = time.time()

        # Calculate current window
        window_start = int(current_time // window) * window
        window_key = f"{key}:{window_start}"

        def update_counter(current_data):
            if current_data is None:
                current_data = {"count": 0, "window_start": window_start}

            # Check if we're in the same window
            if current_data.get("window_start") != window_start:
                # New window, reset counter
                current_data = {"count": 0, "window_start": window_start}

            current_count = current_data.get("count", 0)

            if current_count < limit:
                current_data["count"] = current_count + 1
                allowed = True
            else:
                allowed = False

            current_data["allowed"] = allowed
            return current_data

        result = self.backend.atomic_update(window_key, update_counter, window + 10)

        if result and result.get("allowed", False):
            current_count = result.get("count", 1)
            return True, {
                "remaining": limit - current_count,
                "reset_time": window_start + window,
                "current_count": current_count,
                "window_start": window_start,
            }
        else:
            reset_time = window_start + window
            retry_after = max(1, int(reset_time - current_time))

            return False, {
                "remaining": 0,
                "reset_time": reset_time,
                "current_count": result.get("count", limit) if result else limit,
                "retry_after": retry_after,
                "window_start": window_start,
            }


class SlidingWindowCounterRateLimiter(BaseRateLimiter):
    """
    Sliding window counter rate limiter.

    Approximates sliding window using multiple fixed windows.
    More memory efficient than full sliding window while providing
    better accuracy than fixed window.
    """

    def __init__(
        self,
        backend: Optional[BaseBackend] = None,
        key_prefix: str = "rate_limit",
        num_windows: int = 10,
    ):
        super().__init__(backend, key_prefix)
        self.num_windows = num_windows

    def is_allowed(
        self, identifier: str, limit: int, window: int, scope: str = ""
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed using sliding window counter algorithm."""
        key = self._get_key(identifier, scope)
        current_time = time.time()

        # Divide the window into smaller sub-windows
        sub_window_size = window / self.num_windows
        current_sub_window = int(current_time // sub_window_size)

        def update_counters(current_data):
            if current_data is None:
                current_data = {"windows": {}, "last_cleanup": current_time}

            windows = current_data.get("windows", {})

            # Cleanup old windows
            cutoff_window = current_sub_window - self.num_windows
            windows = {k: v for k, v in windows.items() if int(k) > cutoff_window}

            # Calculate current total count
            total_count = sum(windows.values())

            # Check if we can add a new request
            if total_count < limit:
                # Add to current sub-window
                windows[str(current_sub_window)] = (
                    windows.get(str(current_sub_window), 0) + 1
                )
                allowed = True
                total_count += 1
            else:
                allowed = False

            return {
                "windows": windows,
                "last_cleanup": current_time,
                "allowed": allowed,
                "total_count": total_count,
            }

        result = self.backend.atomic_update(key, update_counters, window + 10)

        if result and result.get("allowed", False):
            total_count = result.get("total_count", 1)
            return True, {
                "remaining": limit - total_count,
                "reset_time": current_time + window,
                "current_count": total_count,
            }
        else:
            # Calculate approximate retry time
            retry_after = max(1, int(sub_window_size))

            return False, {
                "remaining": 0,
                "reset_time": current_time + retry_after,
                "current_count": result.get("total_count", limit) if result else limit,
                "retry_after": retry_after,
            }


# Factory function to get rate limiter instances
def get_rate_limiter(algorithm: str = "sliding_window", **kwargs) -> BaseRateLimiter:
    """
    Factory function to create rate limiter instances.

    Args:
        algorithm: Type of algorithm ("sliding_window", "token_bucket",
            "fixed_window", "sliding_counter")
        **kwargs: Additional arguments passed to the rate limiter constructor

    Returns:
        Rate limiter instance
    """
    algorithms = {
        "sliding_window": SlidingWindowRateLimiter,
        "token_bucket": TokenBucketRateLimiter,
        "fixed_window": FixedWindowRateLimiter,
        "sliding_counter": SlidingWindowCounterRateLimiter,
    }

    if algorithm not in algorithms:
        raise ValueError(
            f"Unknown algorithm: {algorithm}. Available: {list(algorithms.keys())}"
        )

    return algorithms[algorithm](**kwargs)
