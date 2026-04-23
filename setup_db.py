import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Connect to MySQL Server (no specific DB)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Arnavganu@007'
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS canteen_db")
            print("Database 'canteen_db' created or already exists.")
            cursor.close()
            conn.close()
            return True
    except Error as e:
        print(f"Error connecting to MySQL Server: {e}")
        return False

def run_schema():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Arnavganu@007',
            database='canteen_db'
        )
        if conn.is_connected():
            cursor = conn.cursor()
            # Read schema.sql
            with open('canteen_app/schema.sql', 'r') as f:
                schema = f.read()

            # Split statements and execute
            statements = schema.split(';')
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
            
            print("Schema executed successfully.")
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Error as e:
        print(f"Error executing schema: {e}")
        return False

if __name__ == "__main__":
    if create_database():
        run_schema()
