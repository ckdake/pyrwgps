import pytest
import json
from types import SimpleNamespace
from typing import Any, Dict, Optional

from pyrwgps.apiclient import APIError
from pyrwgps.ridewithgps import RideWithGPS


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
        if path == "/api/v1/auth_tokens.json" and method == "POST":
            json_result = json.dumps(
                {
                    "auth_token": {
                        "auth_token": "FAKE_TOKEN",
                        "user": {"id": 1, "display_name": "Test User"},
                    }
                }
            )
        elif path and path.startswith("/trips/") and method == "PUT":
            json_result = '{"trip": {"id": 123, "name": "%s"}}' % params.get("name", "")
        elif path == "/test_post" and method == "POST":
            json_result = '{"result": "created", "id": 42}'
        elif path == "/test_patch" and method == "PATCH":
            json_result = '{"result": "updated", "id": 42, "name": "%s"}' % (
                params.get("name", "") if params else ""
            )
        elif path == "/test_delete" and method == "DELETE":
            json_result = '{"result": "deleted", "id": 42}'
        elif path == "/api/v1/trips.json" and method == "GET":
            page = (params or {}).get("page", 1)
            if page == 1:
                json_result = json.dumps(
                    {
                        "trips": [
                            {"id": 1, "name": "Trip 1"},
                            {"id": 2, "name": "Trip 2"},
                        ],
                        "meta": {
                            "pagination": {
                                "record_count": 3,
                                "page_count": 2,
                                "page_size": 2,
                                "next_page_url": "https://ridewithgps.com/api/v1/trips.json?page=2",
                            }
                        },
                    }
                )
            else:
                json_result = json.dumps(
                    {
                        "trips": [{"id": 3, "name": "Trip 3"}],
                        "meta": {
                            "pagination": {
                                "record_count": 3,
                                "page_count": 2,
                                "page_size": 2,
                                "next_page_url": None,
                            }
                        },
                    }
                )
        elif path == "/users/1/trips.json" and method == "GET":
            offset = (params or {}).get("offset", 0)
            if offset == 0:
                json_result = json.dumps(
                    {
                        "results": [
                            {"id": 101, "name": "Ride 1"},
                            {"id": 102, "name": "Ride 2"},
                        ],
                        "results_count": 3,
                    }
                )
            else:
                json_result = json.dumps(
                    {"results": [{"id": 103, "name": "Ride 3"}], "results_count": 3}
                )
        return self._to_obj(json.loads(json_result))


@pytest.fixture
def client(monkeypatch):
    RideWithGPS.__bases__ = (DummyAPIClient,)
    return RideWithGPS(apikey="dummykey")


@pytest.fixture
def oauth_client(monkeypatch):
    RideWithGPS.__bases__ = (DummyAPIClient,)
    return RideWithGPS(client_id="cid", client_secret="csec")


# ------------------------------------------------------------------
# API key auth
# ------------------------------------------------------------------


def test_authenticate_sets_user_info_and_token(client):
    user = client.authenticate(email="test@example.com", password="pw")
    assert user.id == 1
    assert user.display_name == "Test User"
    assert client.auth_token == "FAKE_TOKEN"


def test_get_returns_python_object(client):
    client.authenticate(email="test@example.com", password="pw")
    rides = client.get(path="/users/1/trips.json", params={"offset": 0, "limit": 2})
    assert hasattr(rides, "results")
    assert isinstance(rides.results, list)
    assert rides.results[0].name == "Ride 1"


def test_put_updates_trip_name(client):
    client.authenticate(email="test@example.com", password="pw")
    response = client.put(path="/trips/123.json", params={"name": "Morning Ride"})
    assert response.trip.name == "Morning Ride"


def test_post_creates_resource(client):
    response = client.post(path="/test_post", params={"foo": "bar"})
    assert response.result == "created"
    assert response.id == 42


def test_patch_updates_resource(client):
    response = client.patch(path="/test_patch", params={"name": "Updated Name"})
    assert response.result == "updated"
    assert response.name == "Updated Name"


def test_delete_removes_resource(client):
    response = client.delete(path="/test_delete", params={"id": 42})
    assert response.result == "deleted"


def test_list_v1_paginates_all_pages(client):
    trips = list(client.list("/api/v1/trips.json", result_key="trips"))
    assert len(trips) == 3
    assert trips[0].name == "Trip 1"
    assert trips[2].name == "Trip 3"


def test_list_v1_respects_limit(client):
    trips = list(client.list("/api/v1/trips.json", result_key="trips", limit=2))
    assert len(trips) == 2
    assert trips[1].name == "Trip 2"


def test_list_legacy_paginates_all_pages(client):
    rides = list(
        client.list("/users/1/trips.json", params={"offset": 0}, result_key="results")
    )
    assert len(rides) == 3
    assert rides[0].name == "Ride 1"
    assert rides[2].name == "Ride 3"


def test_list_legacy_respects_limit(client):
    rides = list(client.list("/users/1/trips.json", result_key="results", limit=1))
    assert len(rides) == 1
    assert rides[0].name == "Ride 1"


def test_authenticate_raises_on_oauth_client(oauth_client):
    with pytest.raises(ValueError, match="API key auth"):
        oauth_client.authenticate(email="x@x.com", password="pw")


# ------------------------------------------------------------------
# OAuth
# ------------------------------------------------------------------


def test_oauth_get_returns_python_object(oauth_client):
    result = oauth_client.get(
        path="/users/1/trips.json", params={"offset": 0, "limit": 2}
    )
    assert result.results[0].name == "Ride 1"


def test_oauth_post_creates_resource(oauth_client):
    result = oauth_client.post(path="/test_post", params={"foo": "bar"})
    assert result.result == "created"


def test_oauth_patch_updates_resource(oauth_client):
    result = oauth_client.patch(path="/test_patch", params={"name": "Updated"})
    assert result.name == "Updated"


def test_oauth_delete_removes_resource(oauth_client):
    result = oauth_client.delete(path="/test_delete", params={"id": 42})
    assert result.result == "deleted"


def test_oauth_list_v1_paginates(oauth_client):
    trips = list(oauth_client.list("/api/v1/trips.json", result_key="trips"))
    assert len(trips) == 3


def test_oauth_list_v1_respects_limit(oauth_client):
    trips = list(oauth_client.list("/api/v1/trips.json", result_key="trips", limit=2))
    assert len(trips) == 2


def test_oauth_list_legacy_paginates(oauth_client):
    rides = list(
        oauth_client.list("/users/1/trips.json", params={}, result_key="results")
    )
    assert len(rides) == 3


def test_oauth_no_version_or_auth_token_injected(oauth_client):
    """OAuth client must not inject version or auth_token query params."""
    oauth_client.get(path="/api/v1/trips.json")
    path, params, method = oauth_client.calls[-1]
    assert "auth_token" not in (params or {})
    assert "version" not in (params or {})


def test_authorization_url_raises_on_apikey_client(client):
    with pytest.raises(ValueError, match="OAuth"):
        client.authorization_url(redirect_uri="https://app.example.com/cb")


def test_init_requires_credentials():
    with pytest.raises(ValueError):
        RideWithGPS()
