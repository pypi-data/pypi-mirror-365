"""
Django middleware for automatic rate limiting.
"""

import re
from typing import Any, Dict, Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin

from .algorithms import get_rate_limiter
from .backends import get_backend
from .decorators import get_client_ip, get_user_identifier
from .exceptions import RateLimitExceeded


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware for automatic rate limiting based on configuration.

    Settings example:

    RATE_LIMIT_SETTINGS = {
        'BACKEND': 'memory',  # 'memory', 'database', 'redis'
        'BACKEND_KWARGS': {},  # Additional backend configuration
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
        'GLOBAL_LIMIT': 10000,  # Global limit per user/IP
        'GLOBAL_WINDOW': 3600,
        'EXEMPT_PATHS': [r'^/health/$', r'^/static/'],
        'EXEMPT_IPS': ['127.0.0.1', '::1'],
        'USE_USER_ID': True,  # Use authenticated user ID when available
        'RATE_LIMIT_HEADERS': True,  # Add rate limit headers to responses
    }
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.config = getattr(settings, "RATE_LIMIT_SETTINGS", {})
        self._setup_backend()
        self._compile_patterns()

    def _setup_backend(self):
        """Initialize the storage backend."""
        backend_type = self.config.get("BACKEND", "memory")
        backend_kwargs = self.config.get("BACKEND_KWARGS", {})
        self.backend = get_backend(backend_type, **backend_kwargs)

    def _compile_patterns(self):
        """Compile regex patterns for performance."""
        self.exempt_patterns = [
            re.compile(pattern) for pattern in self.config.get("EXEMPT_PATHS", [])
        ]

        self.rules = []
        for rule in self.config.get("RULES", []):
            compiled_rule = rule.copy()
            compiled_rule["compiled_pattern"] = re.compile(rule["path_pattern"])
            self.rules.append(compiled_rule)

    def _is_exempt(self, request: HttpRequest) -> bool:
        """Check if request is exempt from rate limiting."""
        # Check exempt IPs
        client_ip = get_client_ip(request)
        exempt_ips = self.config.get("EXEMPT_IPS", [])
        if client_ip in exempt_ips:
            return True

        # Check exempt paths
        path = request.path
        for pattern in self.exempt_patterns:
            if pattern.match(path):
                return True

        return False

    def _find_matching_rule(self, request: HttpRequest) -> Optional[Dict[str, Any]]:
        """Find the first rule that matches the request path."""
        path = request.path
        for rule in self.rules:
            if rule["compiled_pattern"].match(path):
                return rule
        return None

    def _get_rate_limiter(self, algorithm: Optional[str] = None) -> Any:
        """Get rate limiter instance."""
        algorithm = algorithm or self.config.get("DEFAULT_ALGORITHM", "sliding_window")
        return get_rate_limiter(algorithm=algorithm, backend=self.backend)

    def _add_rate_limit_headers(
        self, response: HttpResponse, metadata: Dict[str, Any], limit: int
    ):
        """Add rate limiting headers to response."""
        if not self.config.get("RATE_LIMIT_HEADERS", True):
            return

        if hasattr(response, "__setitem__"):
            response["X-RateLimit-Limit"] = str(limit)
            response["X-RateLimit-Remaining"] = str(metadata.get("remaining", 0))

            reset_time = metadata.get("reset_time")
            if reset_time:
                response["X-RateLimit-Reset"] = str(int(reset_time))

    def _create_error_response(self, error: RateLimitExceeded) -> HttpResponse:
        """Create error response for rate limit exceeded."""
        response_data = {
            "error": "Rate limit exceeded",
            "message": str(error),
        }

        if error.retry_after:
            response_data["retry_after"] = error.retry_after

        if error.limit and error.window:
            response_data["limit"] = error.limit
            response_data["window"] = error.window

        response = JsonResponse(response_data, status=429)

        if error.retry_after:
            response["Retry-After"] = str(error.retry_after)

        return response

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process incoming request for rate limiting."""
        # Skip if exempt
        if self._is_exempt(request):
            return None

        # Find matching rule
        rule = self._find_matching_rule(request)

        # Apply global rate limiting if no specific rule
        if not rule:
            global_limit = self.config.get("GLOBAL_LIMIT")
            global_window = self.config.get("GLOBAL_WINDOW")

            if not (global_limit and global_window):
                return None

            rule = {
                "limit": global_limit,
                "window": global_window,
                "algorithm": self.config.get("DEFAULT_ALGORITHM", "sliding_window"),
                "scope": "global",
                "use_user": self.config.get("USE_USER_ID", True),
            }

        # Get identifier
        use_user = rule.get("use_user", self.config.get("USE_USER_ID", True))
        identifier = get_user_identifier(request, use_user)

        # Get rate limiter
        algorithm: Optional[str] = rule.get("algorithm")
        rate_limiter = self._get_rate_limiter(algorithm)

        try:
            # Check rate limit
            metadata = rate_limiter.enforce(
                identifier=identifier,
                limit=rule["limit"],
                window=rule["window"],
                scope=rule.get("scope", "default"),
            )

            # Store metadata for response processing
            request._rate_limit_metadata = metadata
            request._rate_limit_limit = rule["limit"]

        except RateLimitExceeded as e:
            return self._create_error_response(e)

        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Add rate limiting headers to response."""
        if hasattr(request, "_rate_limit_metadata"):
            self._add_rate_limit_headers(
                response, request._rate_limit_metadata, request._rate_limit_limit
            )

        return response


