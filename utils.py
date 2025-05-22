import sqlite3
import os
from functools import wraps
from dotenv import load_dotenv


load_dotenv()

def check_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = create_db_connection()
        try:
            result = func(conn, *args, **kwargs)
        finally:
            close_db_connection(conn)
        return result
    return wrapper


def create_db_connection():
    db_name = os.getenv("DB_NAME", "database.db") 
    conn = sqlite3.connect(db_name)
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn


def close_db_connection(conn):
    if conn:
        conn.close()
        print("Database connection closed.")
    else:
        print("No database connection to close.")