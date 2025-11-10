import pymysql.cursors
import pymysql.err
import os
import sys
import importlib.util
from pathlib import Path
import sqlite3  # <-- ADDED: Import SQLite module


# Define a custom exception to signal connection/config failure to the GUI
class ConnectionError(Exception):
    pass


# --- 1. PYINSTALLER PATH ADAPTER ---

def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for dev and for PyInstaller.
    """
    try:
        # PyInstaller: Use the temporary path
        base_path = sys._MEIPASS
    except Exception:
        # Development: Use the current working directory
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# --- 2. DYNAMIC CONFIG IMPORT ---

CONFIG_FILE_PATH = resource_path(os.path.join("config", "db_config.py"))
DB_CONFIG = {}
LOCAL_DB_PATH = 'local_cache.db'  # Define local cache file

try:
    # Dynamically load the module from its absolute path
    spec = importlib.util.spec_from_file_location("db_config", CONFIG_FILE_PATH)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    DB_CONFIG = config_module.DB_CONFIG
    print("Database configuration loaded successfully.")

except Exception as e:
    error_msg = f"CRITICAL: Failed to load database configuration. Check if 'config/db_config.py' is correctly bundled (Path: {CONFIG_FILE_PATH}). Error: {e}"
    print(error_msg)


# ----------------------------------------------------------------------
# PRIMARY (MYSQL) CONNECTION FUNCTION
# ----------------------------------------------------------------------
def get_connection():
    """Create and return a database connection using PyMySQL."""
    if not DB_CONFIG:
        raise ConnectionError(f"Database configuration not loaded. Check file path: {CONFIG_FILE_PATH}")

    try:
        return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

    except pymysql.err.MySQLError as err:
        # Catch PyMySQL-specific errors (like WinError 10061)
        raise ConnectionError(f"Failed to connect to MariaDB/MySQL database: {err}")


# ----------------------------------------------------------------------
# LOCAL (SQLITE) CONNECTION AND INITIALIZATION
# ----------------------------------------------------------------------

def get_local_connection():
    """Creates and returns a connection to the local SQLite database."""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    return conn


def initialize_local_db():
    """Creates the necessary tables in the local SQLite database if they don't exist."""
    conn = get_local_connection()
    cursor = conn.cursor()

    # Table for offline user authentication
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS local_users
                   (
                       user_id
                       INTEGER
                       PRIMARY
                       KEY,
                       username
                       TEXT
                       NOT
                       NULL
                       UNIQUE,
                       password_hash
                       TEXT
                       NOT
                       NULL,
                       full_name
                       TEXT,
                       role
                       TEXT
                   )
                   """)

    # Table for offline member lookup
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS local_members
                   (
                       member_id
                       INTEGER
                       PRIMARY
                       KEY,
                       membership_card_no
                       TEXT
                       NOT
                       NULL
                       UNIQUE,
                       first_name
                       TEXT,
                       last_name
                       TEXT
                   )
                   """)

    # NEW Table for offline payment history lookup
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS local_membership
                   (
                       member_id
                       INTEGER,
                       payment_year
                       INTEGER,
                       payment_month_num
                       INTEGER,
                       PRIMARY
                       KEY
                   (
                       member_id,
                       payment_year,
                       payment_month_num
                   )
                       )
                   """)

    conn.commit()
    conn.close()


# Automatic Initialization on Import
try:
    initialize_local_db()
except Exception as e:
    print(f"Warning: Failed to initialize local SQLite database: {e}")

# ----------------------------------------------------------------------
# EXISTING FUNCTIONS (WITH OFFLINE PAYMENT FALLBACK)
# ----------------------------------------------------------------------
# Constants for month conversion
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


def get_paid_months_for_year(member_id, year):
    """
    Retrieves paid months for a member. Tries MySQL first, then falls back to SQLite cache.
    """
    paid_month_names = set()
    conn = None
    cursor = None

    try:
        # --- 1. TRY ONLINE (MYSQL) ---
        conn = get_connection()
        cursor = conn.cursor()

        # SQL to select the month number (1-12) from the 'membership' table
        sql = """
              SELECT MONTH (payment_month) AS month_num
              FROM membership
              WHERE member_id = %s \
                AND payment_year = %s \
              """
        params = (member_id, year)
        cursor.execute(sql, params)
        paid_month_numbers = [row['month_num'] for row in cursor.fetchall()]

    except (ConnectionError, pymysql.err.MySQLError):
        # --- 2. FALLBACK OFFLINE (SQLITE) ---
        try:
            conn = get_local_connection()
            cursor = conn.cursor()

            # Query the local cache table
            sql = """
                  SELECT payment_month_num \
                  FROM local_membership
                  WHERE member_id = ? \
                    AND payment_year = ? \
                  """
            params = (member_id, year)
            cursor.execute(sql, params)
            paid_month_numbers = [row[0] for row in cursor.fetchall()]  # SQLite uses tuple indexing

        except Exception as e:
            # If the local DB fails, return empty set
            print(f"Local Database Error fetching paid months: {e}")
            return set()

    except Exception as e:
        print(f"Unhandled Database Error fetching paid months: {e}")
        return set()

    finally:
        if cursor and hasattr(cursor, 'close'):
            cursor.close()
        if conn:
            # Check connection type to close correctly
            if isinstance(conn, pymysql.connections.Connection) and conn.open:
                conn.close()
            elif isinstance(conn, sqlite3.Connection):
                conn.close()

    # Convert month numbers (1-12) to names (Applies to both online/offline results)
    for month_num in paid_month_numbers:
        if 1 <= month_num <= 12:
            paid_month_names.add(MONTH_NAMES[month_num - 1])

    return paid_month_names