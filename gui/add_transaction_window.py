from PySide6.QtWidgets import QMainWindow, QLabel

class AddTransactionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Transaction")
        self.setFixedSize(400, 300)
        self.label = QLabel("Transaction form coming soon...", self)
        self.label.move(50, 130)
