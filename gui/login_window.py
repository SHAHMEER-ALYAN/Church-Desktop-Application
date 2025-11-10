from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from models.auth_model import authenticate_user
from gui.main_window import MainWindow
import app_state


# We no longer need this import here
# import pymysql as mysql

# NOTE: The app_state should be handled by app_state.py,
# so the following global variable is redundant if app_state is used correctly.
# current_user = {
#     "user_id": None,
#     "username": None,
# }

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Church Management System - Login")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)

        layout.addWidget(QLabel("Please log in"))
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def handle_login(self):
        """
        Attempts to log in. Relies on auth_model to handle connection errors
        and execute the offline fallback, returning the final status.
        """
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Required", "Please enter both username and password.")
            return

        try:
            # This call will handle the ConnectionError internally:
            # 1. If online: Tries MySQL.
            # 2. If MySQL fails: Catches ConnectionError, shows "Status Update" messagebox,
            #    and attempts local cache login.
            success, result_data = authenticate_user(username, password)

            if success:
                user_info = result_data  # This is the full user dictionary

                app_state.current_user = user_info

                QMessageBox.information(self, "Login Successful", f"Welcome, {user_info['username']}!")
                self.main_window = MainWindow()
                self.main_window.show()  # Must show the main window
                self.close()
            else:
                # This catches authentication failures, including the scenario where
                # both online connection and local cache lookups failed.
                QMessageBox.warning(self, "Login Failed", result_data)

        # 🚨 CRITICAL FIX: The ConnectionError block is REMOVED 🚨
        # It is handled inside authenticate_user now.

        except Exception as e:
            # Catch all other unexpected Python errors (non-database/non-auth related)
            QMessageBox.critical(
                self,
                "APPLICATION ERROR",
                f"An unexpected application error occurred: {type(e).__name__}: {e}"
            )