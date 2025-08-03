#!/usr/bin/env python3
"""
Integration tests for PATCH functionality to verify that pyrwgps generates
correct request structures matching working examples.
"""

import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
from pyrwgps.ridewithgps import RideWithGPS


class TestPatchIntegration(unittest.TestCase):
    """Integration tests for PATCH request functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = RideWithGPS(apikey="test_api_key")

        # Mock the connection pool to capture the call details
        self.mock_pool = MagicMock()
        self.client.connection_pool = self.mock_pool

        # Mock response
        self.mock_response = MagicMock()
        self.mock_response.data = b'{"trip": {"id": 284579245, "gear_id": 254097}}'
        self.mock_pool.urlopen.return_value = self.mock_response

    def test_patch_request_structure_matches_working_example(self):
        """Test that pyrwgps generates the same request structure as working requests example."""

        # Make the PATCH call exactly like the real-world usage
        response = self.client.patch(
            path="/trips/284579245",
            params={
                "trip": {
                    "gear_id": 254097,
                }
            },
        )

        # Capture the call details
        call_args = self.mock_pool.urlopen.call_args
        method = call_args[0][0]
        url = call_args[0][1]
        kwargs = call_args[1]

        # Verify the structure matches expectations from working requests example
        self.assertEqual(method, "PATCH", f"Expected PATCH, got {method}")
        self.assertIn("/trips/284579245", url, f"URL should contain trip ID: {url}")
        self.assertIn("apikey=", url, f"URL should contain apikey: {url}")

        headers = kwargs.get("headers", {})
        self.assertEqual(
            headers.get("Content-Type"),
            "application/json",
            f"Wrong content type: {headers}",
        )

        # Verify JSON body content
        self.assertIn("body", kwargs, "Request should have a body")
        body_data = json.loads(kwargs["body"].decode("utf-8"))
        self.assertEqual(
            body_data, {"trip": {"gear_id": 254097}}, f"Wrong body data: {body_data}"
        )

        # Verify response parsing works
        self.assertTrue(hasattr(response, "trip"))
        self.assertEqual(response.trip.id, 284579245)
        self.assertEqual(response.trip.gear_id, 254097)

    def test_patch_with_auth_token_separates_parameters_correctly(self):
        """Test that auth_token goes in URL query string, not JSON body."""

        # Simulate authenticated user
        self.client.auth_token = "fake_auth_token"

        response = self.client.patch(
            path="/trips/284579245",
            params={
                "trip": {
                    "name": "Updated Trip Name",
                    "description": "Updated description",
                }
            },
        )

        # Capture the call details
        call_args = self.mock_pool.urlopen.call_args
        url = call_args[0][1]
        kwargs = call_args[1]

        # Verify auth_token is in URL, not JSON body
        self.assertIn(
            "auth_token=fake_auth_token",
            url,
            "auth_token should be in URL query string",
        )
        self.assertIn("version=2", url, "version should be in URL query string")

        # Verify JSON body only contains trip data
        body_data = json.loads(kwargs["body"].decode("utf-8"))
        expected_body = {
            "trip": {"name": "Updated Trip Name", "description": "Updated description"}
        }
        self.assertEqual(
            body_data,
            expected_body,
            "JSON body should only contain trip data, not auth params",
        )

        # Verify auth parameters are NOT in JSON body
        self.assertNotIn("auth_token", body_data)
        self.assertNotIn("version", body_data)

    def test_patch_gear_setting_real_world_scenario(self):
        """Test the exact scenario from the real-world gear setting use case."""

        # This matches the exact structure from the failing code
        gear_data = {"trip": {"gear_id": int(254097)}}

        response = self.client.patch(path="/trips/284579245", params=gear_data)

        # Verify the request structure
        call_args = self.mock_pool.urlopen.call_args
        method = call_args[0][0]
        url = call_args[0][1]
        kwargs = call_args[1]

        # Should match the working requests.patch structure
        self.assertEqual(method, "PATCH")
        self.assertIn("apikey=test_api_key", url)
        self.assertIn("version=2", url)

        headers = kwargs.get("headers", {})
        self.assertEqual(headers.get("Content-Type"), "application/json")

        # Body should contain exactly the gear data
        body_data = json.loads(kwargs["body"].decode("utf-8"))
        self.assertEqual(body_data, {"trip": {"gear_id": 254097}})

        # Verify response handling
        self.assertTrue(hasattr(response, "trip"))

    def test_patch_handles_empty_response_gracefully(self):
        """Test that PATCH requests handle empty responses (common for successful operations)."""

        # Mock an empty response (realistic for successful PATCH operations)
        self.mock_response.data = b""
        self.mock_pool.urlopen.return_value = self.mock_response

        # This should not raise an exception
        response = self.client.patch(
            path="/trips/284579245",
            params={
                "trip": {
                    "gear_id": 254097,
                }
            },
        )

        # Should return an empty SimpleNamespace object
        self.assertIsNotNone(response)
        self.assertIsInstance(response, SimpleNamespace)
        # Empty responses should result in an object with no attributes
        self.assertEqual(len(vars(response)), 0)

    def test_patch_handles_non_json_response_gracefully(self):
        """Test that PATCH requests handle non-JSON responses gracefully."""

        # Mock a simple text response (some APIs return plain text for successful operations)
        self.mock_response.data = b"OK"
        self.mock_pool.urlopen.return_value = self.mock_response

        # This should not raise an exception
        response = self.client.patch(
            path="/trips/284579245",
            params={
                "trip": {
                    "name": "Updated Name",
                }
            },
        )

        # Should return a SimpleNamespace object with the response text
        self.assertIsNotNone(response)
        self.assertIsInstance(response, SimpleNamespace)
        self.assertTrue(hasattr(response, "response_text"))
        self.assertEqual(response.response_text, "OK")


if __name__ == "__main__":
    unittest.main()
