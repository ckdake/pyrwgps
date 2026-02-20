import unittest
import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from pyrwgps.apiclient import APIClient, APIClientSharedSecret


class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_request_get(self):
        # Patch the connection_pool to avoid real HTTP calls
        self.client.connection_pool = MagicMock()
        mock_response = MagicMock()
        mock_response.data = b'{"result": "success"}'
        self.client.connection_pool.urlopen.return_value = mock_response

        result = self.client.call(path="/test/path", params={"foo": "bar"})
        self.assertEqual(result, SimpleNamespace(result="success"))
        self.client.connection_pool.urlopen.assert_called_once_with(
            "GET", "https://ridewithgps.com/test/path?foo=bar", headers={}
        )


class TestAPIClientSharedSecret(unittest.TestCase):
    def test_compose_url_includes_api_key(self):
        client = APIClientSharedSecret(apikey="abc123")
        client.connection_pool = MagicMock()
        mock_response = MagicMock()
        mock_response.data = b'{"ok": true}'
        client.connection_pool.urlopen.return_value = mock_response

        with patch("pyrwgps.apiclient.json.loads", return_value={"ok": True}):
            result = client.call(path="/endpoint", params={"foo": "bar"})
            print(result)
            self.assertEqual(result, SimpleNamespace(ok=True))
            expected_url = "https://ridewithgps.com/endpoint?apikey=abc123&foo=bar"
            client.connection_pool.urlopen.assert_called_once_with(
                "GET", expected_url, headers={"x-rwgps-api-key": "abc123"}
            )


class TestAPIClientCaching(unittest.TestCase):
    def setUp(self):
        self.client = APIClient(cache=True)
        self.client.connection_pool = MagicMock()
        self.mock_response = MagicMock()
        # Simulate a paginated API: first call returns 2 items, second call returns 2 more, then empty
        self.responses = [
            b'{"results": [{"id": 1}, {"id": 2}], "results_count": 4}',
            b'{"results": [{"id": 3}, {"id": 4}], "results_count": 4}',
            b'{"results": [], "results_count": 4}',
        ]
        self.urlopen_calls = []

        def urlopen_side_effect(method, url, **kwargs):
            self.urlopen_calls.append(url)
            # Return the correct response based on offset in the URL
            if "offset=0" in url:
                self.mock_response.data = self.responses[0]
            elif "offset=2" in url:
                self.mock_response.data = self.responses[1]
            else:
                self.mock_response.data = self.responses[2]
            return self.mock_response

        self.client.connection_pool.urlopen.side_effect = urlopen_side_effect

    def test_cache_behavior(self):
        # First: fetch with limit=2 (should hit offset=0 only)
        result1 = self.client.call(path="/trips.json", params={"offset": 0, "limit": 2})
        self.assertEqual([r.id for r in result1.results], [1, 2])
        self.assertEqual(len(self.urlopen_calls), 1)
        self.assertIn("offset=0", self.urlopen_calls[0])

        # Second: fetch with limit=4 (should hit offset=0 and offset=2)
        self.urlopen_calls.clear()
        result2_page1 = self.client.call(
            path="/trips.json", params={"offset": 0, "limit": 2}
        )
        result2_page2 = self.client.call(
            path="/trips.json", params={"offset": 2, "limit": 2}
        )
        self.assertEqual([r.id for r in result2_page1.results], [1, 2])
        self.assertEqual([r.id for r in result2_page2.results], [3, 4])
        # Only the second call (offset=2) should trigger a real HTTP call, offset=0 should be cached
        self.assertEqual(len(self.urlopen_calls), 1)
        self.assertIn("offset=2", self.urlopen_calls[0])

        # Results should be the same as expected
        self.assertEqual(
            [r.id for r in result2_page1.results + result2_page2.results], [1, 2, 3, 4]
        )


class TestAPIClientPatchWithJSON(unittest.TestCase):
    def setUp(self):
        self.client = APIClientSharedSecret(apikey="test123")
        # Create a proper mock for the connection pool
        self.mock_pool = MagicMock()
        self.client.connection_pool = self.mock_pool

        self.mock_response = MagicMock()
        self.mock_response.data = (
            b'{"trip": {"id": 12345, "name": "Union County Hiking"}}'
        )
        self.mock_pool.urlopen.return_value = self.mock_response

    def test_patch_sends_json_body_with_content_type(self):
        """Test that PATCH requests send JSON data in body with correct content type."""
        trip_data = {
            "trip": {
                "name": "Union County Hiking",
                "description": "",
                "visibility": 2,
                "gear_id": 254097,
                "activity_type": "walking:hiking",
            }
        }

        result = self.client.call(path="/trips/12345", params=trip_data, method="PATCH")

        # Verify the response
        self.assertEqual(result.trip.name, "Union County Hiking")

        # Verify the HTTP call was made correctly
        self.mock_pool.urlopen.assert_called_once()
        call_args = self.mock_pool.urlopen.call_args

        # Check method
        self.assertEqual(call_args[0][0], "PATCH")

        # Check URL (should include API key but no trip data)
        url = call_args[0][1]
        self.assertIn("/trips/12345", url)
        self.assertIn("apikey=test123", url)
        self.assertNotIn("Union%20County", url)  # Trip data should NOT be in URL

        # Check that JSON body and headers were passed
        kwargs = call_args[1]
        self.assertIn("body", kwargs)
        self.assertIn("headers", kwargs)

        # Verify Content-Type header
        headers = kwargs["headers"]
        self.assertEqual(headers["Content-Type"], "application/json")

        # Verify JSON body content
        body_data = json.loads(kwargs["body"].decode("utf-8"))
        self.assertEqual(body_data["trip"]["name"], "Union County Hiking")
        self.assertEqual(body_data["trip"]["gear_id"], 254097)
        self.assertEqual(body_data["trip"]["activity_type"], "walking:hiking")

    def test_patch_gear_id_real_world_example(self):
        """Test PATCH request for setting gear_id like the real world example."""
        gear_data = {
            "trip": {
                "gear_id": 254097,
            }
        }

        result = self.client.call(
            path="/trips/284579245", params=gear_data, method="PATCH"
        )

        # Verify the response
        self.assertEqual(result.trip.name, "Union County Hiking")

        # Verify the HTTP call was made correctly
        self.mock_pool.urlopen.assert_called_once()
        call_args = self.mock_pool.urlopen.call_args

        # Check method
        self.assertEqual(call_args[0][0], "PATCH")

        # Check URL matches the real-world pattern
        url = call_args[0][1]
        self.assertIn("/trips/284579245", url)
        self.assertIn("apikey=test123", url)

        # Check that JSON body and headers were passed
        kwargs = call_args[1]
        self.assertIn("body", kwargs)
        self.assertIn("headers", kwargs)

        # Verify Content-Type header
        headers = kwargs["headers"]
        self.assertEqual(headers["Content-Type"], "application/json")

        # Verify JSON body content matches the exact structure
        body_data = json.loads(kwargs["body"].decode("utf-8"))
        self.assertEqual(body_data["trip"]["gear_id"], 254097)
        self.assertEqual(len(body_data["trip"]), 1)  # Only gear_id should be present


if __name__ == "__main__":
    unittest.main()
