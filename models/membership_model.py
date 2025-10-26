import uuid
from datetime import date, datetime
from database.db_connection import get_connection
import app_state

def get_memberships_by_member(member_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """SELECT m.membership_id, tr.transaction_id, tr.amount,
               DATE_FORMAT(m.payment_month, '%M %Y') AS payment_period,
               tr.transaction_date
        FROM membership m
        JOIN transactions tr ON m.transaction_id = tr.transaction_id
        WHERE m.member_id = %s
        ORDER BY m.payment_year DESC, m.payment_month DESC"""
    cursor.execute(query, (member_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_paid_months_for_member(member_id, year):
    """Return a list of month numbers already paid for this member in a given year."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MONTH(payment_month)
        FROM membership
        WHERE member_id = %s AND payment_year = %s
    """, (member_id, year))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows] if rows else []

def add_membership_payment(member_id, months, year, total_amount):
    try:
        from datetime import date, datetime
        import uuid
        import app_state

        conn = get_connection()
        cursor = conn.cursor()

        per_month = round(total_amount / len(months), 2)
        transactions = []  # store for receipt

        for m in months:
            transaction_id = str(uuid.uuid4())
            month_number = datetime.strptime(m, "%B").month
            payment_date = f"{year}-{month_number:02d}-01"

            cursor.execute("""
                INSERT INTO transactions (transaction_id, member_id, user_id, transaction_type, amount, transaction_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (transaction_id, member_id, app_state.current_user['user_id'], "membership", per_month, date.today()))

            cursor.execute("""
                INSERT INTO membership (transaction_id, member_id, payment_month, payment_year)
                VALUES (%s, %s, %s, %s)
            """, (transaction_id, member_id, payment_date, year))

            transactions.append({
                "transaction_id": transaction_id,
                "month": m,
                "year": year,
                "amount": per_month
            })

        conn.commit()
        conn.close()
        return True, transactions
    except Exception as e:
        conn.rollback()
        conn.close()
        print("❌ Error adding membership:", e)
        return False, str(e)
