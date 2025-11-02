from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QDateEdit, QComboBox, QLineEdit,
    QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import QDate
from datetime import datetime
import app_state
from gui.receipt_dialog import ReceiptDialog
from models.bag_offering_model import add_bag_offering, get_bag_offerings


class BagOfferingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bag Offering Management")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        # -----------------------------
        # FILTER SECTION
        # -----------------------------
        filter_layout = QHBoxLayout()
        self.year_filter = QComboBox()
        self.month_filter = QComboBox()

        current_year = datetime.now().year
        self.year_filter.addItem("All")
        for y in range(current_year, current_year - 10, -1):
            self.year_filter.addItem(str(y))

        self.month_filter.addItem("All")
        for m in [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]:
            self.month_filter.addItem(m)

        self.filter_btn = QPushButton("Apply Filter")
        self.filter_btn.clicked.connect(self.load_bag_offerings)

        filter_layout.addWidget(QLabel("Year:"))
        filter_layout.addWidget(self.year_filter)
        filter_layout.addWidget(QLabel("Month:"))
        filter_layout.addWidget(self.month_filter)
        filter_layout.addWidget(self.filter_btn)
        layout.addLayout(filter_layout)

        # -----------------------------
        # INPUT SECTION
        # -----------------------------
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        self.prayer_select = QComboBox()
        self.prayer_select.addItems(["Wednesday", "Sunday Morning", "Sunday Evening", "Other"])
        self.prayer_select.currentTextChanged.connect(self.toggle_custom_prayer)

        self.custom_prayer = QLineEdit()
        self.custom_prayer.setPlaceholderText("Enter custom prayer name...")
        self.custom_prayer.hide()

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter offering amount (Rs.)")

        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Add any remarks or comments...")

        self.add_btn = QPushButton("Add Bag Offering")
        self.add_btn.clicked.connect(self.save_bag_offering)

        layout.addWidget(QLabel("Service Date:"))
        layout.addWidget(self.date_edit)
        layout.addWidget(QLabel("Prayer Type:"))
        layout.addWidget(self.prayer_select)
        layout.addWidget(self.custom_prayer)
        layout.addWidget(QLabel("Amount (Rs):"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Comment:"))
        layout.addWidget(self.comment_input)
        layout.addWidget(self.add_btn)

        # -----------------------------
        # TABLE VIEW
        # -----------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Transaction ID", "Date", "Prayer Type", "Amount", "Comment"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Load data initially
        self.load_bag_offerings()

    # -----------------------------
    # BEHAVIOR
    # -----------------------------
    def toggle_custom_prayer(self):
        """Show or hide custom prayer field."""
        self.custom_prayer.setVisible(self.prayer_select.currentText() == "Other")

    def save_bag_offering(self):
        date_value = self.date_edit.date().toPython()
        prayer_type = (
            self.custom_prayer.text().strip()
            if self.prayer_select.currentText() == "Other"
            else self.prayer_select.currentText()
        )
        amount_text = self.amount_input.text().strip()
        comment = self.comment_input.toPlainText().strip()

        if not amount_text or not amount_text.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return

        member_id = app_state.current_user.get("member_id") if app_state.current_user else None
        success, transaction_id = add_bag_offering(member_id, date_value, prayer_type, float(amount_text), comment)

        if success:
            receipt_text = (
                f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                f"Transaction ID: {transaction_id}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Transaction Type: Bag Offering\n"
                f"Prayer Type: {prayer_type}\n"
                f"Amount: Rs. {amount_text}\n"
                f"Entered By: {app_state.current_user['full_name']}\n"
                "---------------------------------\n"
                f"{comment if comment else 'Thank you for your offering!'}"
            )
            receipt_dialog = ReceiptDialog("Bag Offering Receipt", receipt_text)
            receipt_dialog.exec()

            self.amount_input.clear()
            self.comment_input.clear()
            self.custom_prayer.clear()
            self.load_bag_offerings()

    def load_bag_offerings(self):
        year = self.year_filter.currentText()
        month = self.month_filter.currentText()
        data = get_bag_offerings(year, month)

        self.table.setRowCount(0)
        for row in data:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(row["transaction_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(str(row["service_date"])))
            self.table.setItem(r, 2, QTableWidgetItem(row.get("prayer_type", "-")))
            self.table.setItem(r, 3, QTableWidgetItem(f"{row['amount']:.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(row.get("comment", "")))
