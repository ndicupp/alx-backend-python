a simple decorator that logs the SQL query before executing it. Here’s a clean implementation:
import sqlite3
import functools

# Decorator to log SQL queries
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get('query', None)
        if query:
            print(f"[LOG] Executing SQL query: {query}")
        return func(*args, **kwargs)
    return wrapper

# Example usage
@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
print(users)

How it works:

log_queries checks if the query argument exists and prints it before calling the decorated function.

The original function executes the query normally.

The decorator is lightweight and doesn’t modify the function’s behavior.




