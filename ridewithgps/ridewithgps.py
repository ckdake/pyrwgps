from ridewithgps import APIClient


class RideWithGPS(APIClient):
    BASE_URL = "https://ridewithgps.com/"

    def __init__(self, api_key: str, version: int = 2, *args: object, **kwargs: object):
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        self.version = version
        self.user_info = None
        self.auth_token = None

    def authenticate(self, email: str, password: str):
        """Authenticate and store user info and auth token for future requests."""
        resp = self.call(
            "/users/current.json",
            {"email": email, "password": password}
        )
        self.user_info = resp.get("user")
        self.auth_token = self.user_info.get("auth_token") if self.user_info else None
        return self.user_info

    def call(
        self,
        endpoint: str,
        params: dict[str, object] | None = None,
        *args: object,
        **kwargs: object
    ):
        if params is None:
            params = {}
        params.setdefault("apikey", self.api_key)
        params.setdefault("version", self.version)
        # Automatically add auth_token if authenticated and not already present
        if self.auth_token and "auth_token" not in params:
            params["auth_token"] = self.auth_token
        return super().call(endpoint, params, *args, **kwargs)
