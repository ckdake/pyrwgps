"""Main RideWithGPS API client."""

from types import SimpleNamespace
from typing import Any, Dict, Optional
from ridewithgps.apiclient import APIClientSharedSecret


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
        """Authenticate and store user info and auth token for future requests."""
        resp = self.get(
            path="/users/current.json", params={"email": email, "password": password}
        )
        self.user_info = resp.user if hasattr(resp, "user") else None
        self.auth_token = self.user_info.auth_token if self.user_info else None
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

    def delete(
        self,
        *args: Any,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a DELETE request to the API and return a Python object."""
        return self.call(*args, path=path, params=params, method="DELETE", **kwargs)

    def list(
        self,
        path: str,
        params: Optional[dict] = None,
        limit: Optional[int] = None,
        **kwargs,
    ):
        """
        Yield up to `limit` items from a RideWithGPS list/search endpoint (auto-paginates).
        If limit is None, yield all available results.
        """
        if params is None:
            params = {}
        offset = params.get("offset", 0)
        fetched = 0
        page_limit = 100  # API max per page, adjust if needed

        while True:
            this_page_limit = page_limit
            if limit is not None:
                remaining = limit - fetched
                if remaining <= 0:
                    break
                this_page_limit = min(page_limit, remaining)

            page_params = params.copy()
            page_params.update({"offset": offset, "limit": this_page_limit})
            response = self.get(path=path, params=page_params, **kwargs)
            items = getattr(response, "results", None)
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
