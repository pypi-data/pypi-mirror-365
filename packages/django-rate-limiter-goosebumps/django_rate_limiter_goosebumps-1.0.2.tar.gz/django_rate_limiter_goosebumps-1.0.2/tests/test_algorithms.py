"""
Tests for Django Rate Limiter algorithms.
"""

import threading
import time
from unittest import TestCase

from django_rate_limiter.algorithms import (
    FixedWindowRateLimiter,
    SlidingWindowCounterRateLimiter,
    SlidingWindowRateLimiter,
    TokenBucketRateLimiter,
    get_rate_limiter,
)
from django_rate_limiter.backends import MemoryBackend
from django_rate_limiter.exceptions import RateLimitExceeded


class TestSlidingWindowRateLimiter(TestCase):
    """Test sliding window rate limiter."""

    def setUp(self):
        self.backend = MemoryBackend()
        self.limiter = SlidingWindowRateLimiter(backend=self.backend)

    def test_basic_rate_limiting(self):
        """Test basic rate limiting functionality."""
        identifier = "test_user"
        limit = 5
        window = 60

        # Should allow first 5 requests
        for i in range(5):
            allowed, metadata = self.limiter.is_allowed(identifier, limit, window)
            self.assertTrue(allowed)
            self.assertEqual(metadata["remaining"], limit - i - 1)

        # 6th request should be denied
        allowed, metadata = self.limiter.is_allowed(identifier, limit, window)
        self.assertFalse(allowed)
        self.assertEqual(metadata["remaining"], 0)

    def test_window_sliding(self):
        """Test that window slides correctly."""
        identifier = "test_user"
        limit = 2
        window = 1  # 1 second window

        # Make 2 requests
        for _ in range(2):
            allowed, _ = self.limiter.is_allowed(identifier, limit, window)
            self.assertTrue(allowed)

        # 3rd request should be denied
        allowed, _ = self.limiter.is_allowed(identifier, limit, window)
        self.assertFalse(allowed)

        # Wait for window to slide
        time.sleep(1.1)

        # Should allow requests again
        allowed, _ = self.limiter.is_allowed(identifier, limit, window)
        self.assertTrue(allowed)

    def test_thread_safety(self):
        """Test thread safety of rate limiter."""
        identifier = "test_user"
        limit = 10
        window = 60
        results = []

        def make_requests():
            for _ in range(5):
                try:
                    self.limiter.enforce(identifier, limit, window)
                    results.append(True)
                except RateLimitExceeded:
                    results.append(False)

        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should have exactly 10 successful requests
        successful = sum(results)
        self.assertEqual(successful, 10)


class TestTokenBucketRateLimiter(TestCase):
    """Test token bucket rate limiter."""

    def setUp(self):
        self.backend = MemoryBackend()
        self.limiter = TokenBucketRateLimiter(backend=self.backend)

    def test_burst_capacity(self):
        """Test burst capacity functionality."""
        identifier = "test_user"
        limit = 10  # 10 tokens per window
        window = 60  # 60 seconds
        burst_capacity = 20  # Can burst up to 20

        # Should allow burst up to capacity
        for i in range(burst_capacity):
            allowed, metadata = self.limiter.is_allowed(
                identifier, limit, window, burst_capacity=burst_capacity
            )
            self.assertTrue(allowed)

        # Next request should be denied
        allowed, _ = self.limiter.is_allowed(
            identifier, limit, window, burst_capacity=burst_capacity
        )
        self.assertFalse(allowed)

    def test_token_replenishment(self):
        """Test token replenishment over time."""
        identifier = "test_user"
        limit = 60  # 60 tokens per window
        window = 60  # 60 seconds (1 token per second)
        burst_capacity = 10

        # Use all tokens
        for _ in range(burst_capacity):
            allowed, _ = self.limiter.is_allowed(
                identifier, limit, window, burst_capacity=burst_capacity
            )
            self.assertTrue(allowed)

        # Should be denied
        allowed, _ = self.limiter.is_allowed(
            identifier, limit, window, burst_capacity=burst_capacity
        )
        self.assertFalse(allowed)

        # Wait for token replenishment
        time.sleep(2)

        # Should allow requests again (2 tokens replenished)
        for _ in range(2):
            allowed, _ = self.limiter.is_allowed(
                identifier, limit, window, burst_capacity=burst_capacity
            )
            self.assertTrue(allowed)


class TestFixedWindowRateLimiter(TestCase):
    """Test fixed window rate limiter."""

    def setUp(self):
        self.backend = MemoryBackend()
        self.limiter = FixedWindowRateLimiter(backend=self.backend)

    def test_fixed_window_behavior(self):
        """Test fixed window rate limiting."""
        identifier = "test_user"
        limit = 5
        window = 2  # 2 seconds

        # Should allow 5 requests in window
        for i in range(5):
            allowed, metadata = self.limiter.is_allowed(identifier, limit, window)
            self.assertTrue(allowed)
            self.assertEqual(metadata["remaining"], limit - i - 1)

        # 6th request should be denied
        allowed, _ = self.limiter.is_allowed(identifier, limit, window)
        self.assertFalse(allowed)

        # Wait for next window
        time.sleep(2.1)

        # Should allow requests in new window
        allowed, metadata = self.limiter.is_allowed(identifier, limit, window)
        self.assertTrue(allowed)
        self.assertEqual(metadata["remaining"], limit - 1)


class TestSlidingWindowCounterRateLimiter(TestCase):
    """Test sliding window counter rate limiter."""

    def setUp(self):
        self.backend = MemoryBackend()
        self.limiter = SlidingWindowCounterRateLimiter(
            backend=self.backend, num_windows=5
        )

    def test_sliding_counter_behavior(self):
        """Test sliding window counter rate limiting."""
        identifier = "test_user"
        limit = 10
        window = 5  # 5 seconds with 5 sub-windows (1 second each)

        # Should allow requests up to limit
        for i in range(limit):
            allowed, metadata = self.limiter.is_allowed(identifier, limit, window)
            self.assertTrue(allowed)

        # Next request should be denied
        allowed, _ = self.limiter.is_allowed(identifier, limit, window)
        self.assertFalse(allowed)


class TestRateLimiterFactory(TestCase):
    """Test rate limiter factory function."""

    def test_get_rate_limiter(self):
        """Test factory function creates correct instances."""
        backend = MemoryBackend()

        # Test different algorithms
        sliding = get_rate_limiter("sliding_window", backend=backend)
        self.assertIsInstance(sliding, SlidingWindowRateLimiter)

        token = get_rate_limiter("token_bucket", backend=backend)
        self.assertIsInstance(token, TokenBucketRateLimiter)

        fixed = get_rate_limiter("fixed_window", backend=backend)
        self.assertIsInstance(fixed, FixedWindowRateLimiter)

        sliding_counter = get_rate_limiter("sliding_counter", backend=backend)
        self.assertIsInstance(sliding_counter, SlidingWindowCounterRateLimiter)

        # Test invalid algorithm
        with self.assertRaises(ValueError):
            get_rate_limiter("invalid_algorithm", backend=backend)
