import hashlib
# Assuming this file correctly imports PyMySQL
from database.db_connection import get_connection, ConnectionError
import pymysql.cursors


def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def authenticate_user(username, password):
    """
    Authenticates a user against the 'users' table.
    Returns (success_status: bool, message: str)
    """
    conn = None
    cursor = None

    if not username or not password:
        return False, "Username and password are required."

    try:
        conn = get_connection()
        # Use DictCursor explicitly for PyMySQL to ensure results can be accessed by column name (e.g., user['password_hash'])
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 1. Fetch user by username
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return False, "Invalid username or password."

        # 2. Verify password
        if user['password_hash'] == hash_password(password):
            # Success: Return user data or success status
            # In your login_window handler, you will need to check this boolean
            # return True, f"Login successful for {user['username']}."
            return True, user
        else:
            # Failure: Password mismatch
            return False, "Invalid username or password."

    # 3. Add explicit error handling for robustness
    except ConnectionError as e:
        # Catches connection failures propagated from get_connection()
        return False, f"Database connection error: {e}"

    except Exception as e:
        # Catches all other unexpected SQL or Python errors during the query execution
        print(f"Login Query Error: {e}")
        return False, f"Internal error during authentication: {type(e).__name__}"

    finally:
        # Ensure resources are cleaned up (use .open check for PyMySQL)
        if cursor:
            cursor.close()
        if conn and conn.open:
            conn.close()


def create_user(username, password, full_name, role='staff'):
    """Create a new user with hashed password."""
    # NOTE: You should add try/except blocks here as well for consistency!
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute("""
                       INSERT INTO users (username, password_hash, full_name, role)
                       VALUES (%s, %s, %s, %s)
                       """, (username, hashed, full_name, role))
        conn.commit()
        return True, "User created successfully."
    except Exception as e:
        if conn: conn.rollback()
        return False, f"Failed to create user: {e}"
    finally:
        if conn and conn.open:
            conn.close()