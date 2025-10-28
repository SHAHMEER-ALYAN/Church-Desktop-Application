from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate
from models.tithe_model import get_tithes_by_member, add_tithe_payment
from gui.receipt_dialog import ReceiptDialog
from datetime import datetime


class TitheWindow(QMainWindow):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.setWindowTitle(f"Tithe - {member['first_name']} {member['last_name']}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # Table of all tithes for this member
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Tithe ID", "Month", "Year", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Tithe")
        self.add_btn.clicked.connect(self.open_add_tithe_dialog)
        btn_layout.addWidget(self.add_btn)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_tithes()

    def load_tithes(self):
        """Load all tithes from DB."""
        tithes = get_tithes_by_member(self.member["member_id"])

        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tithe ID", "Transaction ID", "Month", "Year", "Amount"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for t in tithes:
            # Convert tithe_month (a DATE field) → month name
            if t["tithe_month"]:
                try:
                    if isinstance(t["tithe_month"], str):
                        month_name = datetime.strptime(t["tithe_month"], "%Y-%m-%d").strftime("%B")
                    else:
                        month_name = t["tithe_month"].strftime("%B")
                except Exception:
                    month_name = str(t["tithe_month"])
            else:
                month_name = "Unknown"

            transaction_id = str(t.get("transaction_id", "N/A"))

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t["tithe_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(transaction_id))
            self.table.setItem(row, 2, QTableWidgetItem(month_name))
            self.table.setItem(row, 3, QTableWidgetItem(str(t["tithe_year"])))
            self.table.setItem(row, 4, QTableWidgetItem(f"Rs. {t['amount']:.2f}"))

    def open_add_tithe_dialog(self):
        dialog = AddTitheDialog(self.member)
        dialog.exec()
        self.load_tithes()


class AddTitheDialog(QDialog):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.setWindowTitle("Add Tithe")
        self.setFixedSize(400, 500)

        layout = QFormLayout()

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter total amount")

        # --- Year Selector ---
        self.year_select = QComboBox()
        current_year = QDate.currentDate().year()
        for y in range(current_year, current_year - 5, -1):
            self.year_select.addItem(str(y))
        self.year_select.currentTextChanged.connect(self.refresh_months_list)

        # --- Month Multi-Select ---
        self.month_list = QListWidget()
        self.month_list.setSelectionMode(QAbstractItemView.MultiSelection)

        # --- Buttons ---
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.save_tithe)

        layout.addRow("Total Amount:", self.amount_input)
        layout.addRow("Year:", self.year_select)
        layout.addRow("Select Months:", self.month_list)
        layout.addRow("", self.submit_btn)
        self.setLayout(layout)

        # Initialize with current year's available months
        self.refresh_months_list()

    def refresh_months_list(self):
        """Load months that are not yet paid for this member and year."""
        from models.tithe_model import get_tithes_by_member

        year = int(self.year_select.currentText())
        all_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # Get existing tithes
        existing_tithes = get_tithes_by_member(self.member["member_id"])
        paid_months = [
            datetime.strptime(str(t["tithe_month"]), "%Y-%m-%d").strftime("%B")
            for t in existing_tithes
            if t["tithe_year"] == year
        ]

        # Filter unpaid months
        unpaid_months = [m for m in all_months if m not in paid_months]

        # Populate the list
        self.month_list.clear()
        for m in unpaid_months:
            self.month_list.addItem(QListWidgetItem(m))

        if not unpaid_months:
            self.month_list.addItem(QListWidgetItem("(All months paid for this year)"))
            self.month_list.setDisabled(True)
        else:
            self.month_list.setDisabled(False)

    def save_tithe(self):
        try:
            total_amount = float(self.amount_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid amount.")
            return

        selected_months = [item.text() for item in self.month_list.selectedItems() if not item.text().startswith("(")]
        if not selected_months:
            QMessageBox.warning(self, "Missing Data", "Please select at least one month.")
            return

        year = int(self.year_select.currentText())
        monthly_amount = total_amount / len(selected_months)

        # Ensure no decimal remainder
        if total_amount % len(selected_months) != 0:
            QMessageBox.warning(self, "Invalid Amount", "Amount must divide evenly by number of months.")
            return

        success, results = add_tithe_payment(self.member, selected_months, year, monthly_amount)

        if success:
            for r in results:
                receipt_text = (
                    f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                    f"Transaction ID: {r['transaction_id']}\n"
                    f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"Transaction Type: Tithe\n"
                    f"Member: {self.member['first_name']} {self.member['last_name']} (ID: {self.member['member_id']})\n"
                    f"Amount: Rs. {monthly_amount}\n"
                    f"Month: {r['month']} {r['year']}\n"
                    f"Entered By: Admin\n"
                    "--------------------------------\n"
                    "Thank you for your tithe contribution!"
                )
                receipt_dialog = ReceiptDialog("Tithe Receipt", receipt_text)
                receipt_dialog.exec()

            QMessageBox.information(self, "Success", "Tithe added successfully.")
            self.close()
        else:
            QMessageBox.warning(self, "Duplicate Entry", "Some selected months already have a tithe entry.")
