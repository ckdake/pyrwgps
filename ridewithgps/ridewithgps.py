"""Main RideWithGPS API client."""

import json
from types import SimpleNamespace
from typing import Any, Dict, Optional
from ridewithgps import APIClient


class RideWithGPSError(Exception):
    """Base exception for RideWithGPS client errors."""


class RideWithGPSAPIError(RideWithGPSError):
    """Exception for API errors (e.g., HTTP errors, API error responses)."""

    def __init__(self, message: str, response: Any = None):
        super().__init__(message)
        self.response = response


class RideWithGPS(APIClient):
    """Main RideWithGPS API client."""

    BASE_URL = "https://ridewithgps.com/"

    def __init__(self, api_key: str, version: int = 2, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)
        self.api_key: str = api_key
        self.version: int = version
        self.user_info: Optional[SimpleNamespace] = None
        self.auth_token: Optional[str] = None

    def _to_obj(self, data: Any) -> Any:
        if isinstance(data, dict):
            return SimpleNamespace(**{k: self._to_obj(v) for k, v in data.items()})
        if isinstance(data, list):
            return [self._to_obj(i) for i in data]
        return data

    def authenticate(self, email: str, password: str) -> Optional[SimpleNamespace]:
        """Authenticate and store user info and auth token for future requests."""
        resp = self.get("/users/current.json", {"email": email, "password": password})
        self.user_info = resp.user if hasattr(resp, "user") else None
        self.auth_token = self.user_info.auth_token if self.user_info else None
        return self.user_info

    def call(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        *args: object,
        **kwargs: object,
    ) -> Any:
        if params is None:
            params = {}
        params.setdefault("apikey", self.api_key)
        params.setdefault("version", self.version)
        if self.auth_token and "auth_token" not in params:
            params["auth_token"] = self.auth_token
        response = super().call(endpoint, params, method=method, *args, **kwargs)
        # Convert string to Python object if possible, all responses should be JSON
        if isinstance(response, str):
            try:
                data = json.loads(response)
                if isinstance(data, dict) and ("error" in data or "errors" in data):
                    message = (
                        data.get("error") or data.get("errors") or "Unknown API error"
                    )
                    raise RideWithGPSAPIError(str(message), response=data)
                return self._to_obj(data)
            except json.JSONDecodeError as exc:
                raise RideWithGPSAPIError(
                    "Invalid JSON response", response=response
                ) from exc
        return response

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        *args: object,
        **kwargs: object,
    ) -> Any:
        """Make a GET request to the API and return a Python object."""
        return self.call(endpoint, params, "GET", *args, **kwargs)

    def put(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        *args: object,
        **kwargs: object,
    ) -> Any:
        """Make a PUT request to the API and return a Python object."""
        return self.call(endpoint, params, "PUT", *args, **kwargs)

    def post(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        *args: object,
        **kwargs: object,
    ) -> Any:
        """Make a POST request to the API and return a Python object."""
        return self.call(endpoint, params, "POST", *args, **kwargs)

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        *args: object,
        **kwargs: object,
    ) -> Any:
        """Make a DELETE request to the API and return a Python object."""
        return self.call(endpoint, params, "DELETE", *args, **kwargs)
