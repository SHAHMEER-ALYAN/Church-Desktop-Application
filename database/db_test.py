import sys
from PySide6.QtWidgets import QApplication, QMessageBox
# Ensure this import points to your actual db_connection file
from database.db_connection import get_connection, ConnectionError


def run_db_diagnostic():
    """
    Attempts to get a database connection and reports the result in a QMessageBox.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    try:
        # This call will run the PyInstaller path resolution and the MySQL connection logic
        conn = get_connection()

        if conn and conn.is_connected():
            title = "Database Connection SUCCESS"
            message = "Successfully connected to the MySQL database! The application should now be able to log in."
            QMessageBox.information(None, title, message)
            conn.close()
            return True
        else:
            # Should be caught by the except block, but included for completeness
            title = "Database Connection FAILURE"
            message = "Connection attempt returned no active connection."
            QMessageBox.critical(None, title, message)
            return False

    except ConnectionError as e:
        # This catches errors during config loading or actual MySQL connection failures
        title = "CRITICAL: Configuration/Connection Failure"
        message = f"The application failed to connect or load configuration.\n\nDetails:\n{e}"
        QMessageBox.critical(None, title, message)
        return False

    except Exception as e:
        # Catch unexpected errors (e.g., PySide6/import issues)
        title = "CRITICAL: Unexpected Error"
        message = f"An unexpected error occurred during startup:\n{type(e).__name__}: {e}"
        QMessageBox.critical(None, title, message)
        return False

    finally:
        # We don't exit the app here, just let the main app run after the test
        pass