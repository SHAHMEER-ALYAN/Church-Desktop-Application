import uuid
from datetime import date
from database.db_connection import get_connection
import app_state
import pymysql.cursors


def get_all_parking():
    """Fetch all parking records."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = """
            SELECT p.parking_id, \
                   p.transaction_id, \
                   t.amount, \
                   t.transaction_date,
                   p.vehicle_number, \
                   p.vehicle_type, \
                   p.phone_number,
                   p.payment_month, \
                   p.payment_year,
                   m.first_name, \
                   m.last_name
            FROM parking p
                     JOIN transactions t ON p.transaction_id = t.transaction_id
                     LEFT JOIN members m ON p.member_id = m.member_id
            ORDER BY p.parking_id DESC \
            """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


def search_parking_by_vehicle(vehicle_number):
    """Search parking records by vehicle number."""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = """
            SELECT p.parking_id, \
                   p.transaction_id, \
                   t.amount, \
                   t.transaction_date,
                   p.vehicle_number, \
                   p.vehicle_type, \
                   p.phone_number,
                   p.payment_month, \
                   p.payment_year,
                   m.first_name, \
                   m.last_name
            FROM parking p
                     JOIN transactions t ON p.transaction_id = t.transaction_id
                     LEFT JOIN members m ON p.member_id = m.member_id
            WHERE p.vehicle_number LIKE %s
            ORDER BY p.parking_id DESC \
            """
    cursor.execute(query, (f"%{vehicle_number}%",))
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_parking_payment(member_id, vehicle_number, phone, vehicle_type, total_amount, months, year):
    """
    Record parking payments for multiple months.
    Returns (success, results_list).
    """
    conn = get_connection()
    cursor = conn.cursor()

    results = []

    try:
        user_id = app_state.current_user['user_id'] if app_state.current_user else None

        if not months:
            return False, "No months selected."

        # Calculate amount per month
        monthly_amount = total_amount / len(months)

        for m in months:
            transaction_id = str(uuid.uuid4())

            # 1. Insert into Transactions
            cursor.execute("""
                           INSERT INTO transactions
                           (transaction_id, member_id, user_id, transaction_type, amount, transaction_date)
                           VALUES (%s, %s, %s, 'parking', %s, %s)
                           """, (transaction_id, member_id, user_id, monthly_amount, date.today()))

            # 2. Insert into Parking
            cursor.execute("""
                           INSERT INTO parking
                           (transaction_id, member_id, vehicle_number, phone_number, vehicle_type, payment_month,
                            payment_year)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           """, (transaction_id, member_id, vehicle_number, phone, vehicle_type, m, year))

            results.append({
                "transaction_id": transaction_id,
                "month": m,
                "year": year,
                "amount": monthly_amount
            })

        conn.commit()
        return True, results

    except Exception as e:
        print(f"Error adding parking: {e}")
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()