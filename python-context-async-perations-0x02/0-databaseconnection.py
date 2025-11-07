Here’s a class-based context manager that handles opening and closing a database connection automatically:
import sqlite3

# Class-based context manager for database connections
class DatabaseConnection:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def __enter__(self):
        # Open the connection
        self.conn = sqlite3.connect(self.db_file)
        return self.conn  # This will be assigned to the variable after 'as'

    def __exit__(self, exc_type, exc_value, traceback):
        # Close the connection, even if an exception occurred
        if self.conn:
            self.conn.close()
        # Returning False will propagate exceptions (good for debugging)
        return False

# Using the context manager with 'with' statement
with DatabaseConnection('users.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print(results)

How it works:

__enter__ opens the connection and returns it to the with statement.

__exit__ ensures the connection is closed when exiting the block, even if an error occurs.

You can now safely perform queries without manually opening/closing the connection.
