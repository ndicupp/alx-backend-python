complete code with the log_queries decorator:
import sqlite3
import functools

#### decorator to log SQL queries

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from keyword arguments
        query = kwargs.get('query', '')
        
        # If query is not in kwargs, check if it's the first positional argument
        if not query and args:
            query = args[0] if isinstance(args[0], str) else ''
        
        # Log the SQL query
        print(f"Executing SQL Query: {query}")
        
        # Call the original function
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")


Alternative simpler version (if you know the function will always receive the query as the first argument):
import sqlite3
import functools

#### decorator to log SQL queries

def log_queries(func):
    @functools.wraps(func)
    def wrapper(query, *args, **kwargs):
        # Log the SQL query
        print(f"Executing SQL Query: {query}")
        
        # Call the original function
        return func(query, *args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")

Key features of the decorator:

Uses functools.wraps to preserve the original function's metadata (name, docstring, etc.)

Extracts the query from either keyword arguments or positional arguments

Logs the query by printing it before execution

Calls the original function with all arguments intact

Returns the result unchanged

When you run this code, it will output:
Executing SQL Query: SELECT * FROM users
The decorator can be easily modified to log to a file, add timestamps, or include additional information if needed.




