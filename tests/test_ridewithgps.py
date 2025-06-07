import pytest
import json
from types import SimpleNamespace
from typing import Any, Dict, Optional

from ridewithgps.apiclient import APIError
from ridewithgps.ridewithgps import RideWithGPS


class DummyAPIClient:
    """A dummy APIClient to mock HTTP calls for unit testing."""

    def __init__(self, *args, **kwargs):
        self.calls = []

    def _to_obj(self, data: Any) -> Any:
        if isinstance(data, dict):
            return SimpleNamespace(**{k: self._to_obj(v) for k, v in data.items()})
        if isinstance(data, list):
            return [self._to_obj(i) for i in data]
        return data

    def call(self, *args, path=None, params=None, method="GET", **kwargs):
        self.calls.append((path, params, method))
        json_result = "{}"
        if path == "/users/current.json":
            json_result = '{"user": {"id": 1, "display_name": "Test User", "auth_token": "FAKE_TOKEN"}}'
        elif path and path.startswith("/trips/") and method == "PUT":
            json_result = '{"trip": {"id": 123, "name": "%s"}}' % params.get("name", "")
        elif path == "/users/1/trips.json":
            json_result = '{"results": [{"id": 101, "name": "Ride 1"}, {"id": 102, "name": "Ride 2"}]}'
        elif path == "/test_post" and method == "POST":
            json_result = '{"result": "created", "id": 42}'
        elif path == "/test_delete" and method == "DELETE":
            json_result = '{"result": "deleted", "id": 42}'
        return self._to_obj(json.loads(json_result))


@pytest.fixture
def ridewithgps(monkeypatch):
    # Patch RideWithGPS to use DummyAPIClient as its base
    RideWithGPS.__bases__ = (DummyAPIClient,)
    return RideWithGPS(apikey="dummykey")


def test_authenticate_sets_user_info_and_token(ridewithgps):
    user = ridewithgps.authenticate(email="test@example.com", password="pw")
    assert user.id == 1
    assert user.display_name == "Test User"
    assert ridewithgps.auth_token == "FAKE_TOKEN"


def test_get_returns_python_object(ridewithgps):
    ridewithgps.authenticate(email="test@example.com", password="pw")
    rides = ridewithgps.get(
        path="/users/1/trips.json", params={"offset": 0, "limit": 2}
    )
    assert hasattr(rides, "results")
    assert isinstance(rides.results, list)
    assert rides.results[0].name == "Ride 1"


def test_put_updates_trip_name(ridewithgps):
    ridewithgps.authenticate(email="test@example.com", password="pw")
    new_name = "Morning Ride"
    response = ridewithgps.put(
        path="/trips/123.json",
        params={"name": new_name},
    )
    assert hasattr(response, "trip")
    assert response.trip.name == new_name


def test_post_creates_resource(ridewithgps):
    response = ridewithgps.post(path="/test_post", params={"foo": "bar"})
    assert hasattr(response, "result")
    assert response.result == "created"
    assert response.id == 42


def test_delete_removes_resource(ridewithgps):
    response = ridewithgps.delete(path="/test_delete", params={"id": 42})
    assert hasattr(response, "result")
    assert response.result == "deleted"
    assert response.id == 42
