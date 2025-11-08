import sys
from PySide6.QtWidgets import QApplication, QMessageBox
import pymysql

# --- IMPORT CRITICAL DIAGNOSTIC COMPONENTS ---
from database.db_connection import get_connection, ConnectionError

# Import your application's windows
from gui.login_window import LoginWindow


def run_startup_diagnostic():
    """
    Attempts to connect to the DB and validates the configuration loading.
    NOTE: This is called AFTER QApplication is instantiated.
    """
    # 1. Test database connection
    try:
        conn = get_connection()
        if conn:
            conn.close()
            # If successful, return True to proceed
            return True
        else:
            # Fallback if connection is None
            raise ConnectionError("Connection object is None after attempt.")

    except ConnectionError as e:
        # Catch the custom errors raised by db_connection.py
        QMessageBox.critical(
            None,
            "CRITICAL DATABASE ERROR",
            f"The application failed to connect or load configuration.\n\nDetails:\n{e}"
        )
        return False

    except ConnectionError as e:
        # Catch the custom errors raised by db_connection.py
        QMessageBox.critical(
            None,
            "CRITICAL DATABASE ERROR",
            f"The application failed to connect or load configuration.\n\nDetails:\n{e}"
        )
        return False

    except Exception as e:
        # Catch any unexpected Python/PySide6 error during startup
        QMessageBox.critical(
            None,
            "CRITICAL APPLICATION ERROR",
            f"An unexpected error occurred during startup:\n{type(e).__name__}: {e}"
        )
        return False


if __name__ == "__main__":

    # --- STEP 1: CREATE QAPPLICATION INSTANCE FIRST ---
    # This must be the very first step before any Qt widgets (like QMessageBox) are used.
    app = QApplication(sys.argv)

    # --- STEP 2: RUN DIAGNOSTIC (Now it can use QMessageBox) ---
    if not run_startup_diagnostic():
        # If diagnostic fails, an error box is shown, and we exit immediately.
        sys.exit(1)

    # --- STEP 3: START APPLICATION (Only if diagnostic passed) ---
    try:
        login_window = LoginWindow()
        login_window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(
            None,
            "GUI Initialization Error",
            f"Failed to start the Login Window:\n{type(e).__name__}: {e}"
        )
        sys.exit(1)