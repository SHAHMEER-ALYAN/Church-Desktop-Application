from database.db_connection import get_connection
from models.transaction_model import create_transaction


def add_bag_offering(member_id, service_date, prayer_type, amount, comment):
    """Insert a new bag offering record."""
    conn = get_connection()
    cursor = conn.cursor()

    transaction_id = create_transaction(member_id, "bag_offering", amount)

    cursor.execute("""
        INSERT INTO bag_offering (transaction_id, member_id, service_date, prayer_type, comment)
        VALUES (%s, %s, %s, %s, %s)
    """, (transaction_id, member_id, service_date, prayer_type, comment))

    conn.commit()
    cursor.close()
    conn.close()

    return True, transaction_id


def get_bag_offerings(year="All", month="All"):
    """Fetch all bag offering records (with optional year/month filters)."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            b.transaction_id,
            b.service_date,
            b.prayer_type,
            b.comment,
            t.amount
        FROM bag_offering b
        LEFT JOIN transactions t ON b.transaction_id = t.transaction_id
        WHERE 1=1
    """
    params = []

    if year != "All":
        query += " AND YEAR(b.service_date) = %s"
        params.append(year)
    if month != "All":
        query += " AND MONTHNAME(b.service_date) = %s"
        params.append(month)

    query += " ORDER BY b.service_date DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows
