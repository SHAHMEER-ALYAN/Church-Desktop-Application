# sync_manager.py
import os
import sqlite3
import time
import threading
import uuid
from datetime import datetime
import pymysql as mysql
import requests

from database.db_connection import get_connection
import app_state

# --- 🎯 GLOBAL STATUS VARIABLE ---
_SYNC_STATUS = "🔄 Sync Status: Initializing..."
LOCAL_DB_PATH = os.path.join(os.getcwd(), "local_cache.db")


# ----------------------------------------
# 💡 STATUS GETTER/SETTER
# ----------------------------------------
def set_current_sync_status(status_message):
    """Updates the global sync status variable."""
    global _SYNC_STATUS
    _SYNC_STATUS = status_message
    print(status_message)


def get_current_sync_status():
    """Returns the current sync status for the GUI."""
    global _SYNC_STATUS
    return _SYNC_STATUS


# ----------------------------------------
# 🧱 1. LOCAL DB INITIALIZATION
# ----------------------------------------
def init_local_db():
    """Ensure the SQLite cache database and table exist."""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS offline_membership
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       member_id
                       INTEGER,
                       year
                       INTEGER,
                       months
                       TEXT,
                       total_amount
                       REAL,
                       amount_per_month
                       REAL,
                       created_at
                       TEXT,
                       transaction_uuid
                       TEXT
                       UNIQUE
                   )
                   """)
    conn.commit()
    conn.close()


# ----------------------------------------
# 🌐 2. INTERNET CHECK
# ----------------------------------------
def check_internet_connection():
    """Quickly check if internet is available."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except Exception:
        return False


# ----------------------------------------
# 💾 3. SAVE OFFLINE RECORD
# ----------------------------------------
def save_offline_membership(member_id, months, year, total_amount, amount_per_month):
    """Save membership payments locally in SQLite if MySQL is unreachable."""
    init_local_db()

    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()

    # Use the same transaction ID logic as the online payment function for consistency
    generated_uuid = str(uuid.uuid4())

    try:
        cursor.execute("""
                       INSERT INTO offline_membership (member_id, year, months, total_amount, amount_per_month,
                                                       created_at, transaction_uuid)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       """, (
                           member_id,
                           year,
                           ",".join(months),
                           total_amount,
                           amount_per_month,
                           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           generated_uuid
                       ))
        conn.commit()
        set_current_sync_status(f"⚠️ Offline: Saved {len(months)} months locally. Awaiting sync.")
        return generated_uuid
    except Exception as e:
        print(f"❌ Error saving offline record: {e}")
        return None
    finally:
        conn.close()


# ----------------------------------------
# 🔁 4. UPLOAD LOGIC (used by both manual + auto sync)
# ----------------------------------------
def sync_local_memberships():
    """Uploads all locally saved membership records to MySQL if internet is available."""
    if not check_internet_connection():
        # Report status immediately and exit
        set_current_sync_status("⚠️ Sync Status: Offline — sync postponed.")
        return False, "Offline — sync postponed."

    set_current_sync_status("🔄 Sync Status: Connecting to server...")

    init_local_db()
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM offline_membership")
    records = cursor.fetchall()

    if not records:
        conn.close()
        set_current_sync_status(f"✅ Sync Status: No pending offline records.")
        return True, "✅ No pending offline records."

    set_current_sync_status(f"🔄 Sync Status: Uploading {len(records)} pending record(s)...")

    mysql_conn = None
    mysql_cursor = None
    synced = 0
    failed = 0

    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()

        for record in records:
            (
                local_id,
                member_id,
                year,
                months_csv,
                total_amount,
                amount_per_month,
                created_at,
                transaction_uuid  # Not used in SQL but kept for reference
            ) = record

            try:
                months = months_csv.split(",")

                # NOTE: The division logic is safer to use the stored amount_per_month
                # rather than recalculating, but we'll use your original calculation
                per_month = round(float(total_amount) / len(months), 2)

                for m in months:
                    transaction_id = str(uuid.uuid4())
                    month_number = datetime.strptime(m, "%B").month
                    payment_date = f"{year}-{month_number:02d}-01"

                    # 1. Insert into transactions
                    mysql_cursor.execute("""
                                         INSERT INTO transactions (transaction_id, member_id, user_id, transaction_type,
                                                                   amount, transaction_date)
                                         VALUES (%s, %s, %s, %s, %s, %s)
                                         """, (
                                             transaction_id,
                                             member_id,
                                             app_state.current_user['user_id'],
                                             "membership",
                                             per_month,
                                             datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                         ))

                    # 2. Insert into membership
                    mysql_cursor.execute("""
                                         INSERT INTO membership (transaction_id, member_id, payment_month, payment_year)
                                         VALUES (%s, %s, %s, %s)
                                         """, (
                                             transaction_id,
                                             member_id,
                                             payment_date,
                                             year
                                         ))

                mysql_conn.commit()

                cursor.execute("DELETE FROM offline_membership WHERE id = ?", (local_id,))
                conn.commit()
                synced += 1

            except Exception as e:
                mysql_conn.rollback()  # Rollback the failed record's transaction
                print(f"❌ Sync failed for local record {local_id}: {e}")
                failed += 1

        final_message = f"🔄 Sync complete: {synced} uploaded, {failed} failed."
        set_current_sync_status(final_message)
        return True, final_message

    except mysql.connector.Error as db_err:
        error_msg = f"❌ Sync Status: DB Connection Error ({db_err})"
        set_current_sync_status(error_msg)
        return False, error_msg

    finally:
        if mysql_cursor: mysql_cursor.close()
        if mysql_conn and mysql_conn.is_connected(): mysql_conn.close()
        conn.close()


# ----------------------------------------
# 🔘 5. MANUAL SYNC (button)
# ----------------------------------------
def sync_offline_data():
    """
    Manual sync trigger for GUI 'Sync Now' button.
    """
    set_current_sync_status("🔄 Sync Status: Manually triggered sync...")
    return sync_local_memberships()


# ----------------------------------------
# ⚙️ 6. AUTO-SYNC THREAD
# ----------------------------------------
def start_auto_sync(interval=60):
    """
    Automatically runs sync every `interval` seconds in the background.
    """

    def _auto_sync_loop():
        # Initial status setup
        set_current_sync_status("🟢 Auto-sync thread active. Monitoring...")

        while True:
            # Check internet before attempting connection
            if check_internet_connection():
                success, msg = sync_local_memberships()
                # sync_local_memberships updates the status, so just log here.
            else:
                set_current_sync_status("⚠️ Sync Status: Offline — checking again in 5 minutes.")

            time.sleep(interval)

    thread = threading.Thread(target=_auto_sync_loop, daemon=True)
    thread.start()
    print("🟢 Auto-sync thread started.")