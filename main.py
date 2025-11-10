import sys
from PySide6.QtWidgets import QApplication, QMessageBox

# Import your application's windows
from gui.login_window import LoginWindow

# We no longer need to import get_connection or ConnectionError here,
# as the models will handle the connection attempts and fallbacks.

if __name__ == "__main__":

    # --- STEP 1: CREATE QAPPLICATION INSTANCE FIRST ---
    # This must be the very first step before any Qt widgets are used.
    app = QApplication(sys.argv)

    # --- STEP 2: START APPLICATION (Launch Login Window Directly) ---
    # The application now starts without performing an initial database diagnostic.
    # The first connection attempt will happen inside LoginWindow.handle_login(),
    # which uses auth_model.authenticate_user() and its offline fallback.
    try:
        login_window = LoginWindow()
        login_window.show()
        sys.exit(app.exec())

    except Exception as e:
        # This catches errors only during the GUI initialization phase.
        QMessageBox.critical(
            None,
            "GUI Initialization Error",
            f"Failed to start the Login Window:\n{type(e).__name__}: {e}"
        )
        sys.exit(1)