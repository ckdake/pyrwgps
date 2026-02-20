import os
import json
import pytest
import vcr  # type: ignore
import re
from pyrwgps import RideWithGPS


def scrub_sensitive_data(request):
    import urllib.parse

    url = urllib.parse.urlparse(request.uri)
    query = urllib.parse.parse_qs(url.query)
    for key in ["apikey", "auth_token", "email", "password"]:
        if key in query:
            query[key] = ["DUMMY"]
    new_query = urllib.parse.urlencode(query, doseq=True)
    # Rebuild the URL with the scrubbed query
    new_url = url._replace(query=new_query).geturl()
    request.uri = new_url  # Directly set the uri attribute

    # Scrub credentials from the POST body for the v1 auth endpoint
    body = getattr(request, "body", None) or ""
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="replace")
    if "auth_tokens" in request.uri and body:
        try:
            body_json = json.loads(body)
            if "user" in body_json:
                body_json["user"]["email"] = "DUMMY"
                body_json["user"]["password"] = "DUMMY"
            request.body = json.dumps(body_json)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    return request


def scrub_sensitive_response(response):
    # Normalize and filter out Set-Cookie headers manually
    headers = response["headers"]
    headers = {k: v for k, v in headers.items() if k.lower() != "set-cookie"}
    response["headers"] = headers
    return response


def unfold_yaml_json_string(s):
    # Remove YAML-inserted newlines and indentation in JSON strings
    if isinstance(s, str):
        # Remove newlines followed by spaces (YAML folded lines)
        return re.sub(r"\n\s+", "", s)
    return s


my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes",
    filter_headers=[
        "authorization",
        "set-cookie",
        "cookie",
        "x-csrf-token",
        "x-rwgps-api-key",
        "x-rwgps-auth-token",
    ],
    before_record_request=scrub_sensitive_data,
    before_record_response=scrub_sensitive_response,
)


@pytest.mark.integration
@my_vcr.use_cassette("ridewithgps_fetch_20_rides.yaml")
def test_fetch_20_rides():
    username = os.environ.get("RIDEWITHGPS_EMAIL")
    password = os.environ.get("RIDEWITHGPS_PASSWORD")
    apikey = os.environ.get("RIDEWITHGPS_KEY")

    client = RideWithGPS(apikey=apikey)
    user_info = client.authenticate(email=username, password=password)
    assert (
        user_info is not None
    ), "Authentication failed: check credentials and cassette"
    userid = user_info.id

    rides = client.get(
        path=f"/users/{userid}/trips.json",
        params={"offset": 0, "limit": 20},
    )

    # Unfold YAML-folded JSON if needed
    if isinstance(rides, str):
        rides = unfold_yaml_json_string(rides)
        rides = json.loads(rides)

    # rides should be an object with a 'results' attribute (or dict with 'results' key)
    results = getattr(rides, "results", None)
    if results is None and isinstance(rides, dict):
        results = rides.get("results")

    assert results is not None
    assert isinstance(results, list)
    assert len(results) <= 20


@pytest.mark.integration
@my_vcr.use_cassette("ridewithgps_list_limit_30.yaml")
def test_list_limit_30():
    username = os.environ.get("RIDEWITHGPS_EMAIL")
    password = os.environ.get("RIDEWITHGPS_PASSWORD")
    apikey = os.environ.get("RIDEWITHGPS_KEY")

    client = RideWithGPS(apikey=apikey)
    user_info = client.authenticate(email=username, password=password)
    assert user_info is not None, "Authentication failed: check credentials"

    rides = list(
        client.list(
            path=f"/users/{user_info.id}/trips.json",
            params={},
            limit=30,
        )
    )
    # Should get at most 30 rides
    assert len(rides) <= 30
    # Each ride should have an id and name
    for ride in rides:
        assert hasattr(ride, "id")
        assert hasattr(ride, "name")
