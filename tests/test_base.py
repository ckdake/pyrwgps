import unittest
from unittest.mock import patch, MagicMock
from ridewithgps.base import APIClient, APIClient_SharedSecret


class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_request_get(self):
        # Patch the connection_pool to avoid real HTTP calls
        self.client.connection_pool = MagicMock()
        mock_response = MagicMock()
        mock_response.data = b'{"result": "success"}'
        self.client.connection_pool.urlopen.return_value = mock_response

        result = self.client.call("test/path", params={"foo": "bar"})
        self.assertEqual(result, {"result": "success"})
        self.client.connection_pool.urlopen.assert_called_once_with(
            "GET", "http://localhost:5000/test/path?foo=bar"
        )


class TestAPIClientSharedSecret(unittest.TestCase):
    def test_compose_url_includes_api_key(self):
        client = APIClient_SharedSecret(api_key="abc123")
        client.connection_pool = MagicMock()
        mock_response = MagicMock()
        mock_response.data = b'{"ok": true}'
        client.connection_pool.urlopen.return_value = mock_response

        with patch("ridewithgps.base.json.loads", return_value={"ok": True}):
            result = client.call("endpoint", params={"foo": "bar"})
            self.assertEqual(result, {"ok": True})
            expected_url = "http://localhost:5000/endpoint?key=abc123&foo=bar"
            client.connection_pool.urlopen.assert_called_once_with("GET", expected_url)


if __name__ == "__main__":
    unittest.main()
