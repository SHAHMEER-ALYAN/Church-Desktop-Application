from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout
)
from datetime import datetime
from models.parking_model import add_parking_payment, get_all_parking, search_parking_by_vehicle
from gui.receipt_dialog import ReceiptDialog
import app_state


class ParkingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parking Fee Management")
        self.setMinimumSize(950, 600)

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
        self.vehicle_number = QLineEdit()
        self.vehicle_number.setPlaceholderText("Enter vehicle number (e.g. LEB-1234)")
        self.vehicle_number.textChanged.connect(self.uppercase_vehicle_number)

        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Enter phone number (optional)")

        self.vehicle_type = QComboBox()
        self.vehicle_type.addItems(["Car", "Bike"])
        self.vehicle_type.currentTextChanged.connect(self.set_default_price)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter fee amount")
        self.set_default_price()  # default amount

        self.add_btn = QPushButton("Add Parking Payment")
        self.add_btn.clicked.connect(self.save_parking)

        main_layout.addWidget(QLabel("Vehicle Number:"))
        main_layout.addWidget(self.vehicle_number)
        main_layout.addWidget(QLabel("Phone Number:"))
        main_layout.addWidget(self.phone_number)
        main_layout.addWidget(QLabel("Vehicle Type:"))
        main_layout.addWidget(self.vehicle_type)
        main_layout.addWidget(QLabel("Amount (Rs):"))
        main_layout.addWidget(self.amount_input)
        main_layout.addWidget(self.add_btn)

        # --- Parking Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Transaction ID", "Date", "Vehicle #", "Type", "Amount", "Phone", "Member"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Load all records initially
        self.load_parking()

    # --- Auto Capitalize Vehicle Number ---
    def uppercase_vehicle_number(self):
        current = self.vehicle_number.text()
        self.vehicle_number.blockSignals(True)
        self.vehicle_number.setText(current.upper())
        self.vehicle_number.blockSignals(False)

    # --- Set Default Price ---
    def set_default_price(self):
        vtype = self.vehicle_type.currentText()
        self.amount_input.setText("3000" if vtype == "Car" else "1500")

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
            self.table.setItem(r, 5, QTableWidgetItem(str(row.get("phone_number", ""))))
            name = f"{row.get('first_name', '')} {row.get('last_name', '')}".strip()
            self.table.setItem(r, 6, QTableWidgetItem(name if name else "-"))

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

        if not number:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid vehicle number.")
            return
        if not amount_text or not amount_text.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return

        member_id = app_state.current_user.get("member_id") if app_state.current_user else None
        success, transaction_id = add_parking_payment(member_id, number, phone, vtype, float(amount_text))

        if success:
            # --- Generate Receipt ---
            receipt_text = (
                f"--- CHURCH MANAGEMENT SYSTEM ---\n"
                f"Transaction ID: {transaction_id}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"Transaction Type: Parking Fee\n"
                f"Vehicle Type: {vtype}\n"
                f"Vehicle Number: {number}\n"
                f"Amount Paid: Rs. {amount_text}\n"
                f"Phone Number: {phone or 'N/A'}\n"
                f"Entered By: {app_state.current_user['full_name']}\n"
                "---------------------------------\n"
                f"Thank you for your contribution!"
            )

            receipt_dialog = ReceiptDialog("Parking Receipt", receipt_text)
            receipt_dialog.exec()

            self.vehicle_number.clear()
            self.phone_number.clear()
            self.set_default_price()
            self.load_parking()
