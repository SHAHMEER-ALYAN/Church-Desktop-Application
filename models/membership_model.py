import uuid
from datetime import date, datetime
from database.db_connection import get_connection
from database.local_db import get_local_connection, init_local_db
from utils.network_utils import is_internet_available
import app_state


# -----------------------------------------------------
# 🟢 MEMBERSHIP FUNCTIONS
# -----------------------------------------------------
def get_memberships_by_member(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT m.membership_id, tr.transaction_id, tr.amount,
               DATE_FORMAT(m.payment_month, '%%M %%Y') AS payment_period,
               tr.transaction_date
        FROM membership m
        JOIN transactions tr ON m.transaction_id = tr.transaction_id
        WHERE m.member_id = %s
        ORDER BY m.payment_year DESC, m.payment_month DESC
    """
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


# -----------------------------------------------------
# 🟡 ADD MEMBERSHIP (with offline mode)
# -----------------------------------------------------
def add_membership_payment(member_id, months, year, total_amount):
    """
    Add membership payments for the given months.
    If MySQL connection fails, data is saved locally in SQLite.
    """
    import uuid
    from datetime import date, datetime
    import app_state
    from database.db_connection import get_connection

    if not app_state.current_user or not app_state.current_user.get('user_id'):
        print("ERROR: User data not found in app_state.current_user.")
        return False, "Login status missing. Please restart the application."

        # Now we know app_state.current_user is a dictionary with 'user_id'
    user_id = app_state.current_user['user_id']  # Use this variable in the query

    try:
        conn = get_connection()
        cursor = conn.cursor()

        per_month = round(total_amount / len(months), 2)
        transactions = []

        for m in months:
            transaction_id = str(uuid.uuid4())
            month_number = datetime.strptime(m, "%B").month
            payment_date = f"{year}-{month_number:02d}-01"

            cursor.execute("""
                           INSERT INTO transactions (transaction_id, member_id, user_id, transaction_type, amount,
                                                     transaction_date)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, (transaction_id, member_id, user_id, "membership", per_month, date.today()))

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
        # --- OFFLINE MODE: Save locally in SQLite ---
        print("⚠️ Database unreachable, saving membership locally...")

        import sqlite3
        from database.local_db import get_local_connection, init_local_db

        init_local_db()
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()

        # Generate an offline UUID
        offline_id = str(uuid.uuid4())[:8]
        months_str = ",".join(months)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        local_cursor.execute("""
            INSERT INTO pending_membership_payments (member_id, months, year, total_amount, created_at, synced)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (member_id, months_str, year, total_amount, created_at))

        local_conn.commit()
        local_conn.close()

        print(f"🟡 Saved offline with ID: OFFLINE-{offline_id}")

        # Return fake transaction info for receipt
        return True, [{
            "transaction_id": f"OFFLINE-{offline_id}",
            "month": ", ".join(months),
            "year": year,
            "amount": total_amount
        }]

# -----------------------------------------------------
# 🔍 SEARCH MEMBER BY CARD NUMBER
# -----------------------------------------------------
def search_member_by_card(card_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE membership_card_no = %s", (card_number,))
    member = cursor.fetchone()
    cursor.close()
    conn.close()
    return member
