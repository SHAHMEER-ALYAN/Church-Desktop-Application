from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from models.auth_model import authenticate_user
from gui.main_window import MainWindow
import app_state

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
        username = self.username.text().strip()
        password = self.password.text().strip()

        user = authenticate_user(username, password)
        if user:
            app_state.current_user = user  # store globally
            QMessageBox.information(self, "Success", f"Welcome {user['full_name']}!")
            # self.open_main_window()
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()

            if username == "admin" and password == "admin":
                from gui.login_window import current_user
                current_user["user_id"] = 1
                current_user["username"] = "admin"
                self.open_main_window()

        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
