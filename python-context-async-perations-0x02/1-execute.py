a reusable class-based context manager that executes a query and returns the results, handling both connection and execution automatically. Here’s a clean implementation:
import sqlite3

# Context manager that executes a query automatically
class ExecuteQuery:
    def __init__(self, db_file, query, params=None):
        self.db_file = db_file
        self.query = query
        self.params = params or ()
        self.conn = None
        self.results = None

    def __enter__(self):
        # Open connection
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        # Execute query with parameters
        cursor.execute(self.query, self.params)
        # Fetch results
        self.results = cursor.fetchall()
        return self.results  # returned to the 'as' variable

    def __exit__(self, exc_type, exc_value, traceback):
        # Close connection
        if self.conn:
            self.conn.close()
        # Propagate exceptions if any
        return False

# Using the context manager
query = "SELECT * FROM users WHERE age > ?"
params = (25,)

with ExecuteQuery('users.db', query, params) as results:
    print(results)

How it works:

__init__ stores the database file, query, and parameters.

__enter__ opens the connection, executes the query, fetches results, and returns them.

__exit__ ensures the connection is closed, even if an exception occurs.

The context manager is reusable for any query with parameters, not just this example.
