"""Base HTTP client and shared secret client for the ridewithgps package."""

import json
from urllib.parse import urlencode

import urllib3
import certifi
from .ratelimiter import RateLimiter


class APIClient:
    """Base HTTP client for RideWithGPS API."""

    BASE_URL = "http://localhost:5000/"

    def __init__(
        self,
        rate_limit_lock=None,
        encoding="utf8",
        rate_limit_max=10,
        rate_limit_seconds=1,
        *args,
        **kwargs,
    ):
        """
        Initialize the API client.

        Args:
            rate_limit_lock: Optional lock for rate limiting.
            encoding: Response encoding.
            rate_limit_max: Max requests per window.
            rate_limit_seconds: Window size in seconds.
        """
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
        print(params)
        return self.BASE_URL + path + "?" + urlencode(params)

    def _handle_response(self, response):
        """Decode and parse the HTTP response as JSON."""
        return json.loads(response.data.decode(self.encoding))

    def _request(self, method, path, params=None):
        """Make an HTTP request and return the parsed response."""
        url = self._compose_url(path, params)
        print(url)
        if self.rate_limit_lock:
            self.rate_limit_lock.acquire()
        r = self.connection_pool.urlopen(method.upper(), url)
        return self._handle_response(r)

    def call(self, path, params=None, method="GET", *args, **kwargs):
        """
        Make a rate-limited API call.

        Args:
            path: API endpoint path.
            params: Query parameters.
            method: HTTP method.
        """
        self.ratelimiter.acquire()
        return self._request(method, path, params=params)


class APIClientSharedSecret(APIClient):
    """API client that uses a shared secret key."""

    API_KEY_PARAM = "key"

    def __init__(self, api_key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key

    def _compose_url(self, path, params=None):
        """Compose a URL including the shared secret key."""
        p = {self.API_KEY_PARAM: self.api_key}
        if params:
            p.update(params)
        return self.BASE_URL + path + "?" + urlencode(p)
