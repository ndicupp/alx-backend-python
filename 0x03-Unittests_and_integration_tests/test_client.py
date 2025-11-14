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



Thing().foo_one()

Thing().foo_two()

value

