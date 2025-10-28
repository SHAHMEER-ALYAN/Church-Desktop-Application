from database.db_connection import get_connection
from datetime import date
from models.transaction_model import create_transaction


def add_thanksgiving(member_id, purpose, amount, comment):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Create transaction
    transaction_id = create_transaction(member_id, "thanksgiving", amount)

    cursor.execute("""
        INSERT INTO thanksgiving (member_id, transaction_id, purpose, comment, date)
        VALUES (%s, %s, %s, %s, %s)
    """, (member_id, transaction_id, purpose, comment, date.today()))

    conn.commit()
    cursor.close()
    conn.close()

    return True, {
        "transaction_id": transaction_id,
        "purpose": purpose,
        "amount": amount,
        "comment": comment
    }


def get_thanksgivings_by_member(member_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            g.thanksgiving_id,
            g.transaction_id,
            g.purpose,
            g.comment,
            tr.amount,
            tr.transaction_date AS date
        FROM thanksgiving g
        JOIN transactions tr ON g.transaction_id = tr.transaction_id
        WHERE g.member_id = %s
        ORDER BY tr.transaction_date DESC
    """, (member_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows