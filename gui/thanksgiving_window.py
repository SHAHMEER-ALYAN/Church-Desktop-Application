from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox
)
from datetime import datetime
from models.thanksgiving_model import (
    add_thanksgiving,
    get_thanksgivings_by_member,
    get_all_thanksgivings
)
from models.member_model import get_all_members
from gui.receipt_dialog import ReceiptDialog
import app_state


class ThanksgivingWindow(QMainWindow):
    def __init__(self, member=None):
        super().__init__()
        self.setWindowTitle("Thanksgiving Offerings")
        self.setMinimumSize(900, 600)

        # --- Member handling ---
        if not member or not member.get("member_id"):
            self.member = {"member_id": None, "first_name": "All", "last_name": "Members"}
            self.all_members_mode = True
        else:
            self.member = member
            self.all_members_mode = False

        layout = QVBoxLayout()

        # --- Member Dropdown (for All-Members Mode) ---
        if self.all_members_mode:
            self.member_dropdown = QComboBox()
            self.member_dropdown.addItem("Select Member", None)
            for m in get_all_members():
                self.member_dropdown.addItem(f"{m['first_name']} {m['last_name']}", m["member_id"])
            self.member_dropdown.currentIndexChanged.connect(self.on_member_change)
            layout.addWidget(QLabel("Select Member:"))
            layout.addWidget(self.member_dropdown)
        else:
            member_name = f"{self.member['first_name']} {self.member['last_name']}"
            layout.addWidget(QLabel(f"Member: {member_name}"))

        # --- Input fields ---
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount (Rs.)")

        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Enter purpose / thanksgiving comment")

        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Purpose / Comment:"))
        layout.addWidget(self.comment_input)

        # --- Buttons ---
        self.add_btn = QPushButton("Add Thanksgiving Offering")
        self.add_btn.clicked.connect(self.save_thanksgiving)
        layout.addWidget(self.add_btn)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date", "Member", "Purpose", "Amount", "Comment", "Transaction ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # --- Container ---
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_thanksgivings()

    # --- Reload thanksgiving records ---
    def load_thanksgivings(self):
        if self.all_members_mode:
            records = get_all_thanksgivings()
        else:
            records = get_thanksgivings_by_member(self.member["member_id"])

        self.table.setRowCount(0)
        for t in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t.get("date", "-"))))
            member_name = f"{t.get('first_name', '')} {t.get('last_name', '')}".strip() or "-"
            self.table.setItem(row, 1, QTableWidgetItem(member_name))
            self.table.setItem(row, 2, QTableWidgetItem(t.get("purpose", "-")))
            self.table.setItem(row, 3, QTableWidgetItem(f"Rs. {t.get('amount', 0):.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(t.get("comment", "")))
            self.table.setItem(row, 5, QTableWidgetItem(str(t.get("transaction_id", "-"))))

    # --- When user changes member in dropdown ---
    def on_member_change(self):
        selected_member_id = self.member_dropdown.currentData()
        if selected_member_id:
            from models.member_model import search_member_by_id
            result = search_member_by_id(selected_member_id)
            if result:
                self.member = result[0]
                self.all_members_mode = False
                self.load_thanksgivings()

    # --- Save thanksgiving offering ---
    def save_thanksgiving(self):
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return

        purpose = self.comment_input.toPlainText().strip()

        # Determine member_id
        if self.all_members_mode:
            member_id = self.member_dropdown.currentData()
            if not member_id:
                QMessageBox.warning(self, "Missing Data", "Please select a member first.")
                return
        else:
            member_id = self.member["member_id"]

        comment = self.comment_input.toPlainText().strip()
        success, transaction_id = add_thanksgiving(member_id, amount, purpose, comment)

        if success:
            member_name = (
                f"{self.member['first_name']} {self.member['last_name']}"
                if not self.all_members_mode
                else self.member_dropdown.currentText()
            )

            receipt_text = (
                f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                f"Transaction ID: {transaction_id}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Transaction Type: Thanksgiving\n"
                f"Member: {member_name}\n"
                f"Amount: Rs. {amount:.2f}\n"
                f"Purpose: {purpose}\n"
                f"Entered By: {app_state.current_user['full_name']}\n"
                "--------------------------------\n"
                "Thank you for your thanksgiving offering!"
            )

            ReceiptDialog("Thanksgiving Receipt", receipt_text).exec()
            QMessageBox.information(self, "Success", "Thanksgiving recorded successfully.")
            self.amount_input.clear()
            self.comment_input.clear()
            self.load_thanksgivings()
        else:
            QMessageBox.warning(self, "Error", "Failed to record thanksgiving offering.")
