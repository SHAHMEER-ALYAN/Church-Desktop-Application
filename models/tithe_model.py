from database.db_connection import get_connection
from datetime import date
from models.transaction_model import create_transaction

def get_tithes_by_member(member_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            t.tithe_id,
            t.transaction_id,
            t.tithe_month,
            t.tithe_year,
            tr.amount
        FROM tithe t
        JOIN transactions tr ON t.transaction_id = tr.transaction_id
        WHERE t.member_id = %s
        ORDER BY t.tithe_year DESC, t.tithe_month DESC
    """, (member_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def add_tithe_payment(member, months, year, monthly_amount):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Month name to number mapping
    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }

    added = []
    for month_name in months:
        month_num = month_map[month_name]
        month_date = date(year, month_num, 1)

        # Check for duplicates
        cursor.execute("""
            SELECT 1 FROM tithe
            WHERE member_id = %s AND tithe_month = %s AND tithe_year = %s
        """, (member["member_id"], month_date, year))
        if cursor.fetchone():
            continue  # skip already paid months

        # Create transaction (returns auto-increment ID)
        transaction_id = create_transaction(member["member_id"], "tithe", monthly_amount)

        # Insert tithe record linked to transaction
        cursor.execute("""
            INSERT INTO tithe (member_id, transaction_id, tithe_month, tithe_year)
            VALUES (%s, %s, %s, %s)
        """, (member["member_id"], transaction_id, month_date, year))

        added.append({
            "transaction_id": transaction_id,
            "month": month_name,
            "year": year
        })

    conn.commit()
    cursor.close()
    conn.close()

    return (len(added) > 0, added)