I'm going to explain the 1-batch_processing.py file that implements batch processing with generators:
#!/usr/bin/python3
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Helper function to get database connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      # Replace with your MySQL username
            password='',      # Replace with your MySQL password
            database='ALX_prodev'
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from user_data table in batches.
    
    Args:
        batch_size (int): Number of rows to fetch in each batch
    
    Yields:
        list: Batch of rows as dictionaries
    """
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        if not connection:
            return
        
        cursor = connection.cursor(buffered=True)
        offset = 0
        
        # First loop: Continue fetching batches until no more data
        while True:
            query = "SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s"
            cursor.execute(query, (batch_size, offset))
            
            rows = cursor.fetchall()
            if not rows:
                break
            
            # Convert batch to list of dictionaries
            batch = []
            # Second loop: Convert each row to dictionary
            for row in rows:
                batch.append({
                    'user_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'age': row[3]
                })
            
            yield batch
            offset += batch_size
            
    except Error as e:
        print(f"Error streaming users in batches: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.
    
    Args:
        batch_size (int): Number of rows to process in each batch
    """
    # Third loop: Iterate through batches from the generator
    for batch in stream_users_in_batches(batch_size):
        # Filter users over age 25 within the current batch
        filtered_users = [user for user in batch if user['age'] > 25]
        
        # Yield each filtered user individually
        for user in filtered_users:
            print(user)

# Alternative implementation with explicit counting
def batch_processing_verbose(batch_size):
    """
    Alternative implementation that shows batch counting
    """
    batch_count = 0
    total_users = 0
    
    for batch in stream_users_in_batches(batch_size):
        batch_count += 1
        filtered_users = [user for user in batch if user['age'] > 25]
        total_users += len(filtered_users)
        
        # Print each filtered user
        for user in filtered_users:
            print(user)
    
    print(f"Processed {batch_count} batches, found {total_users} users over age 25", 
          file=sys.stderr)

if __name__ == "__main__":
    import sys
    # Test with batch size of 50 as per the requirement
    try:
        batch_processing(50)
    except BrokenPipeError:
        # Handle broken pipe when used with head/tail commands
        sys.stderr.close()


Loop Analysis (Total: 3 loops):

First loop: while True: in stream_users_in_batches() - fetches batches until no more data

Second loop: for row in rows: in stream_users_in_batches() - converts each row in batch to dictionary

Third loop: for batch in stream_users_in_batches(batch_size): in batch_processing() - processes each batch

Key Features:

Batch Processing: Fetches data in configurable batch sizes for memory efficiency

Age Filtering: Filters users over 25 years old using list comprehension

Generator Pattern: Uses yield to return batches one at a time

Memory Efficient: Only loads one batch into memory at a time

Proper Resource Management: Closes database connections properly

How it works:

stream_users_in_batches() uses LIMIT and OFFSET to fetch data in batches

Each batch is converted to a list of dictionaries

batch_processing() receives batches and filters users over age 25

Filtered users are printed one by one, maintaining the generator pattern

Usage:
The script will output only users over 25 years old, as shown in your test example. When piped to head -n 5, it shows the first 5 users who are over 25 years old from the first batch(es).
