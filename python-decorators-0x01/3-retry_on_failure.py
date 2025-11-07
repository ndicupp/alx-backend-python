retry_on_failure decorator that retries a database operation a few times if it fails due to transient errors. Here’s a full working example including your with_db_connection decorator:
import time
import sqlite3
import functools

# Decorator to automatically manage DB connections
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("my_database.db")  # change to your DB file
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

# Decorator to retry on failure
def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
            # If all retries fail, raise the last exception
            raise last_exception
        return wrapper
    return decorator

# Example usage
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)


How it works:

with_db_connection manages opening/closing the database.

retry_on_failure attempts the operation multiple times if an exception occurs, waiting delay seconds between retries.

If all retries fail, it raises the last exception.
