from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QMessageBox, QLabel, QDialog
)
from datetime import datetime

# --- IMPORTANT IMPORTS ---
# Ensure these functions exist in your models/membership_model.py
from models.membership_model import  add_membership_payment
from models.member_model import search_member_by_card_number as search_member_by_card
from gui.receipt_dialog import ReceiptDialog
from gui.payment_input_window import PaymentInputWindow


class MembershipLookupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Find Membership by Card Number")
        self.setMinimumSize(400, 250)

        layout = QVBoxLayout()
        form = QFormLayout()

        # --- Card Number Input ---
        self.card_input = QLineEdit()
        self.card_input.setPlaceholderText("Enter membership card number")
        form.addRow("Card Number:", self.card_input)

        # --- Search Button ---
        self.search_btn = QPushButton("Find Member")
        self.search_btn.clicked.connect(self.lookup_member)
        form.addRow("", self.search_btn)

        layout.addLayout(form)

        # --- Info Label ---
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _get_current_user_id(self):
        """
        Placeholder: Returns the ID of the currently logged-in user.
        You MUST replace this with your actual session retrieval logic.
        """
        return 1

    def _generate_receipt_text(self, member, payment_data, transaction_id):
        """
        Generates the receipt text, now correctly using the transaction_id.
        """

        receipt = (
            f"--- Church Membership Payment Receipt ---\n\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Transaction ID: {transaction_id}\n\n"
            f"Member: {member.get('first_name', '')} {member.get('last_name', '')}\n"
            f"Card No: {member.get('membership_card_no', 'N/A')}\n"
            f"Member ID: {member.get('member_id', 'N/A')}\n\n"
            f"Year: {payment_data['year']}\n"
            f"Month(s) Paid: {', '.join(payment_data['selected_months'])}\n"
            f"Amount Per Month: Rs. {payment_data['amount_per_month']:.2f}\n"
            f"Total Amount Paid: Rs. {payment_data['total_amount']:.2f}\n\n"
            f"-----------------------------------------\n"
            f"Thank you for your continued support.\n"
        )
        return receipt

    def lookup_member(self):
        """Validate card, open PaymentInputWindow, then show ReceiptDialog."""
        card_number = self.card_input.text().strip()
        if not card_number:
            QMessageBox.warning(self, "Input Error", "Please enter a membership card number.")
            return

        # Search member by card number
        member = search_member_by_card(card_number)

        # --- Start of Modification Block ---
        if not member:
            # Check if the failure was due to a missing member or a deeper issue
            QMessageBox.warning(self, "Not Found", "No member found with this card number.")
            self.info_label.setText("<b style='color:red;'>No matching member found.</b>")
            return

        # Display found member info
        status_text = member.get('status', 'Online')
        status_color = 'green' if status_text == 'Online' else 'orange'

        self.info_label.setText(
            f"<b>Member Found:</b><br>"
            f"Name: {member['first_name']} {member['last_name']}<br>"
            f"Status: <b style='color:{status_color};'>{status_text}</b>"  # Display the status
        )
        # --- End of Modification Block ---

        # --- STEP 1: OPEN PAYMENT INPUT DIALOG ---
        input_dialog = PaymentInputWindow(member, parent=self)

        if input_dialog.exec() == QDialog.Accepted:
            payment_data = input_dialog.payment_data

            # Extract the arguments expected by the model function
            member_id = payment_data['member_id']
            months = payment_data['selected_months']  # Assuming this is a list of month names
            year = payment_data['year']
            total_amount = payment_data['total_amount']

            # --- STEP 2: PROCESS AND SAVE PAYMENT ---
            # Call the model function with the correct arguments
            # Note: We expect a tuple (status, result) based on your function definition
            status, result = add_membership_payment(member_id, months, year, total_amount)

            if not status:
                QMessageBox.critical(self, "Database Error", f"Failed to record payment: {result}")
                self.info_label.setText("<b style='color:red;'>Payment failed.</b>")
                return

            # If successful, 'result' is the list of transaction dictionaries
            transactions_list = result

            # Since you insert multiple records, use the first transaction ID for the receipt display
            # and format the receipt to show the total amount paid.
            transaction_id = transactions_list[0]['transaction_id'] if transactions_list else 'N/A'

            # --- STEP 3: SHOW RECEIPT DIALOG ---
            dialog_title = "Payment Receipt Successful"

            # Pass the first transaction ID and the original payment_data
            receipt_content = self._generate_receipt_text(member, payment_data, transaction_id)

            self.receipt_dialog = ReceiptDialog(dialog_title, receipt_content)
            self.receipt_dialog.exec()

            self.card_input.clear()