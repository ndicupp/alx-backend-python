I'm going to explain a Python script seed.py that sets up the MySQL database and streams rows one by one using a generator:
#!/usr/bin/python3
import mysql.connector
import csv
import uuid
from mysql.connector import Error

def connect_db():
    """Connects to the MySQL database server"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password=''   # Replace with your MySQL password
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Creates the database ALX_prodev if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='ALX_prodev'
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None

def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields"""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,0) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, csv_file_path):
    """Inserts data in the database if it does not exist"""
    try:
        cursor = connection.cursor()
        
        # Read CSV and insert data
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                # Check if user_id already exists
                check_query = "SELECT COUNT(*) FROM user_data WHERE user_id = %s"
                cursor.execute(check_query, (row['user_id'],))
                result = cursor.fetchone()
                
                if result[0] == 0:  # User doesn't exist
                    insert_query = """
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        row['user_id'],
                        row['name'],
                        row['email'],
                        int(row['age'])
                    ))
        
        connection.commit()
        print("Data inserted successfully")
        cursor.close()
    except Error as e:
        print(f"Error inserting data: {e}")
        connection.rollback()

def stream_rows(connection):
    """
    Generator that streams rows from the user_data table one by one
    """
    cursor = None
    try:
        cursor = connection.cursor(buffered=True)
        query = "SELECT user_id, name, email, age FROM user_data"
        cursor.execute(query)
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            
    except Error as e:
        print(f"Error streaming rows: {e}")
    finally:
        if cursor:
            cursor.close()

def stream_rows_batch(connection, batch_size=100):
    """
    Generator that streams rows in batches for better performance
    """
    cursor = None
    try:
        cursor = connection.cursor(buffered=True)
        offset = 0
        
        while True:
            query = "SELECT user_id, name, email, age FROM user_data LIMIT %s OFFSET %s"
            cursor.execute(query, (batch_size, offset))
            
            rows = cursor.fetchall()
            if not rows:
                break
                
            for row in rows:
                yield {
                    'user_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'age': row[3]
                }
            
            offset += batch_size
            
    except Error as e:
        print(f"Error streaming rows: {e}")
    finally:
        if cursor:
            cursor.close()

# Example usage of the generator
if __name__ == "__main__":
    # Setup database (similar to your test script)
    connection = connect_db()
    if connection:
        create_database(connection)
        connection.close()
        print("Connection successful")

        connection = connect_to_prodev()
        if connection:
            create_table(connection)
            insert_data(connection, 'user_data.csv')
            
            # Test the generator
            print("\nStreaming rows one by one:")
            row_count = 0
            for row in stream_rows(connection):
                print(f"Row {row_count + 1}: {row}")
                row_count += 1
                if row_count >= 5:  # Show only first 5 for demo
                    break
            
            print(f"\nTotal rows streamed: {row_count}")
            connection.close()

Key features of this implementation:

Database Setup: Creates the database, table, and inserts data from CSV

Generator Function: stream_rows() yields rows one by one using a cursor

Memory Efficient: Uses buffered cursor to avoid loading all data into memory

Batch Streaming: stream_rows_batch() provides an alternative for large datasets

Error Handling: Proper exception handling and resource cleanup

Usage Example:

# Stream all rows one by one
connection = connect_to_prodev()
for row in stream_rows(connection):
    print(row)
    # Process each row individually
connection.close()

