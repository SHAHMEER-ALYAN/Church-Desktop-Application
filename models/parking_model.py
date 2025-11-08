from database.db_connection import get_connection
from models.transaction_model import create_transaction
from datetime import date

def add_parking_payment(member_id, vehicle_number, phone_number, vehicle_type, amount):
    """Record a parking payment and related transaction."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create linked transaction
    transaction_id = create_transaction(member_id, "parking", amount)

    cursor.execute("""
        INSERT INTO parking (transaction_id, member_id, vehicle_number, phone_number, vehicle_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (transaction_id, member_id, vehicle_number, phone_number, vehicle_type))

    conn.commit()
    cursor.close()
    conn.close()

    return True, transaction_id


def get_all_parking():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            p.parking_id,
            p.transaction_id,
            p.vehicle_number,
            p.phone_number,
            p.vehicle_type,
            t.amount,
            t.transaction_date,
            m.first_name,
            m.last_name
        FROM parking p
        LEFT JOIN transactions t ON p.transaction_id = t.transaction_id
        LEFT JOIN members m ON p.member_id = m.member_id
        ORDER BY t.transaction_date DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def search_parking_by_vehicle(vehicle_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, t.amount, t.transaction_date, m.first_name, m.last_name
        FROM parking p
        JOIN transactions t ON p.transaction_id = t.transaction_id
        LEFT JOIN members m ON p.member_id = m.member_id
        WHERE UPPER(p.vehicle_number) LIKE %s
        ORDER BY t.transaction_date DESC
    """, (f"%{vehicle_number}%",))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
