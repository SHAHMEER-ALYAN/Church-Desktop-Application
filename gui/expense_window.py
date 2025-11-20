from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout, QComboBox,QTableWidget, QHeaderView,
    QLineEdit, QPushButton, QMessageBox, QLabel, QDialog, QTextEdit, QTableWidgetItem
)

from PySide6.QtCore import QSize, Qt

import app_state
from gui.receipt_dialog import ReceiptDialog
from models.expense_model import add_expense, get_all_expenses


class ExpenseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense Management")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        # --- Expense Types List ---
        self.EXPENSE_TYPES = [
            "Repair & Maintenance", "Utilities", "Water (Tanker & Drinking Water)",
            "Event", "Fuel", "Staff Salary",
            "Pastor Allowance (Entertainment Allowance)",
            "Church Guest Fund",
            "Clergy assessment", # <-- UPDATED: Changed from "Clergy Allowances"
            "Refreshment", "Office Expenses", "Financial Support",
            "Staff Loan", "Pastor Loan", "Diocese Loan"
        ]

        # --- Add Expense Section ---
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.EXPENSE_TYPES)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")

        self.receipt_input = QLineEdit()
        self.receipt_input.setPlaceholderText("Enter receipt number")

        self.comments_input = QTextEdit()
        self.comments_input.setPlaceholderText("Enter comments...")

        self.add_btn = QPushButton("Add Expense")
        self.add_btn.clicked.connect(self.save_expense)

        layout.addWidget(QLabel("Expense Type:"))
        layout.addWidget(self.type_combo)
        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Receipt Number:"))
        layout.addWidget(self.receipt_input)
        layout.addWidget(QLabel("Comments:"))
        layout.addWidget(self.comments_input)
        layout.addWidget(self.add_btn)

        # --- Expense Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date", "Type", "Amount", "Receipt", "Entered By", "Comments"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_expenses()

    def load_expenses(self):
        data = get_all_expenses()
        self.table.setRowCount(0)
        for row in data:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row['transaction_date'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row['expense_type']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row['amount'])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(row['receipt_number'])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(row['entered_by'])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(row['comments'])))

    def save_expense(self):
        expense_type = self.type_combo.currentText()
        amount_text = self.amount_input.text().strip()
        receipt = self.receipt_input.text().strip()
        comments = self.comments_input.toPlainText().strip()

        # --- Validate amount ---
        if not amount_text or not amount_text.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return

        amount = float(amount_text)

        success, transaction_id = add_expense(expense_type, amount, receipt, comments)
        if success:
            receipt_text = (
                f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                f"Transaction ID: {transaction_id}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Transaction Type: Expense\n"
                f"Expense Category: {expense_type}\n"
                f"Amount: -Rs. {abs(amount):.2f}\n"
                f"Receipt #: {receipt}\n"
                f"Comments: {comments}\n"
                f"Entered By: {app_state.current_user['full_name']}\n"
                "---------------------------------\n"
                "Recorded successfully.\n\n\n"
                "Prepared by: _____________________\n\n"
                "Parish Secretary: _____________________\n\n"
                "Approved by Parish Incharge: _____________________\n\n"
                "Received by: _____________________ \n"
            )
            receipt_dialog = ReceiptDialog("Expense Receipt", receipt_text)
            receipt_dialog.exec()
            self.load_expenses()

            # Optional: Clear input fields after successful save
            self.amount_input.clear()
            self.receipt_input.clear()
            self.comments_input.clear()