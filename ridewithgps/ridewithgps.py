"""Main RideWithGPS API client."""

from types import SimpleNamespace
from typing import Any, Dict, Optional
from ridewithgps.apiclient import APIClientSharedSecret


class RideWithGPS(APIClientSharedSecret):
    """Main RideWithGPS API client."""

    BASE_URL = "https://ridewithgps.com/"

    def __init__(self, *args: object, apikey: str, version: int = 2, **kwargs: object):
        super().__init__(apikey, *args, **kwargs)
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
