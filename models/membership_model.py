import uuid
from datetime import date, datetime
from PySide6.QtWidgets import QMessageBox

# Database and connection imports
from database.db_connection import get_connection, ConnectionError
from database.local_db import get_local_connection
import pymysql.cursors

# App state
import app_state


# -----------------------------------------------------
# 🟢 MEMBERSHIP QUERY FUNCTIONS
# -----------------------------------------------------
def get_memberships_by_member(member_id):
    """
    Retrieves all membership payment records for a given member from the primary database.
    """
    conn = get_connection()
    # Ensure cursor returns dicts for consistent handling
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
            SELECT m.membership_id, \
                   tr.transaction_id, \
                   tr.amount,
                   DATE_FORMAT(m.payment_month, '%%M %%Y') AS payment_period,
                   tr.transaction_date
            FROM membership m
                     JOIN transactions tr ON m.transaction_id = tr.transaction_id
            WHERE m.member_id = %s
            ORDER BY m.payment_year DESC, m.payment_month DESC \
            """
    cursor.execute(query, (member_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_paid_months_for_year(member_id, year):
    """
    Return a list of month numbers (1-12) already paid for this member in a given year.
    Includes fallback logic to check local history and pending transactions when offline.
    """
    try:
        # 1. --- TRY ONLINE ---
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT MONTH (payment_month)
                       FROM membership
                       WHERE member_id = %s
                         AND payment_year = %s
                       """, (member_id, year))
        rows = cursor.fetchall()
        conn.close()

        # Returns a list of month numbers (1-12)
        return [r[0] for r in rows] if rows else []

    except ConnectionError:
        # 2. --- FALLBACK OFFLINE: Combine Local History + Pending Payments ---

        # Note: We skip the QMessageBox here to avoid flooding the user,
        # but the search function (in member_model) notifies them of offline status.

        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()
        paid_month_numbers = set()

        # A. Query local cache (local_membership_history)
        local_cursor.execute("""
                             SELECT CAST(STRFTIME('%m', payment_month) AS INT)
                             FROM local_membership_history
                             WHERE member_id = ?
                               AND payment_year = ?
                             """, (member_id, year))

        # Add month numbers (1-12) from synced history
        for row in local_cursor.fetchall():
            paid_month_numbers.add(row[0])

        # B. Query pending payments (pending_membership_payments)
        month_name_to_num = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
        }

        local_cursor.execute("""
                             SELECT months
                             FROM pending_membership_payments
                             WHERE member_id = ? AND year = ?
                             """, (member_id, year))

        # Parse the comma-separated string from pending transactions
        for row in local_cursor.fetchall():
            months_str = row[0]
            for month_name in months_str.split(','):
                name = month_name.strip()
                if name in month_name_to_num:
                    paid_month_numbers.add(month_name_to_num[name])

        local_conn.close()
        # Return the final list of month numbers (1-12)
        return list(paid_month_numbers)

    except Exception as e:
        QMessageBox.critical(None, "Local DB Error",
                             f"Fatal error fetching local payment history: {e}")
        return []


# -----------------------------------------------------
# 🟡 ADD MEMBERSHIP (with offline mode)
# -----------------------------------------------------
def add_membership_payment(member_id, months, year, total_amount):
    """
    Add membership payments for the given months.
    If MySQL connection fails, data is saved locally in SQLite.
    """

    # --- CRITICAL FIX: Ensure user data is available ---
    if not app_state.current_user or not app_state.current_user.get('user_id'):
        return False, "User not logged in or missing user_id in app_state."
    user_id = app_state.current_user['user_id']
    # --------------------------------------------------

    try:
        conn = get_connection()
        cursor = conn.cursor()

        per_month = round(total_amount / len(months), 2)
        transactions = []

        for m in months:
            transaction_id = str(uuid.uuid4())
            month_number = datetime.strptime(m, "%B").month
            # payment_date is YYYY-MM-DD format for database insertion
            payment_date = f"{year}-{month_number:02d}-01"

            # 1. Insert into transactions table (Primary Ledger)
            cursor.execute("""
                           INSERT INTO transactions (transaction_id, member_id, user_id, transaction_type, amount,
                                                     transaction_date)
                           VALUES (%s, %s, %s, %s, %s, %s)
                           """, (transaction_id, member_id, user_id, "membership", per_month, date.today()))

            # 2. Insert into membership table (Detail Table)
            cursor.execute("""
                           INSERT INTO membership (transaction_id, member_id, payment_month, payment_year)
                           VALUES (%s, %s, %s, %s)
                           """, (transaction_id, member_id, payment_date, year))

            # 3. Cache history locally after successful sync (Optional but recommended)
            # You would need a separate function call here to update local_membership_history
            # or rely on the sync function that runs on app start/regained connection.

            transactions.append({
                "transaction_id": transaction_id,
                "month": m,
                "year": year,
                "amount": per_month
            })

        conn.commit()
        conn.close()
        return True, transactions

    except ConnectionError as e:
        # --- OFFLINE MODE: Save locally in SQLite ---

        # Notify user of offline action
        QMessageBox.warning(None, "Connection Lost",
                            f"Database unreachable. Saving payment locally (Offline Mode). Error: {e}")

        import sqlite3
        from database.local_db import get_local_connection, init_local_db

        init_local_db()
        local_conn = get_local_connection()
        local_cursor = local_conn.cursor()

        # Generate an offline UUID and prep data
        offline_id = str(uuid.uuid4())[:8]
        months_str = ",".join(months)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        local_cursor.execute("""
                             INSERT INTO pending_membership_payments (member_id, months, year, total_amount, created_at, synced)
                             VALUES (?, ?, ?, ?, ?, 0)
                             """, (member_id, months_str, year, total_amount, created_at))

        local_conn.commit()
        local_conn.close()

        # Success notification
        QMessageBox.information(None, "Offline Success",
                                f"Payment saved locally with ID: OFFLINE-{offline_id}. Must be synced later.")

        # Return fake transaction info for receipt
        return True, [{
            "transaction_id": f"OFFLINE-{offline_id}",
            "month": ", ".join(months),
            "year": year,
            "amount": total_amount
        }]

    except Exception as e:
        print(f"Transaction Error: {e}")
        return False, f"Unable to add membership record due to internal error: {e}"

# -----------------------------------------------------
# 🔍 OTHER FUNCTIONS (If used in membership window)
# -----------------------------------------------------

# NOTE: search_member_by_card has been moved/modified in member_model.py
# If you still have it here, remove it and use the one in member_model.py.