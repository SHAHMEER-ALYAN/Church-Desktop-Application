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
        self.setMinimumSize(950, 600)

        layout = QVBoxLayout()

        # 🧱 Table setup (added Phone column)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Donation ID", "Transaction ID", "Member / Donor",
            "Phone", "Type", "Amount", "Date", "Comment"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # ➕ Add button
        add_btn = QPushButton("Add Donation")
        add_btn.clicked.connect(self.open_add_donation_dialog)
        layout.addWidget(add_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_donations()

    def load_donations(self):
        """Load and display all donations with member or non-member details."""
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

            # --- Determine donor name and phone ---
            if d.get("first_name") or d.get("last_name"):  # Church member
                donor_name = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
                donor_phone = d.get("phone", "")
            elif d.get("donor_name"):  # Non-member
                donor_name = d.get("donor_name")
                donor_phone = d.get("donor_phone", "")
            else:
                donor_name = "-"
                donor_phone = ""

            # --- Fill table ---
            self.table.setItem(row, 0, QTableWidgetItem(str(d.get("donation_id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(d.get("transaction_id", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(donor_name))
            self.table.setItem(row, 3, QTableWidgetItem(donor_phone))
            self.table.setItem(row, 4, QTableWidgetItem(str(d.get("donation_type", "")).capitalize()))
            self.table.setItem(row, 5, QTableWidgetItem(f"Rs. {float(d.get('amount', 0)):.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(str(d.get("donation_date", ""))))
            self.table.setItem(row, 7, QTableWidgetItem(d.get("comment", "") or ""))

    def open_add_donation_dialog(self):
        dialog = AddDonationDialog(self.member)
        dialog.exec()
        self.load_donations()


class AddDonationDialog(QDialog):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.setWindowTitle("Add Donation")
        self.setFixedSize(420, 550)

        layout = QFormLayout()

        # --- Member / Non-member selection ---
        self.is_non_member = QComboBox()
        self.is_non_member.addItems(["Church Member", "Non-Member / Guest"])
        self.is_non_member.currentTextChanged.connect(self.toggle_non_member_fields)
        layout.addRow("Donor Type:", self.is_non_member)

        # --- Member dropdown (only for all-member mode) ---
        self.member_dropdown = None
        if not member.get("member_id"):  # All-members mode
            from models.member_model import get_all_members
            members = get_all_members()

            self.member_dropdown = QComboBox()
            for m in members:
                full_name = f"{m['first_name']} {m['last_name']}"
                self.member_dropdown.addItem(full_name, m["member_id"])

            layout.addRow("Select Member:", self.member_dropdown)

        # --- Non-member fields ---
        self.non_member_name = QLineEdit()
        self.non_member_name.setPlaceholderText("Full Name (for non-members)")
        self.non_member_phone = QLineEdit()
        self.non_member_phone.setPlaceholderText("Phone Number")

        layout.addRow("Donor Name:", self.non_member_name)
        layout.addRow("Donor Phone:", self.non_member_phone)

        # --- Donation Details ---
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems([
            "general", "building", "charity", "event",
            "special", "youth", "mission", "other"
        ])
        layout.addRow("Donation Type:", self.type_dropdown)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount (Rs.)")
        layout.addRow("Amount:", self.amount_input)

        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Enter comment (optional)")
        layout.addRow("Comment:", self.comment_input)

        # --- Submit Button ---
        self.submit_btn = QPushButton("Submit Donation")
        self.submit_btn.clicked.connect(self.save_donation)
        layout.addRow("", self.submit_btn)

        self.setLayout(layout)
        self.toggle_non_member_fields("Church Member")

    def toggle_non_member_fields(self, value):
        """Enable/disable fields based on donor type."""
        is_non_member = value == "Non-Member / Guest"
        self.non_member_name.setEnabled(is_non_member)
        self.non_member_phone.setEnabled(is_non_member)

        if self.member_dropdown:
            self.member_dropdown.setEnabled(not is_non_member)

    def save_donation(self):
        """Save donation for member or non-member."""
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid amount.")
            return

        donation_type = self.type_dropdown.currentText()
        comment = self.comment_input.toPlainText().strip()

        is_non_member = self.is_non_member.currentText() == "Non-Member / Guest"
        donor_name = donor_phone = None
        member_id = None
        member_name = "N/A"

        # Determine donor
        if is_non_member:
            donor_name = self.non_member_name.text().strip()
            donor_phone = self.non_member_phone.text().strip()
            if not donor_name or not donor_phone:
                QMessageBox.warning(self, "Missing Info", "Please enter name and phone number for non-member.")
                return
        else:
            if self.member.get("member_id"):  # from member window
                member_id = self.member["member_id"]
                member_name = f"{self.member['first_name']} {self.member['last_name']}"
            elif self.member_dropdown:  # all-member mode
                member_id = self.member_dropdown.currentData()
                member_name = self.member_dropdown.currentText()
            else:
                QMessageBox.warning(self, "Missing Info", "Please select a member.")
                return

        from models.donation_model import add_donation_payment
        success, data = add_donation_payment(member_id, donation_type, amount, comment, donor_name, donor_phone)

        if success:
            donor_display = member_name if member_id else f"{donor_name} ({donor_phone})"
            receipt_text = (
                f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                f"Transaction ID: {data['transaction_id']}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Transaction Type: Donation\n"
                f"Donor: {donor_display}\n"
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