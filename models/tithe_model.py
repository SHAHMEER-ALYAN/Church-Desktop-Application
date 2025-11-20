import uuid
from datetime import date, datetime
from database.db_connection import get_connection
import app_state
import pymysql.cursors


def get_tithes_by_member(member_id):
    """Fetch all tithes for a specific member."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = """
            SELECT t.tithe_id, \
                   t.transaction_id, \
                   tr.amount, \
                   t.tithe_month, \
                   t.tithe_year,
                   m.first_name, \
                   m.last_name
            FROM tithe t
                     JOIN transactions tr ON t.transaction_id = tr.transaction_id
                     LEFT JOIN members m ON t.member_id = m.member_id
            WHERE t.member_id = %s
            ORDER BY t.tithe_year DESC, t.tithe_month DESC \
            """
    cursor.execute(query, (member_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_tithes():
    """Fetch all tithes (Members + Non-Members)."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = """
            SELECT t.tithe_id, \
                   t.transaction_id, \
                   tr.amount, \
                   t.tithe_month, \
                   t.tithe_year,
                   m.first_name, \
                   m.last_name, \
                   t.donor_name
            FROM tithe t
                     JOIN transactions tr ON t.transaction_id = tr.transaction_id
                     LEFT JOIN members m ON t.member_id = m.member_id
            ORDER BY t.tithe_id DESC \
            """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_tithe_payment(member_data, months, year, monthly_amount):
    """
    Record tithe payments.
    member_data: Dict containing 'member_id' (None for non-members) and 'first_name'/'phone'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    results = []
    try:
        member_id = member_data.get('member_id')
        # If member_id is None, use the provided name; otherwise use None for donor_name
        donor_name = member_data.get('first_name') if not member_id else None
        donor_phone = member_data.get('phone') if not member_id else None

        user_id = app_state.current_user['user_id'] if app_state.current_user else None

        for m in months:
            transaction_id = str(uuid.uuid4())
            month_number = datetime.strptime(m, "%B").month
            tithe_date = f"{year}-{month_number:02d}-01"

            # 1. Insert into Transactions (Ledger)
            cursor.execute("""
                           INSERT INTO transactions
                           (transaction_id, member_id, user_id, transaction_type, amount, transaction_date)
                           VALUES (%s, %s, %s, 'tithe', %s, %s)
                           """, (transaction_id, member_id, user_id, monthly_amount, date.today()))

            # 2. Insert into Tithe (Details)
            cursor.execute("""
                           INSERT INTO tithe
                           (transaction_id, member_id, tithe_month, tithe_year, donor_name, donor_phone)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, (transaction_id, member_id, tithe_date, year, donor_name, donor_phone))

            results.append({
                "transaction_id": transaction_id,
                "month": m,
                "year": year,
                "amount": monthly_amount
            })

        conn.commit()
        return True, results

    except Exception as e:
        print(f"Error adding tithe: {e}")
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()