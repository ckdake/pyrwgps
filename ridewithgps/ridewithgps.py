from ridewithgps import APIClient


class RideWithGPS(APIClient):
    BASE_URL = "https://ridewithgps.com/"

    def __init__(self, api_key: str, version: int = 2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = api_key
        self.version = version

    def call(self, endpoint, params=None, *args, **kwargs):
        if params is None:
            params = {}
        params.setdefault("apikey", self.api_key)
        params.setdefault("version", self.version)
        return super().call(endpoint, params, *args, **kwargs)
