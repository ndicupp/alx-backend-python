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

