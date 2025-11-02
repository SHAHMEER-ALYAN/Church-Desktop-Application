from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QGridLayout, QWidget, QMessageBox, QLabel, QVBoxLayout
)
from PySide6.QtCore import QSize, Qt
from gui.add_transaction_window import AddTransactionWindow
from gui.member_window import MemberWindow
from gui.transaction_view_window import TransactionViewWindow
from datetime import datetime
import app_state


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Church Management System - Dashboard")
        self.showMaximized()

        # --- Outer Vertical Layout ---
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # --- Logged-in User Label ---
        if app_state.current_user:
            user_label = QLabel(
                f"Logged in as: {app_state.current_user['full_name']} ({app_state.current_user['role']})"
            )
            user_label.setAlignment(Qt.AlignCenter)
            user_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; margin-bottom: 20px;")
            main_layout.addWidget(user_label)

        # --- Grid Layout for Buttons ---
        grid_layout = QGridLayout()
        grid_layout.setAlignment(Qt.AlignCenter)
        grid_layout.setSpacing(40)

        # Helper function for consistent button creation
        def create_button(text, callback, row, col):
            btn = QPushButton(text)
            btn.setFixedSize(QSize(300, 100))
            btn.clicked.connect(callback)
            grid_layout.addWidget(btn, row, col)
            return btn

        # --- Add Buttons in Grid (3 columns layout) ---
        create_button("Add / View Member", self.open_member_window, 0, 0)
        create_button("Add / View Tithe", self.open_tithe_window, 0, 1)
        create_button("Add / View Donation", self.open_donation_window, 0, 2)

        create_button("Add / View Bag Offering", self.open_bag_offering_window, 1, 0)
        create_button("Add / View Expense", self.open_expense_window, 1, 1)
        create_button("View Transactions & Reports", self.open_transaction_view, 1, 2)

        create_button("Add / View Thanksgiving", self.open_thanksgiving_window, 2, 0)
        create_button("Add / View Parking Fee", self.open_parking_window, 2, 1)
        create_button("Backup Database", self.open_backup_window, 2, 2)

        # Add grid inside main vertical layout
        main_layout.addLayout(grid_layout)

        # --- Central Widget ---
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # --- Button Actions ---
    def open_member_window(self):
        self.member_window = MemberWindow()
        self.member_window.show()

    def open_tithe_window(self):
        from gui.tithe_window import TitheWindow
        self.tithe_window = TitheWindow()  # no member
        self.tithe_window.show()

    def open_donation_window(self):
        from gui.donation_window import DonationWindow
        self.donation_window = DonationWindow()  # no member
        self.donation_window.show()

    def open_bag_offering_window(self):
        from gui.bag_offering_window import BagOfferingWindow
        self.bag_offering_window = BagOfferingWindow()
        self.bag_offering_window.show()

    def open_expense_window(self):
        from gui.expense_window import ExpenseWindow
        self.expense_window = ExpenseWindow()
        self.expense_window.show()

    def open_thanksgiving_window(self):
        from gui.thanksgiving_window import ThanksgivingWindow
        self.thanksgiving_window = ThanksgivingWindow()  # no member
        self.thanksgiving_window.show()

    def open_parking_window(self):
        from gui.parking_window import ParkingWindow
        self.parking_window = ParkingWindow()
        self.parking_window.show()

    def open_transaction_view(self):
        self.transaction_window = TransactionViewWindow()
        self.transaction_window.show()

    def open_backup_window(self):
        from gui.backup_window import BackupWindow
        self.backup_window = BackupWindow()
        self.backup_window.show()

