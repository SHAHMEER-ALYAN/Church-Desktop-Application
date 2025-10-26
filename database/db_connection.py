import mysql.connector
from config.db_config import DB_CONFIG

def get_connection():
    """Create and return a MySQL database connection."""
    return mysql.connector.connect(**DB_CONFIG)
