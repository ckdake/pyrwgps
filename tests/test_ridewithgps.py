import pytest
from ridewithgps.ridewithgps import RideWithGPS, RideWithGPSAPIError


class DummyAPIClient:
    """A dummy APIClient to mock HTTP calls for unit testing."""

    def __init__(self, *args, **kwargs):
        self.calls = []

    def call(self, endpoint, params=None, method="GET", *args, **kwargs):
        self.calls.append((endpoint, params, method))
        # Simulate a JSON API response as a string
        if endpoint == "/users/current.json":
            return '{"user": {"id": 1, "display_name": "Test User", "auth_token": "FAKE_TOKEN"}}'
        elif endpoint.startswith("/trips/") and method == "PUT":
            return '{"trip": {"id": 123, "name": "%s"}}' % params.get("name", "")
        elif endpoint.startswith("/users/1/trips.json"):
            return '{"results": [{"id": 101, "name": "Ride 1"}, {"id": 102, "name": "Ride 2"}]}'
        elif endpoint == "/test_post" and method == "POST":
            return '{"result": "created", "id": 42}'
        elif endpoint == "/test_delete" and method == "DELETE":
            return '{"result": "deleted", "id": 42}'
        return "{}"


@pytest.fixture
def ridewithgps(monkeypatch):
    # Patch RideWithGPS to use DummyAPIClient as its base
    RideWithGPS.__bases__ = (DummyAPIClient,)
    return RideWithGPS(api_key="dummykey")


def test_authenticate_sets_user_info_and_token(ridewithgps):
    user = ridewithgps.authenticate(email="test@example.com", password="pw")
    assert user.id == 1
    assert user.display_name == "Test User"
    assert ridewithgps.auth_token == "FAKE_TOKEN"


def test_get_returns_python_object(ridewithgps):
    ridewithgps.authenticate(email="test@example.com", password="pw")
    rides = ridewithgps.get("/users/1/trips.json", {"offset": 0, "limit": 2})
    assert hasattr(rides, "results")
    assert isinstance(rides.results, list)
    assert rides.results[0].name == "Ride 1"


def test_put_updates_trip_name(ridewithgps):
    ridewithgps.authenticate(email="test@example.com", password="pw")
    new_name = "Morning Ride"
    response = ridewithgps.put("/trips/123.json", {"name": new_name})
    assert hasattr(response, "trip")
    assert response.trip.name == new_name


def test_post_creates_resource(ridewithgps):
    response = ridewithgps.post("/test_post", {"foo": "bar"})
    assert hasattr(response, "result")
    assert response.result == "created"
    assert response.id == 42


def test_delete_removes_resource(ridewithgps):
    response = ridewithgps.delete("/test_delete", {"id": 42})
    assert hasattr(response, "result")
    assert response.result == "deleted"
    assert response.id == 42


def test_api_error_raises_exception(ridewithgps, monkeypatch):
    # Patch DummyAPIClient.call to return an error response
    def error_call(self, endpoint, params=None, method="GET", *args, **kwargs):
        return '{"error": "Invalid credentials"}'

    monkeypatch.setattr(DummyAPIClient, "call", error_call)

    with pytest.raises(RideWithGPSAPIError) as excinfo:
        ridewithgps.get("/users/current.json", {"email": "bad", "password": "bad"})
    assert "Invalid credentials" in str(excinfo.value)
    assert hasattr(excinfo.value, "response")
    assert excinfo.value.response["error"] == "Invalid credentials"
