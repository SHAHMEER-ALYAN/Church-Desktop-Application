from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from models.auth_model import authenticate_user
from gui.main_window import MainWindow
import app_state

import pymysql as mysql

# --- GLOBAL SESSION STORE ---
current_user = {
    "user_id": None,
    "username": None,
}

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
        """Attempts to log in and shows a critical error if DB connection fails."""
        # username = self.username_input.text().strip()
        # password = self.password_input.text().strip()

        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Required", "Please enter both username and password.")
            return

        try:
            # This call to login_user will trigger get_connection()
            success, result_data = authenticate_user(username, password)

            if success:
                user_info = result_data  # This is the full user dictionary

                app_state.current_user = user_info

                QMessageBox.information(self, "Login Successful", f"Welcome, {user_info['username']}!")
                # self.open_main_dashboard()
                self.main_window = MainWindow()
                self.close()
            else:
                # If failure, result_data is the message string
                QMessageBox.warning(self, "Login Failed", result_data)

        except ConnectionError as e:
            # 🚨 THIS IS THE CRITICAL ALERT BOX 🚨
            QMessageBox.critical(
                self,
                "CRITICAL DATABASE ERROR",
                f"The application could not connect to the database or load configuration.\n\nDetails:\n{e}"
            )
        except Exception as e:
            # Catch all other unexpected Python errors
            QMessageBox.critical(
                self,
                "APPLICATION ERROR",
                f"An unexpected application error occurred: {type(e).__name__}: {e}"
            )