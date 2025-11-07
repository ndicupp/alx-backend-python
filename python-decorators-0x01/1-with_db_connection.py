a decorator that automatically opens a database connection, passes it to the function, and then closes it afterward. Here’s a proper implementation:
import sqlite3
import functools

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open the database connection
        conn = sqlite3.connect("my_database.db")  # change to your DB file
        try:
            # Call the decorated function with the connection as the first argument
            result = func(conn, *args, **kwargs)
        finally:
            # Ensure the connection is closed even if an error occurs
            conn.close()
        return result
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Fetch user by ID with automatic connection handling
user = get_user_by_id(user_id=1)
print(user)

How it works:

The decorator with_db_connection opens a connection.

Passes the conn object to your function.

Closes the connection automatically after the function finishes (even if an error occurs).
