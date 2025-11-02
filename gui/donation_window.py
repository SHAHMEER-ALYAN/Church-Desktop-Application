from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QComboBox, QTextEdit
)
from datetime import datetime
from models.donation_model import get_donations_by_member, add_donation_payment
from gui.receipt_dialog import ReceiptDialog
import app_state


class DonationWindow(QMainWindow):
    def __init__(self, member=None):
        super().__init__()

        # 🟢 Handle all-members mode
        if not member or not member.get("member_id"):
            self.member = {"member_id": None, "first_name": "All", "last_name": "Members"}
            self.all_members_mode = True
        else:
            self.member = member
            self.all_members_mode = False

        self.setWindowTitle(f"Donations - {self.member['first_name']} {self.member['last_name']}")
        self.setMinimumSize(850, 600)

        layout = QVBoxLayout()

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Donation ID", "Transaction ID", "Member", "Type", "Amount", "Date", "Comment"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Add button
        add_btn = QPushButton("Add Donation")
        add_btn.clicked.connect(self.open_add_donation_dialog)
        layout.addWidget(add_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_donations()

    def load_donations(self):
        if self.all_members_mode:
            from models.donation_model import get_all_donations
            donations = get_all_donations()
        else:
            from models.donation_model import get_donations_by_member
            donations = get_donations_by_member(self.member["member_id"])

        self.table.setRowCount(0)
        for d in donations:
            row = self.table.rowCount()
            self.table.insertRow(row)

            member_name = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
            if not member_name:
                member_name = "-"

            self.table.setItem(row, 0, QTableWidgetItem(str(d.get("donation_id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(d.get("transaction_id", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(member_name))
            self.table.setItem(row, 3, QTableWidgetItem(str(d.get("donation_type", "")).capitalize()))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rs. {float(d.get('amount', 0)):.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(str(d.get("donation_date", ""))))
            self.table.setItem(row, 6, QTableWidgetItem(d.get("comment", "") or ""))

    def open_add_donation_dialog(self):
        dialog = AddDonationDialog(self.member)
        dialog.exec()
        self.load_donations()


class AddDonationDialog(QDialog):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.setWindowTitle("Add Donation")
        self.setFixedSize(400, 450)

        layout = QFormLayout()

        # 🟢 Member dropdown (only in All-Members mode)
        self.member_dropdown = None
        if not member.get("member_id"):  # All-members mode
            from models.member_model import get_all_members
            members = get_all_members()

            self.member_dropdown = QComboBox()
            for m in members:
                full_name = f"{m['first_name']} {m['last_name']}"
                self.member_dropdown.addItem(full_name, m["member_id"])

            layout.addRow("Select Member:", self.member_dropdown)

        # Donation Type
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems([
            "general", "building", "charity", "event",
            "special", "youth", "mission", "other"
        ])

        # Amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount (Rs.)")

        # Comment
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Enter comment (optional)")

        # Submit
        self.submit_btn = QPushButton("Submit Donation")
        self.submit_btn.clicked.connect(self.save_donation)

        layout.addRow("Donation Type:", self.type_dropdown)
        layout.addRow("Amount:", self.amount_input)
        layout.addRow("Comment:", self.comment_input)
        layout.addRow("", self.submit_btn)
        self.setLayout(layout)

    def save_donation(self):
        """Save donation to DB."""
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid amount.")
            return

        donation_type = self.type_dropdown.currentText()
        comment = self.comment_input.toPlainText().strip()

        # 🟢 Determine member_id (use dropdown in all-member mode)
        if self.member.get("member_id"):
            member_id = self.member["member_id"]
            member_name = f"{self.member['first_name']} {self.member['last_name']}"
        else:
            if not self.member_dropdown:
                QMessageBox.warning(self, "Error", "Member selection missing.")
                return
            member_id = self.member_dropdown.currentData()
            member_name = self.member_dropdown.currentText()

        # Save donation
        from models.donation_model import add_donation_payment
        success, data = add_donation_payment(member_id, donation_type, amount, comment)

        if success:
            receipt_text = (
                f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                f"Transaction ID: {data['transaction_id']}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Transaction Type: Donation\n"
                f"Member: {member_name} (ID: {member_id})\n"
                f"Donation Type: {data['donation_type'].capitalize()}\n"
                f"Amount: Rs. {data['amount']:.2f}\n"
                f"Comment: {data['comment'] or 'N/A'}\n"
                f"Entered By: {app_state.current_user['full_name']}\n"
                "--------------------------------\n"
                "Thank you for your kind contribution!"
            )

            receipt_dialog = ReceiptDialog("Donation Receipt", receipt_text)
            receipt_dialog.exec()
            QMessageBox.information(self, "Success", "Donation recorded successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Unable to add donation record.")