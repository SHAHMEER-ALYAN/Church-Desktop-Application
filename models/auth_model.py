import hashlib
import pymysql.cursors
from PySide6.QtWidgets import QMessageBox

# --- CRITICAL OFFLINE IMPORTS ---
# Import ConnectionError and local connection functions from the dedicated file
from database.db_connection import get_connection, ConnectionError, get_local_connection
# ---------------------------------


def hash_password(password):
    """Hash a password using SHA256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# ----------------------------------------------------
# 🔑 AUTHENTICATION LOGIC
# ----------------------------------------------------

def authenticate_user(username, password):
    """
    Authenticates a user against the primary MySQL table.
    Falls back to local cache if the connection fails.
    Returns (success_status: bool, result_data: dict/str)
    """
    if not username or not password:
        return False, "Username and password are required."

    hashed_password = hash_password(password)

    # 1. --- TRY ONLINE (Primary MySQL) ---
    try:
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user['password_hash'] == hashed_password:
            # On successful login, IMMEDIATELY synchronize ALL necessary data
            sync_all_data()
            return True, user

        return False, "Invalid username or password."

    except ConnectionError:
        # 2. --- FALLBACK OFFLINE (SQLite Cache) ---

        QMessageBox.information(None, "Status",
                                "Primary database offline. Attempting offline login...")

        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()

        local_cursor.execute("""
            SELECT user_id, username, password_hash, full_name, role
            FROM local_users WHERE username = ?
        """, (username,))

        local_user_tuple = local_cursor.fetchone()
        local_conn.close()

        if local_user_tuple:
            user = {
                'user_id': local_user_tuple[0],
                'username': local_user_tuple[1],
                'password_hash': local_user_tuple[2],
                'full_name': local_user_tuple[3],
                'role': local_user_tuple[4],
                'status': 'OFFLINE'
            }

            if user['password_hash'] == hashed_password:
                QMessageBox.information(None, "Login Success", "Offline login successful!")
                return True, user

        # Failed both online and local cache check
        return False, "Invalid username or password (user not cached locally)."

    except Exception as e:
        QMessageBox.critical(None, "Authentication Error", f"Internal authentication error: {e}")
        return False, "Internal application error."


# ----------------------------------------------------
# 🔄 SYNCHRONIZATION FUNCTIONS (CRITICAL FOR OFFLINE)
# ----------------------------------------------------

def sync_local_users():
    """Pulls active users from MySQL and caches them locally for offline login."""
    try:
        # 1. Fetch from MySQL
        remote_conn = get_connection()
        remote_cursor = remote_conn.cursor(pymysql.cursors.DictCursor)

        remote_cursor.execute("""
            SELECT user_id, username, password_hash, full_name, role 
            FROM users 
        """)
        users = remote_cursor.fetchall()
        remote_conn.close()

        # 2. Insert/Update Local SQLite Cache
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()

        local_cursor.executemany("""
            REPLACE INTO local_users (user_id, username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        """, [(u['user_id'], u['username'], u['password_hash'], u['full_name'], u['role']) for u in users])

        local_conn.commit()
        local_conn.close()

    except ConnectionError:
        # If the sync fails, we silently skip user cache update.
        pass

    except Exception as e:
        QMessageBox.warning(None, "Synchronization Error",
                            f"Could not sync user cache. Error: {e}")


def sync_local_members():
    """Pulls basic member data from MySQL and caches them locally for offline member lookup."""
    try:
        # 1. Fetch from MySQL
        remote_conn = get_connection()
        remote_cursor = remote_conn.cursor(pymysql.cursors.DictCursor)

        remote_cursor.execute("""
            SELECT member_id, membership_card_no, first_name, last_name 
            FROM members 
        """)
        members = remote_cursor.fetchall()
        remote_conn.close()

        # 2. Insert/Update Local SQLite Cache
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()

        local_cursor.executemany("""
            REPLACE INTO local_members (member_id, membership_card_no, first_name, last_name)
            VALUES (?, ?, ?, ?)
        """, [(m['member_id'], m['membership_card_no'], m['first_name'], m['last_name']) for m in members])

        local_conn.commit()
        local_conn.close()

    except ConnectionError:
        # If the sync fails, we silently skip member cache update.
        pass

    except Exception as e:
        QMessageBox.warning(None, "Synchronization Error",
                            f"Could not sync member cache. Error: {e}")

def sync_local_payments():
    """Pulls ALL payment records from MySQL and caches them locally."""
    try:
        # 1. Fetch from MySQL
        remote_conn = get_connection()
        remote_cursor = remote_conn.cursor(pymysql.cursors.DictCursor)

        # Select member_id, the year, and the numeric month (1-12)
        remote_cursor.execute("""
            SELECT member_id, payment_year, MONTH(payment_month) AS payment_month_num
            FROM membership 
        """)
        payments = remote_cursor.fetchall()
        remote_conn.close()

        # 2. Insert/Update Local SQLite Cache
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()

        # Clear existing payment data to ensure fresh sync (optional, but safer)
        local_cursor.execute("DELETE FROM local_membership")

        local_cursor.executemany("""
            REPLACE INTO local_membership (member_id, payment_year, payment_month_num)
            VALUES (?, ?, ?)
        """, [(p['member_id'], p['payment_year'], p['payment_month_num']) for p in payments])

        local_conn.commit()
        local_conn.close()

    except ConnectionError:
        # If the sync fails, we silently skip payment cache update.
        pass

    except Exception as e:
        QMessageBox.warning(None, "Synchronization Error",
                            f"Could not sync payment cache. Error: {e}")


def sync_all_data():
    """Wrapper to run all synchronization routines."""
    sync_local_users()
    sync_local_members()
    sync_local_payments() # <-- CRITICAL: Include payment sync here


# ----------------------------------------------------
# ➕ USER CREATION
# ----------------------------------------------------

def create_user(username, password, full_name, role='staff'):
    """Create a new user with hashed password."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        hashed = hash_password(password)
        cursor.execute("""
                       INSERT INTO users (username, password_hash, full_name, role)
                       VALUES (%s, %s, %s, %s)
                       """, (username, hashed, full_name, role))
        conn.commit()

        # If successful, trigger a quick sync to update the local cache
        sync_all_data()

        return True, "User created successfully."
    except ConnectionError:
        # Cannot create user if offline
        return False, "Cannot create user: Primary database is offline."
    except Exception as e:
        if conn: conn.rollback()
        return False, f"Failed to create user: {e}"
    finally:
        if conn and conn.open:
            conn.close()