class PerIPRateLimitMiddleware(MiddlewareMixin):
    """
    Simple middleware for per-IP rate limiting.

    Settings example:

    PER_IP_RATE_LIMIT = {
        'LIMIT': 1000,
        'WINDOW': 3600,  # 1 hour
        'ALGORITHM': 'sliding_window',
        'BACKEND': 'memory',
    }
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.config = getattr(settings, "PER_IP_RATE_LIMIT", {})

        if self.config:
            backend_type = self.config.get("BACKEND", "memory")
            self.backend = get_backend(backend_type)

            algorithm = self.config.get("ALGORITHM", "sliding_window")
            self.rate_limiter = get_rate_limiter(
                algorithm=algorithm, backend=self.backend
            )

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process request for per-IP rate limiting."""
        if not self.config:
            return None

        ip_address = get_client_ip(request)

        try:
            self.rate_limiter.enforce(
                identifier=ip_address,
                limit=self.config["LIMIT"],
                window=self.config["WINDOW"],
                scope="per_ip",
            )
        except RateLimitExceeded as e:
            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests from IP {ip_address}",
                    "retry_after": e.retry_after,
                },
                status=429,
            )

        return None


class PerUserRateLimitMiddleware(MiddlewareMixin):
    """
    Simple middleware for per-user rate limiting.

    Settings example:

    PER_USER_RATE_LIMIT = {
        'LIMIT': 5000,
        'WINDOW': 3600,  # 1 hour
        'ALGORITHM': 'token_bucket',
        'BACKEND': 'database',
        'AUTHENTICATED_ONLY': True,  # Only rate limit authenticated users
    }
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response
        self.config = getattr(settings, "PER_USER_RATE_LIMIT", {})

        if self.config:
            backend_type = self.config.get("BACKEND", "memory")
            self.backend = get_backend(backend_type)

            algorithm = self.config.get("ALGORITHM", "sliding_window")
            self.rate_limiter = get_rate_limiter(
                algorithm=algorithm, backend=self.backend
            )

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Process request for per-user rate limiting."""
        if not self.config:
            return None

        # Skip if user is not authenticated and we only rate limit authenticated users
        if self.config.get("AUTHENTICATED_ONLY", False):
            if not (hasattr(request, "user") and request.user.is_authenticated):
                return None

        identifier = get_user_identifier(request, use_user=True)

        try:
            self.rate_limiter.enforce(
                identifier=identifier,
                limit=self.config["LIMIT"],
                window=self.config["WINDOW"],
                scope="per_user",
            )
        except RateLimitExceeded as e:
            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": "Too many requests from user",
                    "retry_after": e.retry_after,
                },
                status=429,
            )

        return None
