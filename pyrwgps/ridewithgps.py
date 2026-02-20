"""Main RideWithGPS API client."""

from types import SimpleNamespace
from typing import Any, Dict, Optional
from pyrwgps.apiclient import APIClientSharedSecret


class RideWithGPS(APIClientSharedSecret):
    """Main RideWithGPS API client."""

    BASE_URL = "https://ridewithgps.com/"

    def __init__(
        self,
        *args: object,
        apikey: str,
        version: int = 2,
        cache: bool = False,
        **kwargs: object,
    ):
        super().__init__(apikey, *args, cache=cache, **kwargs)
        self.apikey: str = apikey
        self.version: int = version
        self.user_info: Optional[SimpleNamespace] = None
        self.auth_token: Optional[str] = None

    def authenticate(self, email: str, password: str) -> Optional[SimpleNamespace]:
        """
        Authenticate using the v1 auth_tokens endpoint and store user info and
        auth token for future requests.

        Uses POST /api/v1/auth_tokens.json with x-rwgps-api-key header (Basic auth
        style — no OAuth required). The returned auth_token works for both v1 and
        legacy endpoints.
        """
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
        params.setdefault("version", self.version)
        if self.auth_token and "auth_token" not in params:
            params["auth_token"] = self.auth_token
        return super().call(*args, path=path, params=params, method=method, **kwargs)

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
        """
        Yield up to `limit` items from a RideWithGPS list/search endpoint (auto-paginates).
        If limit is None, yield all available results.

        Supports both the legacy API (offset/limit/results_count) and the v1 API
        (page/page_size/meta.pagination). For v1 endpoints (e.g. /api/v1/trips.json),
        pass the root key of the response as ``result_key`` (e.g. ``result_key="trips``).
        """
        if params is None:
            params = {}
        paginator = self._list_v1 if "/api/v1/" in path else self._list_legacy
        yield from paginator(path, params, limit, result_key, **kwargs)
