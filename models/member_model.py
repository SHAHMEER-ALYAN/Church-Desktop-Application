from database.db_connection import get_connection

def search_member_by_name(name):
    """Return member info if found by name (case-insensitive partial match)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT * FROM members 
        WHERE CONCAT(first_name, ' ', last_name) LIKE %s
    """
    cursor.execute(query, (f"%{name}%",))
    result = cursor.fetchall()
    conn.close()
    return result


def member_exists(email, phone, nic_no, membership_card_no):
    """Return True if a member with same email, phone, NIC, or membership card already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) 
        FROM members 
        WHERE email=%s OR phone=%s OR nic_no=%s OR membership_card_no=%s
    """, (email, phone, nic_no, membership_card_no))
    (count,) = cursor.fetchone()
    conn.close()
    return count > 0


def add_member(first_name, last_name, email, phone, dob, join_date, nic_no, membership_card_no, status="active"):
    """Add a new member if they don't already exist."""
    if member_exists(email, phone, nic_no, membership_card_no):
        return False, "Member with same Email, Phone, NIC, or Membership Card already exists."

    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO members (first_name, last_name, email, phone, membership_card_no, nic_no, date_of_birth, join_date, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (first_name, last_name, email, phone, membership_card_no, nic_no, dob, join_date, status))
    conn.commit()
    conn.close()
    return True, "Member added successfully!"

from database.db_connection import get_connection

def get_all_members():
    """Fetch all members."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members ORDER BY member_id DESC")
    result = cursor.fetchall()
    conn.close()
    return result


def search_member_by_id(member_id):
    """Find member by ID."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def search_member_by_cnic(cnic):
    """Search member by CNIC number (Pakistan 13-digit number)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE nic_no = %s", (cnic,))
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return members

def search_member_by_card_number(card_no):
    """Search member by membership card number."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE membership_card_no LIKE %s", (f"%{card_no}%",))
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return members

def get_member_by_id(member_id):
    """Fetch a single member by their ID and return as a dictionary."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    member = cursor.fetchone()
    cursor.close()
    conn.close()
    return member