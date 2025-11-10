import pymysql.cursors
from PySide6.QtWidgets import QMessageBox

# Assuming these files provide the necessary custom exception and connection logic
from database.db_connection import get_connection, ConnectionError
from database.local_db import get_local_connection


# ----------------------------------------------------
# 🔄 SYNCHRONIZATION FUNCTION
# ----------------------------------------------------

def sync_local_members():
    """
    Pulls essential member data from the primary MySQL database and
    caches them locally in SQLite for offline lookup.
    """
    try:
        # 1. Fetch from MySQL
        remote_conn = get_connection()
        # Use DictCursor explicitly for reliable data access
        remote_cursor = remote_conn.cursor(pymysql.cursors.DictCursor)

        remote_cursor.execute("""
                              SELECT member_id, membership_card_no, first_name, last_name
                              FROM members
                              WHERE status = 'active'
                                 OR status = 'Active'
                              """)
        members = remote_cursor.fetchall()
        remote_conn.close()

        # 2. Insert/Update Local SQLite Cache
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()

        # Use REPLACE INTO for both inserting new members and updating existing ones
        local_cursor.executemany("""
                                 REPLACE
                                 INTO local_members (member_id, membership_card_no, first_name, last_name)
            VALUES (?, ?, ?, ?)
                                 """,
                                 [(m['member_id'], m['membership_card_no'], m['first_name'], m['last_name']) for m in
                                  members])

        local_conn.commit()
        local_conn.close()
        # QMessageBox.information(None, "Sync Complete", "Member cache synchronized.")
        # Removed message box to prevent unnecessary popups on every start

    except ConnectionError:
        # Expected failure if the application starts offline
        pass

    except Exception as e:
        # Unxpected errors during the sync process
        QMessageBox.warning(None, "Synchronization Error",
                            f"Could not sync member cache (offline data might be stale). Error: {e}")


# ----------------------------------------------------
# CORE MEMBER CHECK AND ADDITION
# ----------------------------------------------------

def member_exists(email, phone, nic_no, membership_card_no):
    """
    Checks if a member with the same email, phone, NIC, or membership card
    already exists. Returns True if found, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT COUNT(*)
                       FROM members
                       WHERE email = %s
                          OR phone = %s
                          OR nic_no = %s
                          OR membership_card_no = %s
                       """, (email, phone, nic_no, membership_card_no))
        # Ensure we fetch the count correctly from the tuple result
        (count,) = cursor.fetchone()
        return count > 0
    except Exception as e:
        print(f"Database error during member existence check: {e}")
        return False
    finally:
        if conn:
            conn.close()


