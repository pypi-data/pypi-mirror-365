"""
Storage backends for Django Rate Limiter.

Provides thread-safe, deadlock-safe storage implementations for
in-memory, database, and Redis backends.
"""

import json
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from django.db import transaction
from django.utils import timezone

from .exceptions import BackendError

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class BaseBackend(ABC):
    """Abstract base class for rate limiting storage backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data for a key."""
        pass

    @abstractmethod
    def set(self, key: str, value: Dict[str, Any], ttl: int) -> None:
        """Set data for a key with TTL."""
        pass

    @abstractmethod
    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Atomically increment a counter."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key."""
        pass

    @abstractmethod
    def atomic_update(self, key: str, updater_func, ttl: Optional[int] = None) -> Any:
        """Perform atomic update on a key's value."""
        pass


class MemoryBackend(BaseBackend):
    """Thread-safe in-memory storage backend."""

    def __init__(self):
        self._data: Dict[str, Tuple[Dict[str, Any], Optional[float]]] = {}
        self._lock = threading.RLock()  # Use RLock to prevent deadlocks

    def _cleanup_expired(self):
        """Remove expired entries."""
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, expiry) in self._data.items()
            if expiry and current_time > expiry
        ]
        for key in expired_keys:
            self._data.pop(key, None)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data for a key."""
        with self._lock:
            self._cleanup_expired()
            if key in self._data:
                value, expiry = self._data[key]
                if not expiry or time.time() <= expiry:
                    return value.copy()
            return None

    def set(self, key: str, value: Dict[str, Any], ttl: int) -> None:
        """Set data for a key with TTL."""
        with self._lock:
            expiry = time.time() + ttl if ttl else None
            self._data[key] = (value.copy(), expiry)

    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Atomically increment a counter."""
        with self._lock:
            current_data = self.get(key) or {"count": 0}
            new_count = current_data.get("count", 0) + amount
            current_data["count"] = new_count
            if ttl:
                self.set(key, current_data, ttl)
            else:
                # Keep existing TTL
                expiry = None
                if key in self._data:
                    _, expiry = self._data[key]
                    if expiry:
                        ttl = max(0, int(expiry - time.time()))
                self.set(key, current_data, ttl or 3600)  # Default 1 hour
            return new_count

    def delete(self, key: str) -> None:
        """Delete a key."""
        with self._lock:
            self._data.pop(key, None)

    def atomic_update(self, key: str, updater_func, ttl: Optional[int] = None) -> Any:
        """Perform atomic update on a key's value."""
        with self._lock:
            current_data = self.get(key)
            new_data = updater_func(current_data)
            if new_data is not None:
                self.set(key, new_data, ttl or 3600)
            return new_data


class DatabaseBackend(BaseBackend):
    """Database storage backend using Django ORM."""

    def __init__(self):
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Ensure the rate limit table exists."""
        # This will be handled by migrations
        # Check if database storage config is set

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data for a key."""
        try:
            from .models import RateLimitEntry

            entry = RateLimitEntry.objects.filter(
                key=key, expires_at__gt=timezone.now()
            ).first()
            if entry:
                return json.loads(entry.data)
            return None
        except Exception as e:
            raise BackendError(f"Database get error: {e}")

    def set(self, key: str, value: Dict[str, Any], ttl: int) -> None:
        """Set data for a key with TTL."""
        try:
            from .models import RateLimitEntry

            expires_at = timezone.now() + timezone.timedelta(seconds=ttl)

            with transaction.atomic():
                RateLimitEntry.objects.update_or_create(
                    key=key,
                    defaults={
                        "data": json.dumps(value),
                        "expires_at": expires_at,
                    },
                )
        except Exception as e:
            raise BackendError(f"Database set error: {e}")

    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Atomically increment a counter."""
        try:
            from .models import RateLimitEntry

            with transaction.atomic():
                # Use SELECT FOR UPDATE to prevent race conditions
                entry = (
                    RateLimitEntry.objects.select_for_update()
                    .filter(key=key, expires_at__gt=timezone.now())
                    .first()
                )

                if entry:
                    data = json.loads(entry.data)
                    new_count = data.get("count", 0) + amount
                    data["count"] = new_count
                    entry.data = json.dumps(data)
                    entry.save()
                else:
                    new_count = amount
                    expires_at = timezone.now() + timezone.timedelta(
                        seconds=ttl or 3600
                    )
                    RateLimitEntry.objects.create(
                        key=key,
                        data=json.dumps({"count": new_count}),
                        expires_at=expires_at,
                    )
                return new_count
        except Exception as e:
            raise BackendError(f"Database increment error: {e}")

    def delete(self, key: str) -> None:
        """Delete a key."""
        try:
            from .models import RateLimitEntry

            RateLimitEntry.objects.filter(key=key).delete()
        except Exception as e:
            raise BackendError(f"Database delete error: {e}")

    def atomic_update(self, key: str, updater_func, ttl: Optional[int] = None) -> Any:
        """Perform atomic update on a key's value."""
        try:
            from .models import RateLimitEntry

            with transaction.atomic():
                entry = (
                    RateLimitEntry.objects.select_for_update()
                    .filter(key=key, expires_at__gt=timezone.now())
                    .first()
                )

                current_data = None
                if entry:
                    current_data = json.loads(entry.data)

                new_data = updater_func(current_data)

                if new_data is not None:
                    expires_at = timezone.now() + timezone.timedelta(
                        seconds=ttl or 3600
                    )
                    if entry:
                        entry.data = json.dumps(new_data)
                        entry.expires_at = expires_at
                        entry.save()
                    else:
                        RateLimitEntry.objects.create(
                            key=key, data=json.dumps(new_data), expires_at=expires_at
                        )
                return new_data
        except Exception as e:
            raise BackendError(f"Database atomic update error: {e}")


