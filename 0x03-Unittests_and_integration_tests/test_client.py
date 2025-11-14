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

Explanation
🔹 1. Why @patch("client.get_json")?

Because the class uses:
    from utils import get_json
inside client.py, so we MUST patch the function in the module where it is used, not where it is defined.

🔹 2. @parameterized.expand([...])

Runs the test twice:

with "google"

with "abc"

🔹 3. Test logic

A GithubOrgClient(org_name) instance is created.

Accessing .org triggers a call to get_json(...).

We ensure:

get_json was called exactly once

It was called with the correct URL

The return value is ** forwarded correctly** from the mock value

🔹 4. No real HTTP calls

Because get_json is fully mocked.

python
class MyClass:
    @property
    def last_transaction(self):
        # an expensive and complicated DB query here
        pass
In the test suite:

python
def test():
    # Make sure you patch on MyClass, not on a MyClass instance, otherwise
    # you'll get an AttributeError, because mock is using settattr and
    # last_transaction is a readonly property so there's no setter.
    with mock.patch(MyClass, 'last_transaction') as mock_last_transaction:
        mock_last_transaction.__get__ = mock.Mock(return_value=Transaction())
        myclass = MyClass()
        print myclass.last_transaction

@patch('__main__.SomeClass')
def function(normal_argument, mock_class):
    print(mock_class is SomeClass)

function(None)
class Class:
    def method(self):
        pass

with patch('__main__.Class') as MockClass:
    instance = MockClass.return_value
    instance.method.return_value = 'foo'
    assert Class() is instance
    assert Class().method() == 'foo'

    Original = Class
patcher = patch('__main__.Class', spec=True)
MockClass = patcher.start()
instance = MockClass()
assert isinstance(instance, Original)
patcher.stop()

foo = {}
with patch.dict(foo, {'newkey': 'newvalue'}) as patched_foo:
    assert foo == {'newkey': 'newvalue'}
    assert patched_foo == {'newkey': 'newvalue'}
    # You can add, update or delete keys of foo (or patched_foo, it's the same dict)
    patched_foo['spam'] = 'eggs'

assert foo == {}
assert patched_foo == {}
import os
with patch.dict('os.environ', {'newkey': 'newvalue'}):
    print(os.environ['newkey'])


assert 'newkey' not in os.environ
mymodule = MagicMock()
mymodule.function.return_value = 'fish'
with patch.dict('sys.modules', mymodule=mymodule):
    import mymodule
    mymodule.function('some', 'args')


    patch.TEST_PREFIX = 'foo'
value = 3

@patch('__main__.value', 'not three')
class Thing:
    def foo_one(self):
        print(value)
    def foo_two(self):
        print(value)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Unit-test GithubOrgClient.public_repos"""

        # Mock payload returned by get_json
        mock_get_json.return_value = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]

        # Expected final repo list
        expected_repos = ["repo1", "repo2", "repo3"]

        # Mock _public_repos_url to return a fake URL
        with patch.object(GithubOrgClient, "_public_repos_url", new_callable=property) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/testorg/repos"

            client = GithubOrgClient("testorg")
            repos = client.public_repos()

            # Assertions
            self.assertEqual(repos, expected_repos)

            # Ensure _public_repos_url property was accessed exactly once
            mock_url.assert_called_once()

            # Ensure get_json was called exactly once with the fake URL
            mock_get_json.assert_called_once_with("https://api.github.com/orgs/testorg/repos")
Explanation
✔ Mock get_json via decorator

@patch("client.get_json") ensures no actual HTTP calls happen and we fully control returned API data.

✔ Mock _public_repos_url using a context manager

You must patch it as a property, because in the implementation it is typically used as:
self._public_repos_url
so we use
patch.object(GithubOrgClient, "_public_repos_url", new_callable=property)

Only repo names are returned

Since public_repos() extracts "name", the output becomes:
["repo1", "repo2", "repo3"]

# test_math.py
from nose.tools import assert_equal
from parameterized import parameterized, parameterized_class

import unittest
import math

@parameterized([
    (2, 2, 4),
    (2, 3, 8),
    (1, 9, 1),
    (0, 9, 0),
])
def test_pow(base, exponent, expected):
   assert_equal(math.pow(base, exponent), expected)

class TestMathUnitTest(unittest.TestCase):
   @parameterized.expand([
       ("negative", -1.5, -2.0),
       ("integer", 1, 1.0),
       ("large fraction", 1.6, 1),
   ])
   def test_floor(self, name, input, expected):
       assert_equal(math.floor(input), expected)

@parameterized_class(('a', 'b', 'expected_sum', 'expected_product'), [
   (1, 2, 3, 2),
   (5, 5, 10, 25),
])
class TestMathClass(unittest.TestCase):
   def test_add(self):
      assert_equal(self.a + self.b, self.expected_sum)

   def test_multiply(self):
      assert_equal(self.a * self.b, self.expected_product)

@parameterized_class([
   { "a": 3, "expected": 2 },
   { "b": 5, "expected": -4 },
])
class TestMathClassDict(unittest.TestCase):
   a = 1
   b = 1

   def test_subtract(self):
      assert_equal(self.a - self.b, self.expected)
With nose (and nose2):

$ nosetests -v test_math.py
test_floor_0_negative (test_math.TestMathUnitTest) ... ok
test_floor_1_integer (test_math.TestMathUnitTest) ... ok
test_floor_2_large_fraction (test_math.TestMathUnitTest) ... ok
test_math.test_pow(2, 2, 4, {}) ... ok
test_math.test_pow(2, 3, 8, {}) ... ok
test_math.test_pow(1, 9, 1, {}) ... ok
test_math.test_pow(0, 9, 0, {}) ... ok
test_add (test_math.TestMathClass_0) ... ok
test_multiply (test_math.TestMathClass_0) ... ok
test_add (test_math.TestMathClass_1) ... ok
test_multiply (test_math.TestMathClass_1) ... ok
test_subtract (test_math.TestMathClassDict_0) ... ok

Ran 12 tests in 0.015s

from parameterized import parameterized

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Unit-test GithubOrgClient.has_license"""
        client = GithubOrgClient("testorg")
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected)
from parameterized import parameterized, param

# A list of tuples
@parameterized([
    (2, 3, 5),
    (3, 5, 8),
])
def test_add(a, b, expected):
    assert_equal(a + b, expected)

# A list of params
@parameterized([
    param("10", 10),
    param("10", 16, base=16),
])
def test_int(str_val, expected, base=10):
    assert_equal(int(str_val, base=base), expected)

# An iterable of params
@parameterized(
    param.explicit(*json.loads(line))
    for line in open("testcases.jsons")
)
def test_from_json_file(...):
    ...

# A callable which returns a list of tuples
def load_test_cases():
    return [
        ("test1", ),
        ("test2", ),
    ]
@parameterized(load_test_cases)
def test_from_function(name):
    ...

    

