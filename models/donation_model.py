from database.db_connection import get_connection
from models.transaction_model import create_transaction
from datetime import date

def get_donations_by_member(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            d.donation_id,
            d.transaction_id,
            d.donation_type,
            d.donation_date,
            d.amount,
            d.comment,
            m.first_name,
            m.last_name
        FROM donations d
        LEFT JOIN members m ON d.member_id = m.member_id
        WHERE d.member_id = %s
        ORDER BY d.donation_date DESC
    """, (member_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def add_donation_payment(member_id, donation_type, amount, comment, donor_name=None, donor_phone=None):
    """Add donation for either a member or non-member."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create transaction
    transaction_id = create_transaction(member_id, "donation", amount)

    # Insert donation record
    cursor.execute("""
        INSERT INTO donations (member_id, donor_name, donor_phone, transaction_id, donation_type, donation_date, amount, comment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (member_id, donor_name, donor_phone, transaction_id, donation_type, date.today(), amount, comment))

    conn.commit()
    cursor.close()
    conn.close()

    return True, {
        "transaction_id": transaction_id,
        "amount": amount,
        "donation_type": donation_type,
        "comment": comment,
        "donor_name": donor_name,
        "donor_phone": donor_phone
    }

def get_all_donations():
    """Fetch all donations, including non-member donor details."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            d.donation_id,
            d.transaction_id,
            d.member_id,
            d.donor_name,
            d.donor_phone,
            d.donation_type,
            d.comment,
            d.donation_date,
            tr.amount,
            tr.transaction_date,
            m.first_name,
            m.last_name,
            m.phone
        FROM donations d
        LEFT JOIN transactions tr ON d.transaction_id = tr.transaction_id
        LEFT JOIN members m ON d.member_id = m.member_id
        ORDER BY tr.transaction_date DESC
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows