import sqlite3
import logging
from functools import wraps
from config import DB_PATH
from helpers import api_response  

def with_db_connection(func):
    """
    description:
        Decorator for database operations:
        - Opens a SQLite connection,
        - Passes it as the first argument to the function,
        - Commits changes,
        - Closes the connection after execution,
        - Logs successful operations and errors in English.
    return:
        If successful, returns the result of the decorated function.
        If an error occurs, returns a dict: {"success": False, "message": "..."}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute('PRAGMA foreign_keys = ON;')
            logging.debug("Database connection opened.")
            result = func(conn, *args, **kwargs)
            conn.commit()
            logging.info("Database operation completed successfully.")
            return result
        except Exception as e:
            logging.error(f"Database error: {e}")
            return api_response(False, f"Database error: {str(e)}", 500, "error")
        finally:
            if conn:
                conn.close()
                logging.debug("Database connection closed.")
    return wrapper