class RedisBackend(BaseBackend):
    """Redis storage backend."""

    def __init__(self, redis_client=None, **kwargs):
        if not REDIS_AVAILABLE:
            raise BackendError("Redis is not available. Install redis package.")

        if redis_client:
            self.redis = redis_client
        else:
            # Default Redis connection
            self.redis = redis.Redis(**kwargs)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data for a key."""
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            raise BackendError(f"Redis get error: {e}")

    def set(self, key: str, value: Dict[str, Any], ttl: int) -> None:
        """Set data for a key with TTL."""
        try:
            self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            raise BackendError(f"Redis set error: {e}")

    def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """Atomically increment a counter."""
        try:
            # Use Redis pipeline for atomicity
            pipe = self.redis.pipeline()
            pipe.multi()

            # Check if key exists
            current = self.redis.get(key)
            if current:
                data = json.loads(current)
                new_count = data.get("count", 0) + amount
                data["count"] = new_count
            else:
                new_count = amount
                data = {"count": new_count}

            pipe.setex(key, ttl or 3600, json.dumps(data))
            pipe.execute()

            return new_count
        except Exception as e:
            raise BackendError(f"Redis increment error: {e}")

    def delete(self, key: str) -> None:
        """Delete a key."""
        try:
            self.redis.delete(key)
        except Exception as e:
            raise BackendError(f"Redis delete error: {e}")

    def atomic_update(self, key: str, updater_func, ttl: Optional[int] = None) -> Any:
        """Perform atomic update on a key's value."""
        try:
            with self.redis.pipeline() as pipe:
                while True:
                    try:
                        # Watch the key for changes
                        pipe.watch(key)

                        # Get current value
                        current_data = None
                        data = pipe.get(key)
                        if data:
                            current_data = json.loads(data)

                        # Apply update function
                        new_data = updater_func(current_data)

                        if new_data is not None:
                            # Start transaction
                            pipe.multi()
                            pipe.setex(key, ttl or 3600, json.dumps(new_data))
                            pipe.execute()

                        return new_data
                    except redis.WatchError:
                        # Key was modified, retry
                        continue
        except Exception as e:
            raise BackendError(f"Redis atomic update error: {e}")


# Global backend instances
_memory_backend = None
_database_backend = None
_redis_backend = None


def get_backend(backend_type: str = "memory", **kwargs) -> BaseBackend:
    """Get a backend instance."""
    global _memory_backend, _database_backend, _redis_backend

    if backend_type == "memory":
        if _memory_backend is None:
            _memory_backend = MemoryBackend()
        return _memory_backend
    elif backend_type == "database":
        if _database_backend is None:
            _database_backend = DatabaseBackend()
        return _database_backend
    elif backend_type == "redis":
        if _redis_backend is None:
            _redis_backend = RedisBackend(**kwargs)
        return _redis_backend
    else:
        raise BackendError(f"Unknown backend type: {backend_type}")
