from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView, QLineEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from models.transaction_model import get_filtered_transactions, get_transaction_summary
from datetime import datetime
import pandas as pd  # 🟩 NEW


class TransactionViewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transaction Viewer & Report")
        self.resize(1200, 750)

        main_layout = QVBoxLayout()

        # -------------------------
        # 🔍 Search Section
        # -------------------------
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Transaction ID to search...")
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_transaction)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.load_transactions)

        search_layout.addWidget(QLabel("Search by Transaction ID:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_btn)

        main_layout.addLayout(search_layout)

        # -------------------------
        # Filter Section
        # -------------------------
        filter_layout = QHBoxLayout()
        self.year_filter = QComboBox()
        self.year_filter.addItem("All")
        current_year = datetime.now().year
        for y in range(current_year, current_year - 10, -1):
            self.year_filter.addItem(str(y))

        self.month_filter = QComboBox()
        self.month_filter.addItem("All")
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        for m in months:
            self.month_filter.addItem(m)

        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems([
            "Membership", "Tithe", "Donations", "Bag_offering", "Parking", "Thanksgiving", "Expense"
        ])

        self.expense_filter = QComboBox()
        self.expense_filter.addItem("All Expense Types")
        self.expense_filter.addItems([
            "Repair & Maintenance", "Utilities", "Water", "Event", "Fuel",
            "Staff Salary", "Clergy Allowances", "Refreshment", "Office Expenses",
            "Financial Support", "Staff Loan", "Pastor Loan", "Diocese Loan"
        ])

        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.load_transactions)

        # 🟩 NEW: Export Button
        self.export_btn = QPushButton("📊 Export to Excel")
        self.export_btn.clicked.connect(self.export_to_excel)

        filter_layout.addWidget(QLabel("Year:"))
        filter_layout.addWidget(self.year_filter)
        filter_layout.addWidget(QLabel("Month:"))
        filter_layout.addWidget(self.month_filter)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(QLabel("Expense Type:"))
        filter_layout.addWidget(self.expense_filter)
        filter_layout.addWidget(self.apply_filter_btn)
        filter_layout.addWidget(self.export_btn)  # 🟩 Added here

        main_layout.addLayout(filter_layout)

        # -------------------------
        # Table Section
        # -------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Transaction ID", "Date", "Type", "Member", "Amount", "User", "Comments"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        # -------------------------
        # Summary Section
        # -------------------------
        summary_layout = QHBoxLayout()
        self.total_income_label = QLabel("Total Income: Rs. 0.00")
        self.total_expense_label = QLabel("Total Expense: Rs. 0.00")
        self.net_balance_label = QLabel("Net Balance: Rs. 0.00")
        summary_layout.addWidget(self.total_income_label)
        summary_layout.addWidget(self.total_expense_label)
        summary_layout.addWidget(self.net_balance_label)
        main_layout.addLayout(summary_layout)

        # -------------------------
        # Container Setup
        # -------------------------
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Track last loaded transactions
        self.current_transactions = []

        # Initial Load
        self.load_transactions()

    # -------------------------------------------------
    # 🔄 Load and Display Transactions
    # -------------------------------------------------
    def load_transactions(self):
        year = self.year_filter.currentText()
        month = self.month_filter.currentText()
        tr_type = self.type_filter.currentText()
        exp_type = self.expense_filter.currentText()

        transactions = get_filtered_transactions(year, month, tr_type, exp_type)
        summary = get_transaction_summary(transactions)

        self.current_transactions = transactions  # 🟩 store current data
        self.populate_table(transactions)

        # Update Summary
        self.total_income_label.setText(f"Total Income: Rs. {summary['income']:.2f}")
        self.total_expense_label.setText(f"Total Expense: Rs. {summary['expense']:.2f}")
        self.net_balance_label.setText(f"Net Balance: Rs. {summary['net']:.2f}")

    # -------------------------------------------------
    # 🔍 Search by Transaction ID
    # -------------------------------------------------
    def search_transaction(self):
        search_id = self.search_input.text().strip()
        if not search_id:
            QMessageBox.warning(self, "Input Required", "Please enter a Transaction ID to search.")
            return

        results = [t for t in self.current_transactions if search_id.lower() in str(t["transaction_id"]).lower()]

        if not results:
            QMessageBox.information(self, "No Results", f"No transaction found with ID: {search_id}")
            return

        self.populate_table(results)

    # -------------------------------------------------
    # 📋 Populate Table Helper
    # -------------------------------------------------
    def populate_table(self, transactions):
        self.table.setRowCount(0)
        for t in transactions:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t["transaction_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(t["transaction_date"])))
            self.table.setItem(row, 2, QTableWidgetItem(t["transaction_type"]))
            self.table.setItem(row, 3, QTableWidgetItem(t.get("member_name", "-")))

            amount_item = QTableWidgetItem(f"{t['amount']:.2f}")
            if t["amount"] < 0:
                amount_item.setForeground(Qt.red)
            else:
                amount_item.setForeground(Qt.darkGreen)
            self.table.setItem(row, 4, amount_item)

            self.table.setItem(row, 5, QTableWidgetItem(t.get("user_name", "-")))
            self.table.setItem(row, 6, QTableWidgetItem(t.get("comments", "")))

    # -------------------------------------------------
    # 🟩 Export to Excel
    # -------------------------------------------------
    def export_to_excel(self):
        if not self.current_transactions:
            QMessageBox.warning(self, "No Data", "No transactions available to export.")
            return

        # Choose file name
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File", "transactions.xlsx", "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        # Convert data to DataFrame
        df = pd.DataFrame(self.current_transactions)

        # Export to Excel
        try:
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Export Successful", f"Transactions exported to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"An error occurred:\n{e}")
