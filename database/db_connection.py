import pymysql.cursors
import os
import sys
import importlib.util
from pathlib import Path


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

try:
    # Dynamically load the module from its absolute path
    spec = importlib.util.spec_from_file_location("db_config", CONFIG_FILE_PATH)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    DB_CONFIG = config_module.DB_CONFIG
    print("Database configuration loaded successfully.")

except Exception as e:
    # If config file import fails (the likely PyInstaller issue)
    error_msg = f"CRITICAL: Failed to load database configuration. Check if 'config/db_config.py' is correctly bundled (Path: {CONFIG_FILE_PATH}). Error: {e}"
    print(error_msg)
    # We leave DB_CONFIG empty and let get_connection() raise the error.


# ----------------------------------------------------------------------
# CONNECTION FUNCTION
# ----------------------------------------------------------------------
def get_connection():
    """Create and return a database connection using PyMySQL."""
    if not DB_CONFIG:
        raise ConnectionError(f"Database configuration not loaded. Check file path: {CONFIG_FILE_PATH}")

    try:
        # Use pymysql.connect for reliable bundling
        return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

    except pymysql.err.MySQLError as err:
        # Catch PyMySQL-specific errors
        raise ConnectionError(f"Failed to connect to MariaDB/MySQL database: {err}")


# Constants for month conversion and get_paid_months_for_year (rest of file)
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


def get_paid_months_for_year(member_id, year):
    # ... (function body remains the same, but it now relies on ConnectionError being defined)
    paid_month_names = set()
    conn = None
    cursor = None

    try:
        conn = get_connection()
        # Since get_connection uses DictCursor by default, 'cursor' returns dicts.
        cursor = conn.cursor()

        # SQL to select the month number (1-12) from the 'membership' table
        sql = """
              SELECT MONTH (payment_month) AS month_num -- <-- 1. ADD ALIAS
              FROM membership
              WHERE member_id = %s \
                AND payment_year = %s \
              """
        params = (member_id, year)

        cursor.execute(sql, params)

        # 2. FIX: Access by the new string key 'month_num'
        paid_month_numbers = [row['month_num'] for row in cursor.fetchall()]

        # Convert month numbers (1-12) to names
        for month_num in paid_month_numbers:
            if 1 <= month_num <= 12:
                # Month numbers are 1-based, list index is 0-based
                paid_month_names.add(MONTH_NAMES[month_num - 1])

    except pymysql.connect.Error as e:
        print(f"Database Error fetching paid months for member {member_id}: {e}")
        return set()

    except ConnectionError:
        # Catch the custom error raised by get_connection if config failed
        return set()

    finally:
        if cursor:
            cursor.close()
        if conn and conn.open:
            conn.close()

    return paid_month_names