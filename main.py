from PySide6.QtWidgets import QApplication
from gui.login_window import LoginWindow
import sys
import dotenv

if __name__ == "__main__":
    dotenv.load_dotenv()
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
