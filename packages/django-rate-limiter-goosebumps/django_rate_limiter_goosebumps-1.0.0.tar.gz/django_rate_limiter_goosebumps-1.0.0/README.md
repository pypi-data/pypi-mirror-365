# Django Rate Limiter

A comprehensive Django rate limiter with multiple algorithms and storage backends, designed for high-performance applications with thread safety and deadlock prevention.

## 🚀 Features

- **Multiple Rate Limiting Algorithms**: Sliding window, token bucket, fixed window, sliding window counter
- **Thread-Safe & Deadlock-Safe**: Proper locking mechanisms prevent race conditions
- **Multiple Storage Backends**: In-memory, database, Redis - choose what fits your needs
- **Django Integration**: Decorators, middleware, management commands
- **High Performance**: Optimized for high-throughput scenarios
- **Flexible Configuration**: Per-endpoint, per-user, per-IP, or custom key functions

## 📦 Installation

```bash
pip install django-rate-limiter
```

For Redis support:
```bash
pip install redis
```

## ⚡ Quick Start

### 1. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ... your other apps
    'django_rate_limiter',
]
```

### 2. Choose Your Storage Backend

#### Memory Backend (Development)
```python
RATE_LIMIT_SETTINGS = {
    'BACKEND': 'memory',  # Fast, simple, not persistent
    'GLOBAL_LIMIT': 1000,
    'GLOBAL_WINDOW': 3600,
}
```

#### Database Backend (Single Server)
```python
RATE_LIMIT_SETTINGS = {
    'BACKEND': 'database',  # Persistent, works across restarts
    'GLOBAL_LIMIT': 1000,
    'GLOBAL_WINDOW': 3600,
}
```

Run migrations for database backend:
```bash
python manage.py migrate django_rate_limiter
```

#### Redis Backend (Distributed/High Performance)
```python
RATE_LIMIT_SETTINGS = {
    'BACKEND': 'redis',  # Fast, distributed, scalable
    'BACKEND_KWARGS': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
    },
    'GLOBAL_LIMIT': 1000,
    'GLOBAL_WINDOW': 3600,
}
```

### 3. Use Decorators

```python
from django_rate_limiter.decorators import rate_limit, throttle

@rate_limit(limit=100, window=3600)  # 100 requests per hour
def my_api_view(request):
    return JsonResponse({"message": "Hello world"})

@throttle("10/minute")  # 10 requests per minute
def strict_endpoint(request):
    return JsonResponse({"data": "limited access"})
```

## 🔧 Backend Configuration Guide

### When to Use Each Backend

| Backend   | Best For | Persistence | Multi-Process | Performance | Setup |
|-----------|----------|-------------|---------------|-------------|-------|
| **Memory** | Development, testing | ❌ | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Database** | Single server production | ✅ | ✅ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Redis** | Distributed systems | ✅ | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### Detailed Backend Configuration

#### Memory Backend
```python
# settings.py
RATE_LIMIT_SETTINGS = {
    'BACKEND': 'memory',
    'DEFAULT_ALGORITHM': 'sliding_window',
    'GLOBAL_LIMIT': 1000,
    'GLOBAL_WINDOW': 3600,
}
```

**Pros**: Fastest performance, no external dependencies  
**Cons**: Data lost on restart, single process only

#### Database Backend
```python
# settings.py
RATE_LIMIT_SETTINGS = {
    'BACKEND': 'database',
    'DEFAULT_ALGORITHM': 'sliding_window', 
    'GLOBAL_LIMIT': 1000,
    'GLOBAL_WINDOW': 3600,
}
```

Setup required:
```bash
python manage.py migrate django_rate_limiter
python manage.py cleanup_rate_limits  # Optional cleanup command
```

**Pros**: Persistent across restarts, works with existing Django database  
**Cons**: Slower than memory/Redis, database overhead

#### Redis Backend
```python
# settings.py
RATE_LIMIT_SETTINGS = {
    'BACKEND': 'redis',
    'BACKEND_KWARGS': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None,  # Set if Redis requires auth
    },
    'DEFAULT_ALGORITHM': 'sliding_window',
    'GLOBAL_LIMIT': 1000,
    'GLOBAL_WINDOW': 3600,
}
```

**Pros**: Very fast, distributed, highly scalable  
**Cons**: Requires Redis server setup

## 📚 Usage Examples

### Decorator Usage

```python
from django_rate_limiter.decorators import rate_limit, throttle, per_user_rate_limit

