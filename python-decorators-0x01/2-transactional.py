let me build a transactional decorator that wraps a function call in a try/except block, committing on success and rolling back on error. I'm also going to include my previous with_db_connection decorator so the connection is automatically managed. Here's a complete script:
import sqlite3
import functools

# Decorator to automatically manage DB connections
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("my_database.db")  # change to your DB file
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper

# Decorator to manage transactions
def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()  # commit if function succeeds
            return result
        except Exception as e:
            conn.rollback()  # rollback if any error occurs
            print(f"Transaction rolled back due to error: {e}")
            raise  # re-raise the exception
    return wrapper

# Example usage
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?", 
        (new_email, user_id)
    )

# Update user's email with automatic transaction handling
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')

How it works:

with_db_connection opens/closes the connection.

transactional ensures that any changes are committed if successful or rolled back on error.

The decorators can be combined in any order (here connection first, transaction inside).
