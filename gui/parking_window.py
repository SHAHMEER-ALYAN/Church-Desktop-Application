from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QCheckBox,
    QListWidget, QAbstractItemView
)
from datetime import datetime
from models.parking_model import add_parking_payment, get_all_parking, search_parking_by_vehicle
from gui.receipt_dialog import ReceiptDialog
from models.member_model import search_member_by_card_number, search_member_by_id
import app_state


class ParkingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parking Fee Management")
        self.setMinimumSize(950, 700)

        main_layout = QVBoxLayout()

        # --- Search Section ---
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter Vehicle # to search (e.g. LEB-1234)")
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_parking)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_parking)

        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.refresh_btn)
        main_layout.addLayout(search_layout)

        # --- Add Parking Inputs ---

        # 1. Member Lookup
        self.member_checkbox = QCheckBox("Is Church Member?")
        self.member_checkbox.toggled.connect(self.toggle_member_mode)
        self.member_search = QLineEdit()
        self.member_search.setPlaceholderText("Search Member by Card No / ID (Press Enter)")
        self.member_search.returnPressed.connect(self.lookup_member)
        self.member_search.setVisible(False)
        self.member_info_label = QLabel("")

        self.selected_member_id = None

        # 2. Vehicle Details
        self.vehicle_number = QLineEdit()
        self.vehicle_number.setPlaceholderText("Enter vehicle number (e.g. LEB-1234)")
        self.vehicle_number.textChanged.connect(self.uppercase_vehicle_number)

        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Enter phone number (optional)")

        self.vehicle_type = QComboBox()
        self.vehicle_type.addItems(["Car", "Bike", "Rickshaw"])
        self.vehicle_type.currentTextChanged.connect(self.set_default_price)

        # 3. Payment Period (Multi-select Month)
        self.month_list = QListWidget()
        self.month_list.setSelectionMode(QAbstractItemView.MultiSelection)
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.month_list.addItems(months)
        self.month_list.setFixedHeight(100)  # Limit height
        # Connect selection change to update price automatically
        self.month_list.itemSelectionChanged.connect(self.set_default_price)

        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for y in range(current_year - 2, current_year + 3):
            self.year_combo.addItem(str(y))
        self.year_combo.setCurrentText(str(current_year))

        # 4. Amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter total amount")

        self.add_btn = QPushButton("Add Parking Payment")
        self.add_btn.clicked.connect(self.save_parking)

        # --- Layout Assembly ---
        main_layout.addWidget(self.member_checkbox)
        main_layout.addWidget(self.member_search)
        main_layout.addWidget(self.member_info_label)

        form_layout = QHBoxLayout()

        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("Vehicle Number:"))
        left_col.addWidget(self.vehicle_number)
        left_col.addWidget(QLabel("Phone Number:"))
        left_col.addWidget(self.phone_number)
        left_col.addWidget(QLabel("Vehicle Type:"))
        left_col.addWidget(self.vehicle_type)

        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("Payment Months (Select Multiple):"))
        right_col.addWidget(self.month_list)
        right_col.addWidget(QLabel("Payment Year:"))
        right_col.addWidget(self.year_combo)
        right_col.addWidget(QLabel("Total Amount (Rs):"))
        right_col.addWidget(self.amount_input)

        form_layout.addLayout(left_col)
        form_layout.addLayout(right_col)
        main_layout.addLayout(form_layout)

        main_layout.addWidget(self.add_btn)

        # --- Parking Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Trans ID", "Date", "Vehicle #", "Type", "Amount", "Payment Period", "Phone", "Member"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Load all records initially
        self.load_parking()
        # Initialize default price
        self.set_default_price()

    # --- Logic Functions ---

    def toggle_member_mode(self, checked):
        """Show/Hide member search based on checkbox."""
        self.member_search.setVisible(checked)
        self.member_info_label.setVisible(checked)
        if not checked:
            self.selected_member_id = None
            self.member_info_label.setText("")
            self.member_search.clear()
        self.set_default_price()  # Update price based on new mode

    def lookup_member(self):
        """Find member to apply discount."""
        card_no = self.member_search.text().strip()
        if not card_no: return

        member = None
        if card_no.isdigit() and len(card_no) < 6:
            member = search_member_by_id(card_no)
            if member and isinstance(member, list): member = member[0]
        else:
            member = search_member_by_card_number(card_no)
            if member and isinstance(member, list): member = member[0]

        if member:
            self.selected_member_id = member['member_id']
            self.member_info_label.setText(f"✅ Member Found: {member['first_name']} {member['last_name']}")
            self.member_info_label.setStyleSheet("color: green;")
            self.set_default_price()
        else:
            self.selected_member_id = None
            self.member_info_label.setText("❌ Member Not Found")
            self.member_info_label.setStyleSheet("color: red;")
            self.set_default_price()

    def uppercase_vehicle_number(self):
        current = self.vehicle_number.text()
        self.vehicle_number.blockSignals(True)
        self.vehicle_number.setText(current.upper())
        self.vehicle_number.blockSignals(False)

    def set_default_price(self):
        vtype = self.vehicle_type.currentText()
        is_member = self.selected_member_id is not None

        # Calculate based on selected months count
        selected_count = len(self.month_list.selectedItems())
        if selected_count == 0: selected_count = 1  # Default to 1 for calculation display

        price_per_month = 0
        if vtype == "Bike":
            price_per_month = 1000
        elif vtype == "Rickshaw":
            price_per_month = 1500
        elif vtype == "Car":
            if is_member:
                price_per_month = 2000
            else:
                price_per_month = 3000

        total_price = price_per_month * selected_count
        self.amount_input.setText(str(total_price))

    # --- Load Parking Table ---
    def load_parking(self):
        data = get_all_parking()
        self.populate_table(data)

    def populate_table(self, data):
        self.table.setRowCount(0)
        for row in data:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(row.get("transaction_id", "-"))))
            self.table.setItem(r, 1, QTableWidgetItem(str(row["transaction_date"])))
            self.table.setItem(r, 2, QTableWidgetItem(row["vehicle_number"]))
            self.table.setItem(r, 3, QTableWidgetItem(row["vehicle_type"]))
            self.table.setItem(r, 4, QTableWidgetItem(f"{row['amount']:.2f}"))

            period = f"{row.get('payment_month', '')} {row.get('payment_year', '')}"
            self.table.setItem(r, 5, QTableWidgetItem(period.strip()))

            self.table.setItem(r, 6, QTableWidgetItem(str(row.get("phone_number", ""))))
            name = f"{row.get('first_name', '')} {row.get('last_name', '')}".strip()
            self.table.setItem(r, 7, QTableWidgetItem(name if name else "-"))

    # --- Search Parking by Vehicle Number ---
    def search_parking(self):
        vehicle_number = self.search_box.text().strip().upper()
        if not vehicle_number:
            QMessageBox.warning(self, "Input Error", "Please enter a vehicle number to search.")
            return

        data = search_parking_by_vehicle(vehicle_number)
        if not data:
            QMessageBox.information(self, "No Results", f"No records found for '{vehicle_number}'.")
        self.populate_table(data)

    # --- Save Parking Payment ---
    def save_parking(self):
        number = self.vehicle_number.text().strip().upper()
        phone = self.phone_number.text().strip()
        vtype = self.vehicle_type.currentText()
        amount_text = self.amount_input.text().strip()
        year = self.year_combo.currentText()

        # Get selected months
        selected_items = self.month_list.selectedItems()
        months = [item.text() for item in selected_items]

        if not number:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid vehicle number.")
            return
        if not months:
            QMessageBox.warning(self, "Input Error", "Please select at least one month.")
            return
        if not amount_text or not amount_text.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return

        total_amount = float(amount_text)

        if total_amount % len(months) != 0:
            QMessageBox.warning(self, "Amount Warning",
                                "Total amount does not divide evenly by months selected. Proceeding anyway.")

        member_id = self.selected_member_id

        success, results = add_parking_payment(member_id, number, phone, vtype, total_amount, months, year)

        if success:
            # --- Generate Combined Receipt ---
            months_str = ", ".join([r['month'] for r in results])
            # Use the first transaction ID as reference for the combined receipt
            trans_ref = results[0]['transaction_id'] if results else "N/A"

            receipt_text = (
                f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                f"Transaction Ref: {trans_ref}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Transaction Type: Parking Fee\n"
                f"Vehicle Type: {vtype}\n"
                f"Vehicle Number: {number}\n"
                f"Payment Period: {months_str} {year}\n"
                f"Total Amount Paid: Rs. {total_amount:.2f}\n"
                f"Phone Number: {phone or 'N/A'}\n"
                f"Entered By: {app_state.current_user['full_name']}\n"
                "---------------------------------\n"
                f"Thank you for your contribution!"
            )

            receipt_dialog = ReceiptDialog("Parking Receipt", receipt_text)
            receipt_dialog.exec()

            self.vehicle_number.clear()
            self.phone_number.clear()
            self.month_list.clearSelection()
            self.set_default_price()
            self.load_parking()
        else:
            QMessageBox.critical(self, "Error", f"Failed to add parking: {results}")