def add_member(first_name, last_name, email, phone, dob, join_date, nic_no, membership_card_no, status="active"):
    """
    Adds a new member to the database if they don't already exist.
    Returns (success_status: bool, message: str).
    """
    if member_exists(email, phone, nic_no, membership_card_no):
        return False, "Member with same Email, Phone, NIC, or Membership Card already exists."

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
                INSERT INTO members (first_name, last_name, email, phone, membership_card_no, nic_no, date_of_birth, \
                                     join_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
                """
        cursor.execute(query, (first_name, last_name, email, phone, membership_card_no, nic_no, dob, join_date, status))
        conn.commit()
        return True, "Member added successfully!"
    except Exception as e:
        print(f"Database error adding member: {e}")
        if conn:
            conn.rollback()
        return False, f"Database error: Could not add member. {e}"
    finally:
        if conn:
            conn.close()


# ----------------------------------------------------
# FETCHING AND SEARCHING
# ----------------------------------------------------

def get_all_members():
    """Fetch all members, ordered by descending ID."""
    conn = None
    try:
        conn = get_connection()
        # Use DictCursor for consistent dictionary access in the GUI
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM members ORDER BY member_id DESC")
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Database error fetching all members: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search_member_by_name(name):
    """Return member info if found by name (case-insensitive partial match on full name)."""
    conn = None
    try:
        conn = get_connection()
        # Use DictCursor instead of the deprecated dictionary=True
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = """
                SELECT * \
                FROM members
                WHERE CONCAT(first_name, ' ', last_name) LIKE %s
                   OR first_name LIKE %s
                   OR last_name LIKE %s \
                """
        cursor.execute(query, (f"%{name}%", f"%{name}%", f"%{name}%"))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Database error during name search: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search_member_by_id(member_id):
    """Find member by member_id."""
    conn = None
    try:
        conn = get_connection()
        # Use DictCursor
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Database error during ID search: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search_member_by_cnic(cnic):
    """Search member by CNIC number (exact match on cleaned number)."""
    conn = None
    try:
        conn = get_connection()
        # Use DictCursor
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        # Assuming CNIC is stored in a clean format in DB, we search the cleaned input
        cursor.execute("SELECT * FROM members WHERE nic_no = %s", (cnic,))
        members = cursor.fetchall()
        return members
    except Exception as e:
        print(f"Database error during CNIC search: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search_member_by_phone(phone):
    """
    Search member by phone number, ignoring dashes and spaces in both the search
    term and the database column for robust matching.
    """
    conn = None
    try:
        cleaned_phone = phone.replace('-', '').replace(' ', '')
        conn = get_connection()
        # Use DictCursor
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        query = """
                SELECT * \
                FROM members
                WHERE REPLACE(REPLACE(phone, '-', ''), ' ', '') LIKE %s \
                """
        cursor.execute(query, (f"%{cleaned_phone}%",))
        members = cursor.fetchall()
        return members
    except Exception as e:
        print(f"Database error during phone search: {e}")
        return []
    finally:
        if conn:
            conn.close()


def search_member_by_card_number(card_number):
    """
    Search member by card number, prioritizing the online MySQL database,
    and falling back to the local SQLite cache if offline.
    """
    conn = None

    try:
        # 1. --- TRY ONLINE (MySQL) ---
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM members WHERE membership_card_no = %s", (card_number,))
        member = cursor.fetchone()
        conn.close()

        return member

    except ConnectionError:
        # 2. --- FALLBACK OFFLINE (SQLite Cache) ---

        QMessageBox.information(None, "Status Update",
                                "Primary database offline. Checking local member cache...")

        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()

        local_cursor.execute("""
                             SELECT member_id, first_name, last_name, membership_card_no
                             FROM local_members
                             WHERE membership_card_no = ?
                             """, (card_number,))

        local_member_tuple = local_cursor.fetchone()
        local_conn.close()

        if local_member_tuple:
            # Recreate the dictionary structure expected by the GUI
            return {
                'member_id': local_member_tuple[0],
                'first_name': local_member_tuple[1],
                'last_name': local_member_tuple[2],
                'membership_card_no': local_member_tuple[3],
                'status': 'OFFLINE CACHE'
            }

        return None

    except Exception as e:
        QMessageBox.critical(None, "Search Error",
                             f"Unexpected error during card search: {e}")
        return None


def get_member_by_id(member_id):
    """Fetch a single member by their ID and return as a dictionary (fetchone)."""
    conn = None
    try:
        conn = get_connection()
        # Use DictCursor
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
        member = cursor.fetchone()
        return member
    except Exception as e:
        print(f"Database error during single member fetch by ID: {e}")
        return None
    finally:
        if conn:
            conn.close()


# In models/member_model.py, inside sync_local_members()

def sync_local_members():
    """Pulls active member list from MySQL and caches them locally."""
    try:
        # ... (Synchronization logic succeeds) ...
        # REMOVE: print("Member cache synchronized successfully.")
        pass

    except Exception as e:
        # REPLACE print() with QMessageBox
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(None, "Synchronization Error",
                            f"Could not sync member cache (offline data might be stale): {e}")
        # REMOVE: print(f"Could not sync member cache: {e}")