# Basic rate limiting
@rate_limit(limit=100, window=3600)  # 100 requests per hour
def api_endpoint(request):
    return JsonResponse({"data": "response"})

# Using different backends
@rate_limit(limit=50, window=300, backend="database")
def persistent_endpoint(request):
    return JsonResponse({"message": "Stored in database"})

@rate_limit(limit=1000, window=3600, backend="redis")
def high_traffic_endpoint(request):
    return JsonResponse({"message": "Fast Redis storage"})

# Different algorithms
@rate_limit(limit=10, window=60, algorithm="token_bucket")
def burst_allowed_endpoint(request):
    return JsonResponse({"message": "Allows burst traffic"})

# Simple throttling
@throttle("10/minute")
def simple_throttled_view(request):
    return JsonResponse({"message": "10 per minute max"})

# Per-user rate limiting
@per_user_rate_limit(limit=1000, window=3600)
def user_api(request):
    return JsonResponse({"user": str(request.user)})
```

```python
MIDDLEWARE = [
    # ... other middleware
    'django_rate_limiter.middleware.RateLimitMiddleware',
]

RATE_LIMIT_SETTINGS = {
    'BACKEND': 'memory',  # 'memory', 'database', 'redis'
    'DEFAULT_ALGORITHM': 'sliding_window',
    'RULES': [
        {
            'path_pattern': r'^/api/',
            'limit': 1000,
            'window': 3600,
            'algorithm': 'sliding_window',
            'scope': 'api',
        },
        {
            'path_pattern': r'^/login/$',
            'limit': 5,
            'window': 300,
            'algorithm': 'fixed_window',
            'use_user': False,  # Use IP instead of user
        },
    ],
    'GLOBAL_LIMIT': 10000,
    'GLOBAL_WINDOW': 3600,
    'EXEMPT_PATHS': [r'^/health/$', r'^/static/'],
    'EXEMPT_IPS': ['127.0.0.1', '::1'],
    'USE_USER_ID': True,
    'RATE_LIMIT_HEADERS': True,
}
```

### Programmatic Usage

```python
from django_rate_limiter import check_rate_limit, RateLimitExceeded

try:
    metadata = check_rate_limit(
        identifier="user:123",
        limit=100,
        window=3600,
        algorithm="token_bucket",
        backend="redis"
    )
    print(f"Remaining requests: {metadata['remaining']}")
except RateLimitExceeded as e:
    print(f"Rate limit exceeded! Retry after: {e.retry_after} seconds")
```

## Rate Limiting Algorithms

### 1. Sliding Window

Maintains exact request timestamps for precise rate limiting:

```python
@rate_limit(limit=100, window=3600, algorithm="sliding_window")
def precise_api_view(request):
    return JsonResponse({"data": "response"})
```

**Pros:** Precise, no burst at window boundaries  
**Cons:** Higher memory usage

### 2. Token Bucket

Allows controlled bursts while maintaining steady rate:

```python
@rate_limit(
    limit=60,  # 60 tokens per hour
    window=3600,
    algorithm="token_bucket",
    burst_capacity=100  # Can burst up to 100 requests
)
def bursty_api_view(request):
    return JsonResponse({"data": "response"})
```

**Pros:** Allows bursts, smooth rate limiting  
**Cons:** More complex logic

### 3. Fixed Window

Simple counter reset at fixed intervals:

```python
@rate_limit(limit=1000, window=3600, algorithm="fixed_window")
def simple_api_view(request):
    return JsonResponse({"data": "response"})
```

**Pros:** Simple, memory efficient  
**Cons:** Potential bursts at window boundaries

### 4. Sliding Window Counter

Approximates sliding window using multiple counters:

```python
@rate_limit(
    limit=1000, 
    window=3600, 
    algorithm="sliding_counter",
    num_windows=12  # 12 5-minute windows
)
def balanced_api_view(request):
    return JsonResponse({"data": "response"})
```

**Pros:** Good balance of accuracy and efficiency  
**Cons:** Approximation, not exact

## Storage Backends

### Memory Backend

Fast, single-server storage:

```python
@rate_limit(limit=100, window=3600, backend="memory")
def memory_limited_view(request):
    return JsonResponse({"data": "response"})
```

### Database Backend

Persistent storage using Django ORM:

```python
@rate_limit(limit=100, window=3600, backend="database")
def db_limited_view(request):
    return JsonResponse({"data": "response"})
