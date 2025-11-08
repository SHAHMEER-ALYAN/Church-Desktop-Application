from database.db_connection import get_connection


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
        cursor = conn.cursor()
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
        cursor = conn.cursor(dictionary=True)
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
        cursor = conn.cursor(dictionary=True)
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
        cursor = conn.cursor(dictionary=True)
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


# --- NEW FUNCTION FOR ROBUST PHONE SEARCH ---
def search_member_by_phone(phone):
    """
    Search member by phone number, ignoring dashes and spaces in both the search
    term and the database column for robust matching.
    """
    conn = None
    try:
        # Pre-clean the search term for comparison
        cleaned_phone = phone.replace('-', '').replace(' ', '')

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Use MySQL's REPLACE function to clean the phone column before comparison
        # This makes the query slightly slower but much more robust for user input
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


def search_member_by_card_number(card_no):
    """Search member by membership card number (partial match)."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM members WHERE membership_card_no LIKE %s", (f"%{card_no}%",))
        members = cursor.fetchall()
        return members
    except Exception as e:
        print(f"Database error during card number search: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_member_by_id(member_id):
    """Fetch a single member by their ID and return as a dictionary (fetchone)."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
        member = cursor.fetchone()
        return member
    except Exception as e:
        print(f"Database error during single member fetch by ID: {e}")
        return None
    finally:
        if conn:
            conn.close()