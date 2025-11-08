from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QDialogButtonBox, QMessageBox,
    QListWidget, QLabel, QAbstractItemView
)
from PySide6.QtCore import Qt
from datetime import datetime

# --- UPDATED IMPORTS ---
# Import the function and constants from the new db_connection file
from database.db_connection import get_paid_months_for_year, MONTH_NAMES


class PaymentInputWindow(QDialog):
    def __init__(self, member_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Record Payment for {member_info['first_name']} {member_info['last_name']}")
        self.member_info = member_info
        self.payment_data = None
        self.ALL_MONTHS = MONTH_NAMES  # Use the imported constants

        self.setModal(True)
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        form = QFormLayout()

        # --- Year Selection ---
        self.year_input = QComboBox()
        current_year = datetime.now().year
        # Populate with current year and the two previous years
        years = [str(y) for y in range(current_year, current_year - 3, -1)]
        self.year_input.addItems(years)
        self.year_input.setCurrentText(str(current_year))
        self.year_input.currentIndexChanged.connect(self._update_month_list)
        form.addRow("Payment Year:", self.year_input)

        # --- Unpaid Month Selection ---
        self.month_list = QListWidget()
        # MultiSelection allows clicking/dragging without Ctrl/Shift
        self.month_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.month_list.setFixedHeight(150)

        main_layout.addLayout(form)
        main_layout.addWidget(QLabel("Select Unpaid Month(s):"))
        main_layout.addWidget(self.month_list)

        # --- Amount Input ---
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter total amount (must be divisible by months selected)")

        amount_layout = QFormLayout()
        amount_layout.addRow("Total Amount (Rs.):", self.amount_input)
        main_layout.addLayout(amount_layout)

        # --- Dialog Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_payment)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self._update_month_list()  # Initial population

    def _update_month_list(self):
        """Filters out paid months for the selected year using live DB data."""
        selected_year = int(self.year_input.currentText())
        member_id = self.member_info['member_id']

        # CALLS THE LIVE DB FUNCTION
        paid_months = get_paid_months_for_year(member_id, selected_year)

        # Filtering logic
        unpaid_months = [month for month in self.ALL_MONTHS if month not in paid_months]

        self.month_list.clear()
        self.month_list.addItems(unpaid_months)

    def accept_payment(self):
        """
        Validates input, checks for amount divisibility, and prepares data.
        """
        selected_months = [item.text() for item in self.month_list.selectedItems()]
        amount_text = self.amount_input.text().strip()

        if not selected_months:
            QMessageBox.critical(self, "Input Error", "Please select at least one unpaid month.")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter a valid total amount greater than zero.")
            return

        # --- DIVISION LOGIC & VALIDATION ---
        num_months = len(selected_months)

        # Check if the amount is perfectly divisible by the number of months
        if amount % num_months != 0:
            QMessageBox.critical(
                self,
                "Amount Error",
                f"The total amount (Rs. {amount:.2f}) is not perfectly divisible by the number of selected months ({num_months}). Please adjust the amount."
            )
            return

        # Calculate the per-month amount
        amount_per_month = amount / num_months
        # -----------------------------------

        # Store the data and accept the dialog (closes the window)
        self.payment_data = {
            'member_id': self.member_info['member_id'],
            'year': int(self.year_input.currentText()),
            'selected_months': selected_months,
            'total_amount': amount,
            'amount_per_month': amount_per_month,
        }
        self.accept()