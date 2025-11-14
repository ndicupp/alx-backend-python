#!/usr/bin/env python3
import unittest
from parameterized import parameterized

class AddTestCase(unittest.TestCase):
    @parameterized.expand([
        ("2 and 3", 2, 3, 5),
        ("3 and 5", 3, 5, 8),
    ])
    def test_add(self, _, a, b, expected):
        assert_equal(a + b, expected)
Will create the test cases:

$ nosetests example.py
test_add_0_2_and_3 (example.AddTestCase) ... ok
test_add_1_3_and_5 (example.AddTestCase) ... ok

Ran 2 tests in 0.001s

OK

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient
from utils import get_json   # Only for type reference; patched during test


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient.org"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")  # Patch get_json *inside the client module*
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct data and calls get_json once"""

        # Mock return value (could be anything, test only needs correctness of forwarding)
        mock_get_json.return_value = {"org": org_name}

        client = GithubOrgClient(org_name)
        result = client.org

        # Assertions
        mock_get_json.assert_called_once_with(f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, {"org": org_name})


if __name__ == "__main__":
    unittest.main()

