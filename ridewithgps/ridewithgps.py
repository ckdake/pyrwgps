import json
from types import SimpleNamespace
from typing import Any, Dict, Optional, List
from ridewithgps import APIClient


class RideWithGPS(APIClient):
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
        elif isinstance(data, list):
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
        # Automatically add auth_token if authenticated and not already present
        if self.auth_token and "auth_token" not in params:
            params["auth_token"] = self.auth_token
        response = super().call(endpoint, params, method=method, *args, **kwargs)
        # Convert string to Python object if possible, all responses should be JSON
        if isinstance(response, str):
            try:
                data = json.loads(response)
                return self._to_obj(data)
            except Exception:
                return response
        return response

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, *args: object, **kwargs: object) -> Any:
        """Make a GET request to the API and return a Python object."""
        return self.call(endpoint, params, method="GET", *args, **kwargs)

    def put(self, endpoint: str, params: Optional[Dict[str, Any]] = None, *args: object, **kwargs: object) -> Any:
        """Make a PUT request to the API and return a Python object."""
        return self.call(endpoint, params, method="PUT", *args, **kwargs)

    def post(self, endpoint: str, params: Optional[Dict[str, Any]] = None, *args: object, **kwargs: object) -> Any:
        """Make a POST request to the API and return a Python object."""
        return self.call(endpoint, params, method="POST", *args, **kwargs)

    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, *args: object, **kwargs: object) -> Any:
        """Make a DELETE request to the API and return a Python object."""
        return self.call(endpoint, params, method="DELETE", *args, **kwargs)
