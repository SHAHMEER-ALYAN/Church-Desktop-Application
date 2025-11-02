from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
)

import app_state
from gui.receipt_dialog import ReceiptDialog
from models.membership_model import add_membership_payment, get_paid_months_for_member
from models.membership_model import get_memberships_by_member


class MembershipWindow(QMainWindow):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.setWindowTitle("Membership Payments")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        self.info_label = QLabel(
            f"<b>Member ID:</b> {member['member_id']}<br>"
            f"<b>Name:</b> {member['first_name']} {member['last_name']}"
        )
        layout.addWidget(self.info_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Amount", "Month", "Transaction Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Add Membership Button
        self.add_btn = QPushButton("Add Membership Payment")
        self.add_btn.clicked.connect(self.open_add_membership_dialog)  # ✅ no parentheses
        layout.addWidget(self.add_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_membership()

    def load_membership(self):
        """Load all membership records for this member and display them."""
        membership = get_memberships_by_member(self.member["member_id"])
        self.table.setRowCount(0)

        # Add a Transaction ID column
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Transaction ID", "Amount", "Month", "Transaction Date"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, t in enumerate(membership):
            self.table.insertRow(i)

            transaction_id = str(t.get("transaction_id", "N/A"))
            amount = str(t.get("amount", "0"))
            payment_period = str(t.get("payment_period", "Unknown"))
            transaction_date = str(t.get("transaction_date", "Unknown"))

            self.table.setItem(i, 0, QTableWidgetItem(transaction_id))
            self.table.setItem(i, 1, QTableWidgetItem(amount))
            self.table.setItem(i, 2, QTableWidgetItem(payment_period))
            self.table.setItem(i, 3, QTableWidgetItem(transaction_date))

    def open_add_membership_dialog(self):
        dialog = AddMembershipDialog(self.member)
        if dialog.exec():
            self.load_membership()


from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QListWidget, QListWidgetItem,
    QAbstractItemView, QPushButton, QComboBox, QMessageBox
)

class AddMembershipDialog(QDialog):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.setWindowTitle("Add Membership Payment")
        self.setFixedSize(450, 550)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # ----- Amount Input -----
        self.amount = QLineEdit()
        self.amount.setPlaceholderText("Enter total amount")

        # ----- Year Dropdown -----
        self.year_combo = QComboBox()
        years = [str(y) for y in range(2020, 2035)]
        self.year_combo.addItems(years)
        current_year = str(datetime.now().year)
        self.year_combo.setCurrentText(current_year)
        self.year_combo.currentTextChanged.connect(self.load_months_list)

        # ----- Month Multi-Select -----
        self.months_list = QListWidget()
        self.months_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.load_months_list(current_year)

        # ----- Buttons -----
        self.submit_btn = QPushButton("Add Membership")
        self.submit_btn.clicked.connect(self.save_membership)

        form_layout.addRow("Total Amount:", self.amount)
        form_layout.addRow("Select Year:", self.year_combo)
        form_layout.addRow("Select Months:", self.months_list)
        form_layout.addRow("", self.submit_btn)
        layout.addLayout(form_layout)
        self.setLayout(layout)

    # ----------------------------
    # LOAD UNPAID MONTHS
    # ----------------------------
    def load_months_list(self, selected_year):
        """Populate months excluding those already paid."""
        self.months_list.clear()
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        paid_months = get_paid_months_for_member(self.member['member_id'], selected_year)
        unpaid_months = [m for i, m in enumerate(months, start=1) if i not in paid_months]

        for m in unpaid_months:
            self.months_list.addItem(QListWidgetItem(m))

    # ----------------------------
    # SAVE MEMBERSHIP PAYMENT
    # ----------------------------
    def save_membership(self):
        selected_items = self.months_list.selectedItems()
        months = [i.text() for i in selected_items]
        year = self.year_combo.currentText()
        total_amount_text = self.amount.text().strip()

        if not months:
            QMessageBox.warning(self, "Input Error", "Please select at least one month.")
            return
        if not total_amount_text or not total_amount_text.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid amount.")
            return

        total_amount = float(total_amount_text)

        # ✅ Validate amount evenly divides across months
        if total_amount % len(months) != 0:
            QMessageBox.warning(self, "Amount Error", "The total amount must divide evenly across selected months.")
            return

        # ✅ Double-check that selected months aren't already paid (safety check)
        paid_months = get_paid_months_for_member(self.member['member_id'], year)
        month_map = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }

        already_paid = [m for m in months if month_map[m] in paid_months]
        if already_paid:
            QMessageBox.warning(
                self,
                "Duplicate Month(s)",
                f"The following month(s) are already paid:\n\n{', '.join(already_paid)}"
            )
            return

        # ✅ If all checks pass, proceed
        success, data = add_membership_payment(self.member['member_id'], months, year, total_amount)

        if success:
            for t in data:
                receipt_text = (
                    f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                    f"Transaction ID: {t['transaction_id']}\n"
                    f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"Transaction Type: Membership\n"
                    f"Member: {self.member['first_name']} {self.member['last_name']} (ID: {self.member['member_id']})\n"
                    f"Amount: Rs. {t['amount']}\n"
                    f"Month: {t['month']} {t['year']}\n"
                    f"Entered By: {app_state.current_user['full_name']}\n"
                    "---------------------------------\n"
                    f"Thank you for your contribution!"
                )
                receipt_dialog = ReceiptDialog("Membership Receipt", receipt_text)
                receipt_dialog.exec()

            QMessageBox.information(self, "Success", "Membership payment(s) added successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Unable to add membership record.")