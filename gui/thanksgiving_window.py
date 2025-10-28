from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QMessageBox
)
from datetime import datetime
import app_state
from gui.receipt_dialog import ReceiptDialog
from models.thanksgiving_model import get_thanksgivings_by_member, add_thanksgiving


class ThanksgivingWindow(QMainWindow):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.setWindowTitle(f"Thanksgiving - {member['first_name']} {member['last_name']}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # --- Add Thanksgiving Section ---
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")

        self.purpose_input = QComboBox()
        self.purpose_input.addItems([
            "General Thanksgiving",
            "Birthday",
            "Wedding Anniversary",
            "New Job / Promotion",
            "Healing",
            "Other Blessings"
        ])

        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Add a comment or note (optional)...")

        self.add_btn = QPushButton("Add Thanksgiving")
        self.add_btn.clicked.connect(self.save_thanksgiving)

        layout.addWidget(QLabel("Purpose:"))
        layout.addWidget(self.purpose_input)
        layout.addWidget(QLabel("Amount (Rs):"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Comment:"))
        layout.addWidget(self.comment_input)
        layout.addWidget(self.add_btn)

        # --- Thanksgiving Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Date", "Purpose", "Amount", "Comment", "Transaction ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_thanksgivings()

    def load_thanksgivings(self):
        records = get_thanksgivings_by_member(self.member["member_id"])
        self.table.setRowCount(0)

        for row, t in enumerate(records):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t["date"])))
            self.table.setItem(row, 1, QTableWidgetItem(t["purpose"]))
            self.table.setItem(row, 2, QTableWidgetItem(f"Rs. {t['amount']:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(t.get("comment", "")))
            self.table.setItem(row, 4, QTableWidgetItem(t["transaction_id"]))

    def save_thanksgiving(self):
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid amount.")
            return

        purpose = self.purpose_input.currentText()
        comment = self.comment_input.toPlainText().strip()

        success, data = add_thanksgiving(self.member["member_id"], purpose, amount, comment)

        if success:
            t = data
            receipt_text = (
                f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                f"Transaction ID: {t['transaction_id']}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Transaction Type: Thanksgiving\n"
                f"Member: {self.member['first_name']} {self.member['last_name']} (ID: {self.member['member_id']})\n"
                f"Amount: Rs. {amount}\n"
                f"Purpose: {purpose}\n"
                f"Comment: {comment}\n"
                f"Entered By: {app_state.current_user['full_name']}\n"
                "---------------------------------\n"
                "Thank you for your thanksgiving offering!"
            )
            ReceiptDialog("Thanksgiving Receipt", receipt_text).exec()

            QMessageBox.information(self, "Success", "Thanksgiving offering added successfully.")
            self.load_thanksgivings()
        else:
            QMessageBox.warning(self, "Error", "Failed to record thanksgiving offering.")
