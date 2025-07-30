"""
Decorators for rate limiting Django views and functions.
"""

import functools
from typing import Any, Callable, Dict, Optional

from django.http import HttpRequest, HttpResponse, JsonResponse

from .algorithms import get_rate_limiter
from .backends import get_backend
from .exceptions import RateLimitExceeded


def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "unknown")
    return ip


def get_user_identifier(request: HttpRequest, use_user: bool = True) -> str:
    """Get a unique identifier for the user."""
    if (
        use_user
        and hasattr(request, "user")
        and request.user is not None
        and hasattr(request.user, "is_authenticated")
        and request.user.is_authenticated
    ):
        return f"user:{request.user.pk}"
    else:
        return f"ip:{get_client_ip(request)}"


def rate_limit(
    limit: int,
    window: int,
    algorithm: str = "sliding_window",
    backend: str = "memory",
    scope: Optional[str] = None,
    key_func: Optional[Callable[[HttpRequest], str]] = None,
    error_response: Optional[Callable[[RateLimitExceeded], HttpResponse]] = None,
    use_user: bool = True,
    backend_kwargs: Optional[Dict[str, Any]] = None,
    **limiter_kwargs,
):
    """
    Rate limiting decorator for Django views.

    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        algorithm: Rate limiting algorithm ("sliding_window", "token_bucket",
            "fixed_window", "sliding_counter")
        backend: Storage backend ("memory", "database", "redis")
        scope: Optional scope for grouping (defaults to view name)
        key_func: Optional function to generate custom keys
        error_response: Optional function to generate custom error responses
        use_user: Whether to use authenticated user ID instead of IP
        backend_kwargs: Additional arguments for backend initialization
        **limiter_kwargs: Additional arguments for rate limiter

    Example:
        @rate_limit(limit=100, window=3600, algorithm="sliding_window")
        def my_view(request):
            return JsonResponse({"message": "Hello world"})

        @rate_limit(limit=10, window=60, scope="api", backend="redis")
        def api_endpoint(request):
            return JsonResponse({"data": "some data"})
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            # Get backend instance
            backend_kwargs_final = backend_kwargs or {}
            backend_instance = get_backend(backend, **backend_kwargs_final)

            # Get rate limiter instance
            rate_limiter = get_rate_limiter(
                algorithm=algorithm, backend=backend_instance, **limiter_kwargs
            )

            # Generate identifier
            if key_func:
                identifier = key_func(request)
            else:
                identifier = get_user_identifier(request, use_user)

            # Generate scope
            scope_final = scope or f"{func.__module__}.{func.__name__}"

            try:
                # Check rate limit
                metadata = rate_limiter.enforce(identifier, limit, window, scope_final)

                # Add rate limit headers to response
                response = func(request, *args, **kwargs)

                # Add rate limiting headers
                if hasattr(
                    response, "__setitem__"
                ):  # Check if response supports headers
                    response["X-RateLimit-Limit"] = str(limit)
                    response["X-RateLimit-Remaining"] = str(
                        metadata.get("remaining", 0)
                    )
                    response["X-RateLimit-Reset"] = str(
                        int(metadata.get("reset_time", 0))
                    )

                return response

            except RateLimitExceeded as e:
                if error_response:
                    return error_response(e)
                else:
                    # Default error response
                    response_data = {
                        "error": "Rate limit exceeded",
                        "message": str(e),
                        "limit": limit,
                        "window": window,
                    }

                    if e.retry_after:
                        response_data["retry_after"] = e.retry_after

                    response = JsonResponse(response_data, status=429)
                    response["X-RateLimit-Limit"] = str(limit)
                    response["X-RateLimit-Remaining"] = "0"

                    if e.retry_after:
                        response["Retry-After"] = str(e.retry_after)

                    return response

        return wrapper

    return decorator


def rate_limit_class(
    limit: int, window: int, methods: Optional[list] = None, **decorator_kwargs
):
    """
    Class decorator for rate limiting all methods of a Django class-based view.

    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        methods: List of HTTP methods to rate limit (defaults to all)
        **decorator_kwargs: Additional arguments passed to rate_limit decorator

    Example:
        @rate_limit_class(limit=100, window=3600, methods=['GET', 'POST'])
        class MyAPIView(APIView):
            def get(self, request):
                return Response({"message": "Hello"})
    """
    methods = methods or ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

    def decorator(cls):
        for method in methods:
            method_lower = method.lower()
            if hasattr(cls, method_lower):
                original_method = getattr(cls, method_lower)
                decorated_method = _create_rate_limited_method(
                    original_method,
                    method_lower,
                    cls.__module__,
                    cls.__name__,
                    limit,
                    window,
                    decorator_kwargs,
                )
                setattr(cls, method_lower, decorated_method)
        return cls

    return decorator


def _create_rate_limited_method(
    original_method, method_name, cls_module, cls_name, limit, window, decorator_kwargs
):
    """Create a rate-limited wrapper for a class method."""

    @functools.wraps(original_method)
    def method_wrapper(self, request, *args, **kwargs):
        return _handle_rate_limiting(
            original_method,
            method_name,
            cls_module,
            cls_name,
            self,
            request,
            args,
            kwargs,
            limit,
            window,
            decorator_kwargs,
        )

    return method_wrapper


def _handle_rate_limiting(
    original_method,
    method_name,
    cls_module,
    cls_name,
    self,
    request,
    args,
    kwargs,
    limit,
    window,
    decorator_kwargs,
):
    """Handle the rate limiting logic for class methods."""
    # Get backend instance
    backend_kwargs_final = decorator_kwargs.get("backend_kwargs", {})
    backend_instance = get_backend(
        decorator_kwargs.get("backend", "memory"), **backend_kwargs_final
    )

    # Get rate limiter instance
    limiter_kwargs = {
        k: v
        for k, v in decorator_kwargs.items()
        if k
        not in [
            "backend",
            "backend_kwargs",
            "scope",
            "key_func",
            "error_response",
            "use_user",
        ]
    }
    rate_limiter = get_rate_limiter(
        algorithm=decorator_kwargs.get("algorithm", "sliding_window"),
        backend=backend_instance,
        **limiter_kwargs,
    )

    # Generate identifier
    key_func = decorator_kwargs.get("key_func")
    use_user = decorator_kwargs.get("use_user", True)
    if key_func:
        identifier = key_func(request)
    else:
        identifier = get_user_identifier(request, use_user)

    # Generate scope
    scope = decorator_kwargs.get("scope") or f"{cls_module}.{cls_name}.{method_name}"

    try:
        # Check rate limit
        metadata = rate_limiter.enforce(identifier, limit, window, scope)

        # Call original method
        response = original_method(self, request, *args, **kwargs)

        # Add rate limiting headers
        if hasattr(response, "__setitem__"):
            response["X-RateLimit-Limit"] = str(limit)
            response["X-RateLimit-Remaining"] = str(metadata.get("remaining", 0))
            response["X-RateLimit-Reset"] = str(int(metadata.get("reset_time", 0)))

        return response

    except RateLimitExceeded as e:
        return _create_error_response(e, limit, window, decorator_kwargs)


def _create_error_response(exception, limit, window, decorator_kwargs):
    """Create an error response for rate limit exceeded."""
    error_response = decorator_kwargs.get("error_response")
    if error_response:
        return error_response(exception)

    # Default error response
    response_data = {
        "error": "Rate limit exceeded",
        "message": str(exception),
        "limit": limit,
        "window": window,
    }

    if exception.retry_after:
        response_data["retry_after"] = exception.retry_after

    response = JsonResponse(response_data, status=429)
    response["X-RateLimit-Limit"] = str(limit)
    response["X-RateLimit-Remaining"] = "0"

    if exception.retry_after:
        response["Retry-After"] = str(exception.retry_after)

    return response


def throttle(rate: str, algorithm: str = "token_bucket", **decorator_kwargs):
    """
    Simplified rate limiting decorator using rate strings.

    Args:
        rate: Rate string in format "limit/period"
            (e.g., "100/hour", "10/minute", "1/second")
        algorithm: Rate limiting algorithm
        **decorator_kwargs: Additional arguments passed to rate_limit decorator

    Example:
        @throttle("100/hour")
        def my_view(request):
            return JsonResponse({"message": "Hello world"})

        @throttle("10/minute", algorithm="sliding_window")
        def api_endpoint(request):
            return JsonResponse({"data": "some data"})
    """
    # Parse rate string
    try:
        limit_str, period_str = rate.split("/")
        limit = int(limit_str)

        period_multipliers = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }

        if period_str not in period_multipliers:
            raise ValueError(f"Invalid period: {period_str}")

        window = period_multipliers[period_str]

    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Invalid rate format: {rate}. Use 'limit/period' format."
        ) from e

    return rate_limit(
        limit=limit, window=window, algorithm=algorithm, **decorator_kwargs
    )


def per_user_rate_limit(limit: int, window: int, **decorator_kwargs):
    """
    Rate limit per authenticated user (falls back to IP for anonymous users).

    Args:
        limit: Maximum number of requests allowed per user
        window: Time window in seconds
        **decorator_kwargs: Additional arguments passed to rate_limit decorator
    """
    return rate_limit(limit=limit, window=window, use_user=True, **decorator_kwargs)


def per_ip_rate_limit(limit: int, window: int, **decorator_kwargs):
    """
    Rate limit per IP address.

    Args:
        limit: Maximum number of requests allowed per IP
        window: Time window in seconds
        **decorator_kwargs: Additional arguments passed to rate_limit decorator
    """
    return rate_limit(limit=limit, window=window, use_user=False, **decorator_kwargs)


def custom_key_rate_limit(
    key_func: Callable[[HttpRequest], str], limit: int, window: int, **decorator_kwargs
):
    """
    Rate limit using a custom key function.

    Args:
        key_func: Function that takes a request and returns a unique key
        limit: Maximum number of requests allowed
        window: Time window in seconds
        **decorator_kwargs: Additional arguments passed to rate_limit decorator

    Example:
        def api_key_extractor(request):
            return request.META.get('HTTP_X_API_KEY', 'anonymous')

        @custom_key_rate_limit(api_key_extractor, limit=1000, window=3600)
        def api_view(request):
            return JsonResponse({"data": "api response"})
    """
    return rate_limit(limit=limit, window=window, key_func=key_func, **decorator_kwargs)


def rate_limit_method(method_name: str, limit: int, window: int, **decorator_kwargs):
    """
    Class decorator for rate limiting a specific method of a Django class-based view.

    Args:
        method_name: Name of the HTTP method to rate limit (e.g., 'get', 'post', 'put')
        limit: Maximum number of requests allowed
        window: Time window in seconds
        **decorator_kwargs: Additional arguments passed to rate_limit decorator

    Example:
        @rate_limit_method('post', limit=50, window=3600)
        class MyAPIView(APIView):
            def get(self, request):
                return Response({"message": "Not rate limited"})

            def post(self, request):
                return Response({"message": "Rate limited"})
    """

    def decorator(cls):
        method_lower = method_name.lower()
        if hasattr(cls, method_lower):
            original_method = getattr(cls, method_lower)
            decorated_method = _create_rate_limited_method(
                original_method,
                method_lower,
                cls.__module__,
                cls.__name__,
                limit,
                window,
                decorator_kwargs,
            )
            setattr(cls, method_lower, decorated_method)
        return cls

    return decorator
