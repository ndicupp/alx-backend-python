a decorator that caches query results in a dictionary so that repeated queries don’t hit the database unnecessarily. Here’s a working implementation including with_db_connection:
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

# Simple cache dictionary
query_cache = {}

# Decorator to cache query results based on the SQL query string
def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print("Using cached result...")
            return query_cache[query]
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        print("Caching result...")
        return result
    return wrapper

# Example usage
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users_again)


How it works:

with_db_connection handles opening/closing the connection.

cache_query stores results of queries in the query_cache dictionary keyed by the SQL string.

If the same query is called again, it returns the cached result instead of hitting the database.
