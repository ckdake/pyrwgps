import os
import pytest
import vcr  # type: ignore
import re
from ridewithgps import RideWithGPS
import logging
import http.client as http_client


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
    ],
    before_record_request=scrub_sensitive_data,
    before_record_response=scrub_sensitive_response,
)


@pytest.mark.integration
@my_vcr.use_cassette("ridewithgps_integration.yaml")
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
    import json

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
