
#!/usr/bin/env python3
function construct-memoized-functor (F is a function object parameter)
    allocate a function object called memoized-version;

    let memoized-version(arguments) be
        if self has no attached array values then [self is a reference to this object]
            allocate an associative array called values;
            attach values to self;
        end if;

        if self.values[arguments] is empty then
            self.values[arguments] = F(arguments);
        end if;

        return self.values[arguments];
    end let;

    return memoized-version;
end function

exact test implementation for the memoize decorator, written cleanly and professionally in the same style as your previous tests:
import unittest
from unittest.mock import patch
from utils import memoize  # make sure this import path is correct

class TestMemoize(unittest.TestCase):
    """Unit tests for utils.memoize"""

    def test_memoize(self):
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        test_obj = TestClass()

        with patch.object(TestClass, "a_method", return_value=42) as mock_method:
            # First call → method should be called
            first = test_obj.a_property()
            # Second call → method should NOT be called again (memoized)
            second = test_obj.a_property()

            self.assertEqual(first, 42)
            self.assertEqual(second, 42)

            # Confirm a_method was called only once due to caching
            mock_method.assert_called_once()

if __name__ == "__main__":
    unittest.main()



