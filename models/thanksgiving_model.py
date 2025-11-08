from database.db_connection import get_connection
from datetime import date
from models.transaction_model import create_transaction


def add_thanksgiving(member_id, amount, purpose, comment="", donor_name=None, donor_phone=None):
    conn = get_connection()
    cursor = conn.cursor()

    # Create linked transaction
    transaction_id = create_transaction(member_id, "thanksgiving", amount)

    # Insert thanksgiving record (with donor info)
    cursor.execute("""
        INSERT INTO thanksgiving (
            member_id, transaction_id, purpose, comment, date, donor_name, donor_phone
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (member_id, transaction_id, purpose, comment, date.today(), donor_name, donor_phone))

    conn.commit()
    cursor.close()
    conn.close()
    return True, transaction_id


def get_all_thanksgivings():
    """Fetch all thanksgiving records (members + non-members)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            tg.thanksgiving_id,
            tg.transaction_id,
            tg.member_id,
            tg.purpose,
            tg.comment,
            tg.date,
            tg.donor_name,
            tg.donor_phone,
            tr.amount AS amount,
            tr.transaction_date,
            m.first_name,
            m.last_name,
            m.phone
        FROM thanksgiving tg
        JOIN transactions tr ON tg.transaction_id = tr.transaction_id
        LEFT JOIN members m ON tg.member_id = m.member_id
        ORDER BY tr.transaction_date DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_thanksgivings_by_member(member_id):
    """Fetch thanksgiving records for a specific member."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            tg.thanksgiving_id,
            tg.transaction_id,
            tg.purpose,
            tg.comment,
            tg.date,
            tg.donor_name,
            tg.donor_phone,
            tr.amount AS amount,
            tr.transaction_date,
            m.first_name,
            m.last_name,
            m.phone
        FROM thanksgiving tg
        JOIN transactions tr ON tg.transaction_id = tr.transaction_id
        LEFT JOIN members m ON tg.member_id = m.member_id
        WHERE tg.member_id = %s
        ORDER BY tr.transaction_date DESC
    """, (member_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows