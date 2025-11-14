unit test for the access_nested_map function to check that it raises a KeyError correctly. Here’s a clean implementation using unittest and parameterized.expand:
import unittest
from parameterized import parameterized
from utils import access_nested_map  # make sure this import is correct

class TestAccessNestedMap(unittest.TestCase):
    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_missing_key):
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        # Check that the KeyError message is the missing key
        self.assertEqual(str(context.exception), repr(expected_missing_key))

Explanation:

parameterized.expand lets us run the same test with multiple inputs.

with self.assertRaises(KeyError) as context captures the exception.

str(context.exception) returns the exception message, which for KeyError is typically the string representation of the missing key, e.g., 'a'.

The test checks that the correct key caused the error.

unit test for utils.get_json that uses unittest.mock.patch to avoid real HTTP calls and verifies both the returned data and that requests:
import unittest
from unittest.mock import patch, Mock
from utils import get_json  # make sure the import path is correct
from parameterized import parameterized

class TestGetJson(unittest.TestCase):
    """Unit tests for utils.get_json"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch("utils.requests.get")  # patch requests.get in the utils module
    def test_get_json(self, test_url, test_payload, mock_get):
        # Setup the mock to return a response with .json() method
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function
        result = get_json(test_url)

        # Assertions
        mock_get.assert_called_once_with(test_url)  # ensure requests.get called once with URL
        self.assertEqual(result, test_payload)      # ensure the function returns the correct payload

if __name__ == "__main__":
    unittest.main()
combine both test classes—TestAccessNestedMap and TestGetJson—into a single, clean tests.py file, fully ready for unittest execution with parameterized tests and mocking:
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json  # adjust imports if needed

class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for utils.access_nested_map"""

    # Test successful retrievals
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    # Test KeyError exceptions
    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_missing_key):
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), repr(expected_missing_key))


class TestGetJson(unittest.TestCase):
    """Unit tests for utils.get_json"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch("utils.requests.get")  # patch requests.get in the utils module
    def test_get_json(self, test_url, test_payload, mock_get):
        # Setup the mock to return a response with .json() method
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function
        result = get_json(test_url)

        # Assertions
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


if __name__ == "__main__":
    unittest.main()


