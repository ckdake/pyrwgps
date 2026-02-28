"""Main RideWithGPS API client."""

import json
from types import SimpleNamespace
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from pyrwgps.apiclient import APIClient


class RideWithGPS(APIClient):
    """RideWithGPS API client.

    Supports two authentication methods depending on how it is initialised:

    **API key (shared secret):**

        client = RideWithGPS(apikey="your_key")
        client.authenticate(email="...", password="...")

    **OAuth 2.0:**

        client = RideWithGPS(client_id="...", client_secret="...")
        url = client.authorization_url(redirect_uri="https://yourapp.com/callback")
        client.exchange_code(code="...", redirect_uri="https://yourapp.com/callback")

    Or with an existing access token:

        client = RideWithGPS(client_id="...", client_secret="...", access_token="tok")
    """

    BASE_URL = "https://ridewithgps.com/"
    _OAUTH_AUTHORIZE_URL = "https://ridewithgps.com/oauth/authorize"
    _OAUTH_TOKEN_PATH = "/oauth/token.json"

    def __init__(
        self,
        *args: object,
        apikey: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        version: int = 2,
        cache: bool = False,
        **kwargs: object,
    ):
        if apikey is None and client_id is None:
            raise ValueError(
                "Provide apikey= for API key auth, "
                "or client_id= + client_secret= for OAuth."
            )
        super().__init__(*args, cache=cache, **kwargs)
        self.apikey = apikey
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.version = version
        self.user_info: Optional[SimpleNamespace] = None
        self.auth_token: Optional[str] = None  # set by authenticate()

    @property
    def _oauth(self) -> bool:
        """True when this client is using OAuth."""
        return self.client_id is not None

    # ------------------------------------------------------------------
    # Auth methods
    # ------------------------------------------------------------------

    def authenticate(self, email: str, password: str) -> Optional[SimpleNamespace]:
        """Authenticate with email/password and store the session token.

        API key auth only. For OAuth, use authorization_url() + exchange_code().
        """
        if self._oauth:
            raise ValueError(
                "authenticate() is for API key auth. "
                "For OAuth, use authorization_url() and exchange_code()."
            )
        resp = self.post(
            path="/api/v1/auth_tokens.json",
            params={"user": {"email": email, "password": password}},
        )
        auth_token_obj = resp.auth_token if hasattr(resp, "auth_token") else None
        self.user_info = (
            auth_token_obj.user
            if auth_token_obj and hasattr(auth_token_obj, "user")
            else None
        )
        self.auth_token = (
            auth_token_obj.auth_token
            if auth_token_obj and hasattr(auth_token_obj, "auth_token")
            else None
        )
        return self.user_info

    def authorization_url(self, redirect_uri: str) -> str:
        """Return the OAuth authorization URL to redirect users to.

        OAuth only. For API key auth, use authenticate().
        """
        if not self._oauth:
            raise ValueError(
                "authorization_url() is for OAuth. "
                "For API key auth, use authenticate()."
            )
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
        }
        return self._OAUTH_AUTHORIZE_URL + "?" + urlencode(params)

    def exchange_code(self, code: str, redirect_uri: str) -> Any:
        """Exchange an OAuth authorization code for an access token.

        Stores the access_token on this client for subsequent requests.
        OAuth only. For API key auth, use authenticate().
        """
        if not self._oauth:
            raise ValueError(
                "exchange_code() is for OAuth. "
                "For API key auth, use authenticate()."
            )
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
        }
        response = self._request("POST", self._OAUTH_TOKEN_PATH, params=params)
        if isinstance(response, dict):
            self.access_token = response.get("access_token")
        return self._to_obj(response)

    # ------------------------------------------------------------------
    # HTTP layer
    # ------------------------------------------------------------------

    def _compose_url(self, path, params=None):
        """For API key auth, inject apikey into every GET/DELETE URL."""
        if self._oauth:
            return super()._compose_url(path, params)
        p = {"apikey": self.apikey}
        if params:
            p.update(params)
        base_url = self.BASE_URL.rstrip("/")
        return f"{base_url}/{path.lstrip('/')}?" + urlencode(p)

    def _request(self, method, path, params=None, extra_headers=None):
        """Apply auth appropriate for the active auth method."""
        if self._oauth:
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"
            if extra_headers:
                headers.update(extra_headers)
            return super()._request(method, path, params=params, extra_headers=headers)

        # API key auth: inject apikey into URL; version/auth_token stay in query string
        method = method.upper()
        if method in ("POST", "PUT", "PATCH"):
            query_params = {"apikey": self.apikey}
            body_params = {}
            if params:
                for key, value in params.items():
                    if key in ("version", "auth_token"):
                        query_params[key] = value
                    else:
                        body_params[key] = value
            base_url = self.BASE_URL.rstrip("/")
            url = f"{base_url}/{path.lstrip('/')}?" + urlencode(query_params)
            headers = {
                "Content-Type": "application/json",
                "x-rwgps-api-key": self.apikey,
            }
            if "auth_token" in query_params:
                headers["x-rwgps-auth-token"] = query_params["auth_token"]
            if extra_headers:
                headers.update(extra_headers)
            body = json.dumps(body_params).encode(self.encoding)
            if self.rate_limit_lock:
                self.rate_limit_lock.acquire()
            r = self.connection_pool.urlopen(method, url, body=body, headers=headers)
        else:
            url = self._compose_url(path, params)
            headers = {"x-rwgps-api-key": self.apikey}
            if params and "auth_token" in params:
                headers["x-rwgps-auth-token"] = params["auth_token"]
            if extra_headers:
                headers.update(extra_headers)
            if self.rate_limit_lock:
                self.rate_limit_lock.acquire()
            r = self.connection_pool.urlopen(method, url, headers=headers)
        return self._handle_response(r)

    def call(
        self,
        *args: Any,
        path: Any,
        params: Any = None,
        method: Any = "GET",
        **kwargs: Any,
    ) -> Any:
        if params is None:
            params = {}
        if not self._oauth:
            params.setdefault("version", self.version)
            if self.auth_token and "auth_token" not in params:
                params["auth_token"] = self.auth_token
        return super().call(*args, path=path, params=params, method=method, **kwargs)

    # ------------------------------------------------------------------
    # API methods
    # ------------------------------------------------------------------

    def get(
        self,
        *args: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a GET request to the API and return a Python object."""
        return self.call(*args, path=path, params=params, method="GET", **kwargs)

    def put(
        self,
        *args: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a PUT request to the API and return a Python object."""
        return self.call(*args, path=path, params=params, method="PUT", **kwargs)

    def post(
        self,
        *args: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a POST request to the API and return a Python object."""
        return self.call(*args, path=path, params=params, method="POST", **kwargs)

    def patch(
        self,
        *args: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a PATCH request to the API and return a Python object."""
        return self.call(*args, path=path, params=params, method="PATCH", **kwargs)

    def delete(
        self,
        *args: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a DELETE request to the API and return a Python object."""
        return self.call(*args, path=path, params=params, method="DELETE", **kwargs)

    def _list_v1(self, path, params, limit, result_key, **kwargs):
        """Yield items from a v1 API endpoint using page/page_size pagination."""
        page_size = params.get("page_size", 100)
        page = params.get("page", 1)
        fetched = 0

        while True:
            this_page_size = (
                page_size if limit is None else min(page_size, limit - fetched)
            )
            if limit is not None and this_page_size <= 0:
                break
            page_params = {**params, "page": page, "page_size": this_page_size}
            response = self.get(path=path, params=page_params, **kwargs)
            items = getattr(response, result_key, None)
            if not items:
                break
            for item in items:
                yield item
                fetched += 1
                if limit is not None and fetched >= limit:
                    return
            pagination = getattr(getattr(response, "meta", None), "pagination", None)
            if not getattr(pagination, "next_page_url", None):
                break
            page += 1

    def _list_legacy(self, path, params, limit, result_key, **kwargs):
        """Yield items from a legacy API endpoint using offset/limit pagination."""
        offset = params.get("offset", 0)
        page_limit = 100
        fetched = 0

        while True:
            this_limit = (
                page_limit if limit is None else min(page_limit, limit - fetched)
            )
            if limit is not None and this_limit <= 0:
                break
            page_params = {**params, "offset": offset, "limit": this_limit}
            response = self.get(path=path, params=page_params, **kwargs)
            items = getattr(response, result_key, None)
            if not items:
                break
            for item in items:
                yield item
                fetched += 1
                if limit is not None and fetched >= limit:
                    return
            offset += len(items)
            results_count = getattr(response, "results_count", None)
            if results_count is not None and offset >= results_count:
                break

    def list(
        self,
        path: str,
        params: Optional[dict] = None,
        limit: Optional[int] = None,
        result_key: str = "results",
        **kwargs,
    ):
        """Yield up to `limit` items from a RideWithGPS list/search endpoint (auto-paginates).

        If limit is None, yield all available results.

        Supports both the legacy API (offset/limit/results_count) and the v1 API
        (page/page_size/meta.pagination). For v1 endpoints (e.g. /api/v1/trips.json),
        pass the root key of the response as ``result_key`` (e.g. ``result_key="trips"``).
        """
        if params is None:
            params = {}
        paginator = self._list_v1 if "/api/v1/" in path else self._list_legacy
        yield from paginator(path, params, limit, result_key, **kwargs)
