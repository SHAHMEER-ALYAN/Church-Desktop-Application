from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from models.transaction_model import get_filtered_transactions, get_transaction_summary
from datetime import datetime

class TransactionViewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transaction Viewer & Report")
        self.resize(1100, 700)

        main_layout = QVBoxLayout()

        # --- Filters ---
        filter_layout = QHBoxLayout()
        self.year_filter = QComboBox()
        self.year_filter.addItem("All")
        current_year = datetime.now().year
        for y in range(current_year, current_year - 10, -1):
            self.year_filter.addItem(str(y))

        self.month_filter = QComboBox()
        self.month_filter.addItem("All")
        months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
        for m in months:
            self.month_filter.addItem(m)

        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems(["Membership", "Tithe", "Donation", "Bag_offering", "Parking", "Thanksgiving", "Expense"])

        self.expense_filter = QComboBox()
        self.expense_filter.addItem("All Expense Types")
        self.expense_filter.addItems([
            "Repair & Maintenance", "Utilities", "Water", "Event", "Fuel",
            "Staff Salary", "Clergy Allowances", "Refreshment", "Office Expenses",
            "Financial Support", "Staff Loan", "Pastor Loan", "Diocese Loan"
        ])

        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.load_transactions)

        filter_layout.addWidget(QLabel("Year:"))
        filter_layout.addWidget(self.year_filter)
        filter_layout.addWidget(QLabel("Month:"))
        filter_layout.addWidget(self.month_filter)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("Expense Type:"))
        filter_layout.addWidget(self.expense_filter)
        filter_layout.addWidget(self.apply_filter_btn)

        main_layout.addLayout(filter_layout)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Transaction ID", "Date", "Type", "Member", "Amount", "User", "Comments"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        # --- Summary Labels ---
        summary_layout = QHBoxLayout()
        self.total_income_label = QLabel("Total Income: Rs. 0.00")
        self.total_expense_label = QLabel("Total Expense: Rs. 0.00")
        self.net_balance_label = QLabel("Net Balance: Rs. 0.00")
        summary_layout.addWidget(self.total_income_label)
        summary_layout.addWidget(self.total_expense_label)
        summary_layout.addWidget(self.net_balance_label)
        main_layout.addLayout(summary_layout)

        # --- Container ---
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Initial load
        self.load_transactions()

    def load_transactions(self):
        year = self.year_filter.currentText()
        month = self.month_filter.currentText()
        tr_type = self.type_filter.currentText()
        exp_type = self.expense_filter.currentText()

        transactions = get_filtered_transactions(year, month, tr_type, exp_type)
        summary = get_transaction_summary(transactions)

        # Update Table
        self.table.setRowCount(0)
        for t in transactions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t['transaction_id'])))
            self.table.setItem(row, 1, QTableWidgetItem(str(t['transaction_date'])))
            self.table.setItem(row, 2, QTableWidgetItem(t['transaction_type']))
            self.table.setItem(row, 3, QTableWidgetItem(t.get('member_name', '-')))
            amount_item = QTableWidgetItem(f"{t['amount']:.2f}")
            if t['amount'] < 0:
                amount_item.setForeground(Qt.red)
            else:
                amount_item.setForeground(Qt.darkGreen)
            self.table.setItem(row, 4, amount_item)
            self.table.setItem(row, 5, QTableWidgetItem(t.get('user_name', '-')))
            self.table.setItem(row, 6, QTableWidgetItem(t.get('comments', '')))

        # Update Summary
        self.total_income_label.setText(f"Total Income: Rs. {summary['income']:.2f}")
        self.total_expense_label.setText(f"Total Expense: Rs. {summary['expense']:.2f}")
        self.net_balance_label.setText(f"Net Balance: Rs. {summary['net']:.2f}")
