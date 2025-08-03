"""Base HTTP client and shared secret client for the ridewithgps package."""

import json
from urllib.parse import urlencode

from types import SimpleNamespace
from typing import Any

import urllib3
import certifi
from .ratelimiter import RateLimiter


class APIError(Exception):
    """Base exception for API client errors."""


class APIClient:
    """Base HTTP client for RideWithGPS API."""

    BASE_URL = "http://localhost:5000"

    def __init__(
        self,
        *args,
        cache: bool = False,
        rate_limit_lock=None,
        encoding="utf8",
        rate_limit_max=10,
        rate_limit_seconds=1,
        **kwargs,
    ):
        """
        Initialize the API client.

        Args:
            cache: Enable in-memory caching for GET requests.
            rate_limit_lock: Optional lock for rate limiting.
            encoding: Response encoding.
            rate_limit_max: Max requests per window.
            rate_limit_seconds: Window size in seconds.
        """
        # pylint: disable=unused-argument, too-many-arguments
        self.cache_enabled = cache
        self._cache: dict | None = {} if cache else None  # type: ignore[assignment]
        self.rate_limit_lock = rate_limit_lock
        self.encoding = encoding
        self.connection_pool = self._make_connection_pool()
        self.ratelimiter = RateLimiter(
            max_messages=rate_limit_max, every_seconds=rate_limit_seconds
        )

    def _make_connection_pool(self):
        """Create a urllib3 PoolManager with certifi CA certs."""
        return urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

    def _compose_url(self, path, params=None):
        """Compose a full URL from path and query parameters."""
        if params:
            return self.BASE_URL + path + "?" + urlencode(params)
        return self.BASE_URL + path

    def _handle_response(self, response):
        """Decode and parse the HTTP response as JSON."""
        return json.loads(response.data.decode(self.encoding))

    def _request(self, method, path, params=None):
        """Make an HTTP request and return the parsed response."""
        method = method.upper()
        
        if method in ("POST", "PUT", "PATCH"):
            # For POST/PUT/PATCH, send data as JSON in body
            url = self.BASE_URL + path
            headers = {"Content-Type": "application/json"}
            body = json.dumps(params or {}).encode(self.encoding)
            
            if self.rate_limit_lock:
                self.rate_limit_lock.acquire()
            r = self.connection_pool.urlopen(method, url, body=body, headers=headers)
        else:
            # For GET/DELETE, use query parameters
            url = self._compose_url(path, params)
            if self.rate_limit_lock:
                self.rate_limit_lock.acquire()
            r = self.connection_pool.urlopen(method, url)
            
        return self._handle_response(r)

    def _to_obj(self, data: Any) -> Any:
        if isinstance(data, dict):
            return SimpleNamespace(**{k: self._to_obj(v) for k, v in data.items()})
        if isinstance(data, list):
            return [self._to_obj(i) for i in data]
        return data

    def call(self, *args, path, params=None, method="GET", **kwargs):
        """
        Make a rate-limited API call.

        Args:
            path: API endpoint path.
            params: Query parameters.
            method: HTTP method.
        """
        # pylint: disable=unused-argument
        cache_key = None
        use_cache = (
            self.cache_enabled
            and method.upper() == "GET"
            and isinstance(self._cache, dict)
        )
        if use_cache:
            params_tuple = tuple(sorted((params or {}).items()))
            cache_key = (path, params_tuple)
            # pylint: disable=unsupported-membership-test, unsubscriptable-object
            if cache_key in self._cache:
                return self._cache[cache_key]

        self.ratelimiter.acquire()
        response = self._request(method, path, params=params)
        if isinstance(response, str):
            try:
                data = json.loads(response)
                if isinstance(data, dict) and ("error" in data or "errors" in data):
                    message = (
                        data.get("error") or data.get("errors") or "Unknown API error"
                    )
                    raise APIError(str(message))
                result = self._to_obj(data)
            except json.JSONDecodeError as exc:
                raise APIError("Invalid JSON response") from exc
        else:
            result = self._to_obj(response)

        if use_cache:
            # pylint: disable=unsupported-assignment-operation
            self._cache[cache_key] = result
        return result

    def clear_cache(self) -> None:
        """
        Clear the in-memory GET request cache.
        """
        if isinstance(self._cache, dict):
            self._cache.clear()


class APIClientSharedSecret(APIClient):
    """API client that uses a shared secret key."""

    # pylint: disable=too-few-public-methods

    API_KEY_PARAM = "apikey"

    def __init__(self, apikey, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apikey = apikey

    def _compose_url(self, path, params=None):
        """Compose a URL including the shared secret key."""
        p = {self.API_KEY_PARAM: self.apikey}
        if params:
            p.update(params)
        return self.BASE_URL + path + "?" + urlencode(p)

    def _request(self, method, path, params=None):
        """Make an HTTP request with API key authentication."""
        method = method.upper()
        
        if method in ("POST", "PUT", "PATCH"):
            # For POST/PUT/PATCH, send data as JSON in body, API key in URL
            url = self.BASE_URL + path + "?" + urlencode({self.API_KEY_PARAM: self.apikey})
            headers = {"Content-Type": "application/json"}
            body = json.dumps(params or {}).encode(self.encoding)
            
            if self.rate_limit_lock:
                self.rate_limit_lock.acquire()
            r = self.connection_pool.urlopen(method, url, body=body, headers=headers)
        else:
            # For GET/DELETE, use query parameters including API key
            url = self._compose_url(path, params)
            if self.rate_limit_lock:
                self.rate_limit_lock.acquire()
            r = self.connection_pool.urlopen(method, url)
            
        return self._handle_response(r)
