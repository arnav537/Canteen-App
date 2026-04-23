import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Connects to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Arnavganu@007',
            database='canteen_db'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
