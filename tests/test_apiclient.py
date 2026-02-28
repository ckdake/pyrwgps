import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
from pyrwgps.apiclient import APIClient


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


class TestAPIClientCaching(unittest.TestCase):
    def setUp(self):
        self.client = APIClient(cache=True)
        self.client.connection_pool = MagicMock()
        self.mock_response = MagicMock()
        # Simulate a paginated API: first call returns 2 items, second 2 more, then empty
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


if __name__ == "__main__":
    unittest.main()
