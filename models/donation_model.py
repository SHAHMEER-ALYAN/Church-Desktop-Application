from database.db_connection import get_connection
from models.transaction_model import create_transaction
from datetime import date

def get_donations_by_member(member_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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

def add_donation_payment(member_id, donation_type, amount, comment):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # create a linked transaction
    transaction_id = create_transaction(member_id, "donation", amount)

    cursor.execute("""
        INSERT INTO donations (member_id, transaction_id, donation_type, donation_date, amount, comment)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (member_id, transaction_id, donation_type, date.today(), amount, comment))

    conn.commit()
    cursor.close()
    conn.close()

    return True, {
        "transaction_id": transaction_id,
        "amount": amount,
        "donation_type": donation_type,
        "comment": comment
    }

def get_all_donations():
    """Fetch all donations from all members."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
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
        ORDER BY d.donation_date DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
