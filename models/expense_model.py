import uuid
from datetime import date
from database.db_connection import get_connection
import app_state

def add_expense(expense_type, amount, receipt_number, comments):
    try:
        transaction_id = str(uuid.uuid4())
        conn = get_connection()
        cursor = conn.cursor()

        # Record in transactions table
        # before insertion, ensure numeric
        amt = float(amount)
        amt = -abs(amt)  # always negative

        cursor.execute("""
                       INSERT INTO transactions (transaction_id, transaction_type, user_id, amount, transaction_date)
                       VALUES (%s, %s, %s, %s, %s)
                       """, (transaction_id, "expense", app_state.current_user['user_id'], amt, date.today()))

        # Record in expenses table
        cursor.execute("""
            INSERT INTO expenses (transaction_id, expense_type, receipt_number, comments)
            VALUES (%s, %s, %s, %s)
        """, (transaction_id, expense_type, receipt_number, comments))

        conn.commit()
        conn.close()
        return True, transaction_id
    except Exception as e:
        print("❌ Error adding expense:", e)
        conn.rollback()
        conn.close()
        return False, str(e)


def get_all_expenses():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*, t.amount, t.transaction_date, u.full_name AS entered_by
        FROM expenses e
        JOIN transactions t ON e.transaction_id = t.transaction_id
        LEFT JOIN users u ON t.user_id = u.user_id
        ORDER BY t.transaction_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows
