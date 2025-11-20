from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QAbstractItemView,
    QCheckBox, QLabel  # Added QCheckBox, QLabel
)
from PySide6.QtCore import Qt, QDate

import app_state
from models.member_model import get_all_members
from models.tithe_model import get_tithes_by_member, add_tithe_payment
from gui.receipt_dialog import ReceiptDialog
from datetime import datetime


class TitheWindow(QMainWindow):
    def __init__(self, member=None):
        super().__init__()

        # 🟢 If no member passed, show data for all members
        if not member or not member.get("member_id"):
            self.member = {"member_id": None, "first_name": "All", "last_name": "Members"}
            self.all_members_mode = True
        else:
            self.member = member
            self.all_members_mode = False

        self.setWindowTitle(f"Tithe - {self.member['first_name']} {self.member['last_name']}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # Table of all tithes for this member
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Tithe ID", "Transaction ID", "Member/Donor", "Month", "Year", "Amount"
        ])
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
        if self.all_members_mode:
            from models.tithe_model import get_all_tithes
            tithes = get_all_tithes()
        else:
            from models.tithe_model import get_tithes_by_member
            tithes = get_tithes_by_member(self.member["member_id"])

        self.table.setRowCount(0)

        for t in tithes:
            # Extract month name safely
            if t.get("tithe_month"):
                try:
                    if isinstance(t["tithe_month"], str):
                        month_name = datetime.strptime(t["tithe_month"], "%Y-%m-%d").strftime("%B")
                    else:
                        month_name = t["tithe_month"].strftime("%B")
                except Exception:
                    month_name = str(t["tithe_month"])
            else:
                month_name = "-"

            transaction_id = str(t.get("transaction_id", "N/A"))

            # Logic to show Member Name OR Non-Member Donor Name
            first = t.get('first_name')
            last = t.get('last_name')
            donor = t.get('donor_name')

            if first or last:
                member_name = f"{first or ''} {last or ''}".strip()
            elif donor:
                member_name = f"{donor} (Non-Member)"
            else:
                member_name = "Unknown"

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(t.get("tithe_id", "-"))))
            self.table.setItem(row, 1, QTableWidgetItem(transaction_id))
            self.table.setItem(row, 2, QTableWidgetItem(member_name))
            self.table.setItem(row, 3, QTableWidgetItem(month_name))
            self.table.setItem(row, 4, QTableWidgetItem(str(t.get("tithe_year", "-"))))
            self.table.setItem(row, 5, QTableWidgetItem(f"Rs. {t.get('amount', 0):.2f}"))

    def open_add_tithe_dialog(self):
        dialog = AddTitheDialog(self.member)
        dialog.exec()
        self.load_tithes()


class AddTitheDialog(QDialog):
    def __init__(self, member):
        super().__init__()
        self.member = member
        self.setWindowTitle("Add Tithe")
        self.setFixedSize(400, 600)

        layout = QFormLayout()

        # --- Non-Member Checkbox ---
        # Only available if we are in "All Members" mode (not adding for specific member)
        self.non_member_cb = QCheckBox("Non-Member Tithe")
        if not member.get("member_id"):
            layout.addRow("", self.non_member_cb)
            self.non_member_cb.toggled.connect(self.toggle_mode)

        # --- Member Dropdown ---
        self.member_label = QLabel("Select Member:")
        self.member_dropdown = QComboBox()

        if not member.get("member_id"):
            from models.member_model import get_all_members
            members = get_all_members()
            for m in members:
                full_name = f"{m['first_name']} {m['last_name']}"
                self.member_dropdown.addItem(full_name, m["member_id"])

            self.member_dropdown.currentIndexChanged.connect(self.refresh_months_list)
            layout.addRow(self.member_label, self.member_dropdown)

        # --- Non-Member Fields (Hidden by default) ---
        self.donor_name_label = QLabel("Donor Name:")
        self.donor_name = QLineEdit()
        self.donor_name.setPlaceholderText("Enter Name")

        self.donor_phone_label = QLabel("Donor Phone:")
        self.donor_phone = QLineEdit()
        self.donor_phone.setPlaceholderText("Enter Phone")

        layout.addRow(self.donor_name_label, self.donor_name)
        layout.addRow(self.donor_phone_label, self.donor_phone)

        # --- Total Amount ---
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter total amount (Rs.)")
        layout.addRow("Total Amount:", self.amount_input)

        # --- Year Selector ---
        self.year_select = QComboBox()
        current_year = QDate.currentDate().year()
        for y in range(current_year, current_year - 5, -1):
            self.year_select.addItem(str(y))
        self.year_select.currentTextChanged.connect(self.refresh_months_list)
        layout.addRow("Year:", self.year_select)

        # --- Month Multi-Select ---
        self.month_list = QListWidget()
        self.month_list.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addRow("Select Months:", self.month_list)

        # --- Submit Button ---
        self.submit_btn = QPushButton("Submit Tithe")
        self.submit_btn.clicked.connect(self.save_tithe)
        layout.addRow("", self.submit_btn)

        self.setLayout(layout)

        # Initial State
        self.toggle_mode()
        self.refresh_months_list()

    def toggle_mode(self):
        """Show/Hide fields based on Non-Member checkbox."""
        is_non_member = self.non_member_cb.isChecked() if hasattr(self, 'non_member_cb') else False

        # Toggle Member Dropdown visibility
        if hasattr(self, 'member_dropdown'):
            self.member_dropdown.setVisible(not is_non_member)
            self.member_label.setVisible(not is_non_member)

        # Toggle Donor Fields visibility
        self.donor_name.setVisible(is_non_member)
        self.donor_name_label.setVisible(is_non_member)
        self.donor_phone.setVisible(is_non_member)
        self.donor_phone_label.setVisible(is_non_member)

        # Refresh months (Non-members see all months, Members see unpaid)
        self.refresh_months_list()

    def get_selected_member_id(self):
        """Return selected member_id (handles both modes)."""
        if self.member.get("member_id"):
            return self.member["member_id"]
        elif hasattr(self, 'member_dropdown') and not self.non_member_cb.isChecked():
            return self.member_dropdown.currentData()
        return None

    def refresh_months_list(self):
        """Refresh the list of months."""
        self.month_list.clear()
        all_months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        # If Non-Member mode, show all months without checking DB history
        if hasattr(self, 'non_member_cb') and self.non_member_cb.isChecked():
            for m in all_months:
                self.month_list.addItem(QListWidgetItem(m))
            self.month_list.setDisabled(False)
            return

        # Existing Logic for Members (Check paid history)
        from models.tithe_model import get_tithes_by_member
        member_id = self.get_selected_member_id()

        if not member_id:
            self.month_list.addItem(QListWidgetItem("(Please select a member)"))
            self.month_list.setDisabled(True)
            return

        year = int(self.year_select.currentText())
        existing_tithes = get_tithes_by_member(member_id)
        paid_months = []

        for t in existing_tithes:
            try:
                if t["tithe_year"] == year:
                    month_name = datetime.strptime(str(t["tithe_month"]), "%Y-%m-%d").strftime("%B")
                    paid_months.append(month_name)
            except Exception:
                continue

        unpaid_months = [m for m in all_months if m not in paid_months]

        for m in unpaid_months:
            self.month_list.addItem(QListWidgetItem(m))

        if not unpaid_months:
            self.month_list.addItem(QListWidgetItem("(All months paid for this year)"))
            self.month_list.setDisabled(True)
        else:
            self.month_list.setDisabled(False)

    def save_tithe(self):
        """Save the tithe record(s) into the database."""
        is_non_member = self.non_member_cb.isChecked() if hasattr(self, 'non_member_cb') else False

        member_data = {}

        if is_non_member:
            # VALIDATE NON-MEMBER INPUT
            name = self.donor_name.text().strip()
            phone = self.donor_phone.text().strip()
            if not name:
                QMessageBox.warning(self, "Input Error", "Donor Name is required.")
                return

            # Construct dummy member object with ID as None
            member_data = {
                'member_id': None,
                'first_name': name,
                'last_name': '(Non-Member)',
                'phone': phone
            }
        else:
            # VALIDATE MEMBER INPUT
            member_id = self.get_selected_member_id()
            if not member_id:
                QMessageBox.warning(self, "Missing Member", "Please select a member.")
                return

            from models.member_model import get_member_by_id
            member_data = get_member_by_id(member_id)

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

        if total_amount % len(selected_months) != 0:
            QMessageBox.warning(self, "Invalid Amount", "Amount must divide evenly by number of months.")
            return

        from models.tithe_model import add_tithe_payment
        success, results = add_tithe_payment(member_data, selected_months, year, monthly_amount)

        if success:
            for r in results:
                receipt_text = (
                    f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                    f"Transaction ID: {r['transaction_id']}\n"
                    f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    f"Transaction Type: Tithe\n"
                    f"Donor: {member_data['first_name']} {member_data.get('last_name', '')}\n"
                    f"Amount: Rs. {monthly_amount}\n"
                    f"Month: {r['month']} {r['year']}\n"
                    f"Entered By: {app_state.current_user['full_name']}\n"
                    "--------------------------------\n"
                    "Thank you for your tithe contribution!"
                )
                receipt_dialog = ReceiptDialog("Tithe Receipt", receipt_text)
                receipt_dialog.exec()

            QMessageBox.information(self, "Success", "Tithe added successfully.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", f"Failed to add tithe: {results}")