```

### Redis Backend

Distributed, high-performance storage:

```python
@rate_limit(
    limit=100, 
    window=3600, 
    backend="redis",
    backend_kwargs={
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': 'your-password'
    }
)
def redis_limited_view(request):
    return JsonResponse({"data": "response"})
```

## Advanced Usage

### Custom Rate Limiting Keys

```python
def api_key_extractor(request):
    return request.META.get('HTTP_X_API_KEY', 'anonymous')

@custom_key_rate_limit(api_key_extractor, limit=1000, window=3600)
def api_key_limited_view(request):
    return JsonResponse({"data": "response"})
```

### Rate Limiting Decorators

```python
# Per user rate limiting
@per_user_rate_limit(limit=1000, window=3600)
def user_limited_view(request):
    return JsonResponse({"data": "response"})

# Per IP rate limiting
@per_ip_rate_limit(limit=100, window=3600)
def ip_limited_view(request):
    return JsonResponse({"data": "response"})

# Simple throttling with rate strings
@throttle("100/hour", algorithm="token_bucket")
def throttled_view(request):
    return JsonResponse({"data": "response"})
```

### Class-Based Views

```python
from django.views import View
from django_rate_limiter import rate_limit_class

@rate_limit_class(limit=100, window=3600, methods=['GET', 'POST'])
class MyAPIView(View):
    def get(self, request):
        return JsonResponse({"method": "GET"})
    
    def post(self, request):
        return JsonResponse({"method": "POST"})
```

## Management Commands

Clean up expired rate limit entries:

```bash
# Dry run (show what would be deleted)
python manage.py cleanup_rate_limits --dry-run

# Actually delete expired entries
python manage.py cleanup_rate_limits
```

## Configuration

### Complete Settings Example

```python
RATE_LIMIT_SETTINGS = {
    # Backend configuration
    'BACKEND': 'redis',  # 'memory', 'database', 'redis'
    'BACKEND_KWARGS': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
    },
    
    # Default algorithm
    'DEFAULT_ALGORITHM': 'sliding_window',
    
    # Path-specific rules
    'RULES': [
        {
            'path_pattern': r'^/api/v1/',
            'limit': 1000,
            'window': 3600,
            'algorithm': 'sliding_window',
            'scope': 'api_v1',
        },
        {
            'path_pattern': r'^/api/v2/',
            'limit': 2000,
            'window': 3600,
            'algorithm': 'token_bucket',
            'scope': 'api_v2',
            'burst_capacity': 100,
        },
        {
            'path_pattern': r'^/auth/',
            'limit': 10,
            'window': 300,
            'algorithm': 'fixed_window',
            'use_user': False,  # Use IP for auth endpoints
        },
    ],
    
    # Global limits
    'GLOBAL_LIMIT': 10000,
    'GLOBAL_WINDOW': 3600,
    
    # Exemptions
    'EXEMPT_PATHS': [
        r'^/health/$',
        r'^/static/',
        r'^/media/',
    ],
    'EXEMPT_IPS': ['127.0.0.1', '::1'],
    
    # Behavior settings
    'USE_USER_ID': True,  # Use authenticated user ID when available
    'RATE_LIMIT_HEADERS': True,  # Add X-RateLimit-* headers
}
```

## Thread Safety & Performance

This package is designed with thread safety and performance in mind:

- **Memory Backend:** Uses `threading.RLock()` to prevent deadlocks
- **Database Backend:** Uses `select_for_update()` for atomic operations
- **Redis Backend:** Uses Redis transactions and watches for atomic updates
- **Algorithms:** All algorithms use atomic operations to prevent race conditions

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=django_rate_limiter --cov-report=html
```

## Development Tools 🛠️

This project includes comprehensive development tools to ensure code quality:

```bash
# Quick setup
./setup-dev.sh

# Run all quality checks
./check-code.sh           # Shell script
python check_quality.py   # Python script  
make check                # Makefile

# Pre-commit hooks (automatic)
pre-commit install
```

For detailed information about development tools, see [DEV_TOOLS.md](DEV_TOOLS.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0

- Initial release
- Multiple rate limiting algorithms (sliding window, token bucket, fixed window, sliding counter)
- Multiple storage backends (memory, database, Redis)
- Thread-safe and deadlock-safe implementation
- Django decorators and middleware
- Management commands
- Comprehensive test suite
