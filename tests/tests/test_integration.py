import os
import pytest
import vcr
import re
from ridewithgps import RideWithGPS

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
    headers = response['headers']
    headers = {
        k: v for k, v in headers.items()
        if k.lower() != 'set-cookie'
    }
    response['headers'] = headers
    return response

def unfold_yaml_json_string(s):
    # Remove YAML-inserted newlines and indentation in JSON strings
    if isinstance(s, str):
        # Remove newlines followed by spaces (YAML folded lines)
        return re.sub(r'\n\s+', '', s)
    return s

my_vcr = vcr.VCR(
    cassette_library_dir='tests/cassettes',
    filter_headers=[
        'authorization',
        'set-cookie',
        'cookie',
        'x-csrf-token', 
    ],
    before_record_request=scrub_sensitive_data,
    before_record_response=scrub_sensitive_response,
)

@pytest.mark.integration
@my_vcr.use_cassette('ridewithgps_integration.yaml')
def test_fetch_20_rides():
    username = os.environ.get('RIDEWITHGPS_EMAIL')
    password = os.environ.get('RIDEWITHGPS_PASSWORD')
    apikey   = os.environ.get('RIDEWITHGPS_KEY')

    client = RideWithGPS()
    auth = client.call(
        "/users/current.json", 
        {"email": username, "password": password, "apikey": apikey, "version": 2}
    )
    userid = auth['user']['id']
    auth_token = auth['user']['auth_token']

    rides = client.call(
        f"/users/{userid}/trips.json",
        {"offset": 0, "limit": 20, "apikey": apikey, "version": 2, "auth_token": auth_token}
    )

    # Unfold YAML-folded JSON if needed
    import json
    if isinstance(rides, str):
        rides = unfold_yaml_json_string(rides)
        rides = json.loads(rides)

    assert isinstance(rides, dict)
    assert 'results' in rides
    assert isinstance(rides['results'], list)
    assert len(rides['results']) <= 20