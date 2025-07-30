"""
Tests for Django Rate Limiter backends.
"""

import threading
import time
from unittest import TestCase

from django_rate_limiter.backends import MemoryBackend, get_backend
from django_rate_limiter.exceptions import BackendError


class TestMemoryBackend(TestCase):
    """Test in-memory storage backend."""

    def setUp(self):
        self.backend = MemoryBackend()

    def test_basic_operations(self):
        """Test basic get/set operations."""
        key = "test_key"
        value = {"count": 5, "timestamp": time.time()}
        ttl = 60

        # Initially should return None
        self.assertIsNone(self.backend.get(key))

        # Set value
        self.backend.set(key, value, ttl)

        # Get value
        retrieved = self.backend.get(key)
        self.assertEqual(retrieved, value)

        # Delete value
        self.backend.delete(key)
        self.assertIsNone(self.backend.get(key))

    def test_expiration(self):
        """Test TTL expiration."""
        key = "test_key"
        value = {"count": 1}
        ttl = 1  # 1 second

        self.backend.set(key, value, ttl)

        # Should be available immediately
        self.assertIsNotNone(self.backend.get(key))

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        self.assertIsNone(self.backend.get(key))

    def test_increment(self):
        """Test atomic increment operation."""
        key = "counter"
        ttl = 60

        # First increment
        count = self.backend.increment(key, 1, ttl)
        self.assertEqual(count, 1)

        # Second increment
        count = self.backend.increment(key, 1, ttl)
        self.assertEqual(count, 2)

        # Increment by 5
        count = self.backend.increment(key, 5, ttl)
        self.assertEqual(count, 7)

    def test_atomic_update(self):
        """Test atomic update operation."""
        key = "test_key"
        ttl = 60

        def updater(current_data):
            if current_data is None:
                return {"count": 1, "requests": [time.time()]}
            current_data["count"] += 1
            current_data["requests"].append(time.time())
            return current_data

        # First update
        result = self.backend.atomic_update(key, updater, ttl)
        self.assertEqual(result["count"], 1)
        self.assertEqual(len(result["requests"]), 1)

        # Second update
        result = self.backend.atomic_update(key, updater, ttl)
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["requests"]), 2)

    def test_thread_safety(self):
        """Test thread safety of memory backend."""
        key = "counter"
        ttl = 60
        num_threads = 10
        increments_per_thread = 10
        results = []

        def increment_counter():
            for _ in range(increments_per_thread):
                count = self.backend.increment(key, 1, ttl)
                results.append(count)

        # Start multiple threads
        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=increment_counter)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Final count should be total increments
        expected_total = num_threads * increments_per_thread
        final_data = self.backend.get(key)
        self.assertEqual(final_data["count"], expected_total)

        # All results should be unique (no race conditions)
        self.assertEqual(len(set(results)), len(results))

    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        # Add some entries with different TTLs
        self.backend.set("key1", {"data": "value1"}, 1)  # Expires in 1 second
        self.backend.set("key2", {"data": "value2"}, 60)  # Expires in 1 minute

        # Both should be available
        self.assertIsNotNone(self.backend.get("key1"))
        self.assertIsNotNone(self.backend.get("key2"))

        # Wait for first to expire
        time.sleep(1.1)

        # Trigger cleanup by accessing
        self.assertIsNone(self.backend.get("key1"))  # Should trigger cleanup
        self.assertIsNotNone(self.backend.get("key2"))  # Should still exist


class TestBackendFactory(TestCase):
    """Test backend factory function."""

    def test_get_memory_backend(self):
        """Test getting memory backend."""
        backend = get_backend("memory")
        self.assertIsInstance(backend, MemoryBackend)

        # Should return same instance (singleton)
        backend2 = get_backend("memory")
        self.assertIs(backend, backend2)

    def test_invalid_backend(self):
        """Test invalid backend type."""
        with self.assertRaises(BackendError):
            get_backend("invalid_backend")


# Note: DatabaseBackend and RedisBackend tests would require additional setup
# and dependencies, so they're omitted for simplicity in this basic test suite
