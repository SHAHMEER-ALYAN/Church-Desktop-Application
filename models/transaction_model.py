import uuid
from datetime import date
import app_state
from database.db_connection import get_connection


def create_transaction(member_id, transaction_type, amount):
    """
    Inserts a new transaction associated with the currently logged-in user.
    Returns the transaction_id (UUID string).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # get logged-in user ID safely
    user_id = app_state.current_user.get("user_id", 1) if app_state.current_user else 1

    # Generate a unique UUID
    transaction_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO transactions (transaction_id, member_id, transaction_type, user_id, amount, transaction_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (transaction_id, member_id, transaction_type, user_id, amount, date.today()))

    conn.commit()
    cursor.close()
    conn.close()

    return transaction_id

def get_all_transactions():
    """Fetch all transactions with member and user info."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            t.transaction_id,
            t.transaction_type,
            t.amount,
            t.transaction_date,
            t.created_at,
            m.first_name,
            m.last_name,
            u.username,
            u.full_name
        FROM transactions t
        LEFT JOIN members m ON t.member_id = m.member_id
        LEFT JOIN users u ON t.user_id = u.user_id
        ORDER BY t.transaction_date DESC
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def get_filtered_transactions(year, month, tr_type, exp_type):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT t.transaction_id, \
                   t.transaction_date, \
                   t.transaction_type, \
                   t.amount, \
                   m.first_name                                AS member_name, \
                   u.full_name                                 AS user_name, \
                   COALESCE(e.comments, d.comment, th.comment) AS comments, \
                   COALESCE(e.expense_type, d.purpose, 'N/A')  AS detail
            FROM transactions t
                     LEFT JOIN members m ON t.member_id = m.member_id
                     LEFT JOIN users u ON t.user_id = u.user_id
                     LEFT JOIN expenses e ON t.transaction_id = e.transaction_id
                     LEFT JOIN donation d ON t.transaction_id = d.transaction_id
                     LEFT JOIN thanksgiving th ON t.transaction_id = th.transaction_id
            WHERE 1 = 1 \
            """

    params = []

    # Filters
    if year != "All":
        query += " AND YEAR(t.transaction_date) = %s"
        params.append(int(year))

    if month != "All":
        query += " AND MONTHNAME(t.transaction_date) = %s"
        params.append(month)

    if tr_type != "All Types":
        query += " AND t.transaction_type = %s"
        params.append(tr_type)

    if tr_type.lower() == "expense" and exp_type != "All Expense Types":
        query += " AND e.expense_type = %s"
        params.append(exp_type)

    query += " ORDER BY t.transaction_date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_transaction_summary(transactions):
    income = sum(t['amount'] for t in transactions if t['amount'] > 0)
    expense = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
    net = income - expense
    return {"income": income, "expense": expense, "net": net}
