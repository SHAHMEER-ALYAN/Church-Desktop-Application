from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QDialog,
    QFormLayout, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QPushButton, QMenu
from models.member_model import search_member_by_name, add_member, get_all_members, search_member_by_id
# from gui.membership_window import TitheWindow
from gui.membership_window import MembershipWindow
from gui.donation_window import DonationWindow

class MemberWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Member Management")
        self.setMinimumSize(900, 600)

        main_layout = QVBoxLayout()

        # --- Search Section ---
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter name, ID, CNIC (13 digits), or Card # ...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_member)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_all_members)

        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.refresh_button)
        main_layout.addLayout(search_layout)

        # --- Table to display members ---
        self.member_table = QTableWidget()
        self.member_table.setColumnCount(10)
        self.member_table.setHorizontalHeaderLabels([
            "ID", "First Name", "Last Name", "Email", "Phone",
            "Membership Card #", "NIC Number", "Date of Birth", "Join Date", "Actions"
        ])
        self.member_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.member_table)

        # --- Add Member Button ---
        self.add_member_btn = QPushButton("Add New Member")
        self.add_member_btn.clicked.connect(self.open_add_member_dialog)
        main_layout.addWidget(self.add_member_btn)

        # --- Container Setup ---
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Load data initially
        self.load_all_members()

    # ---------------- LOAD ALL MEMBERS ----------------
    def load_all_members(self):
        """Fetch and display all members in the table."""
        members = get_all_members()
        self.populate_table(members)

    # ---------------- SEARCH MEMBER ----------------
    # ---------------- SEARCH MEMBER ----------------
    def search_member(self):
        keyword = self.search_box.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Search Error", "Please enter a name, ID, card number, or CNIC to search.")
            return

        members = []

        # --- Search by Member ID (purely numeric and short) ---
        if keyword.isdigit() and len(keyword) < 6:
            members = search_member_by_id(int(keyword))

        # --- Search by CNIC (Pakistani 13-digit number) ---
        elif keyword.isdigit() and len(keyword) == 13:
            from models.member_model import search_member_by_cnic
            members = search_member_by_cnic(keyword)

        # --- Search by Membership Card Number (contains letters or dashes) ---
        elif any(ch.isalpha() for ch in keyword) or "-" in keyword:
            from models.member_model import search_member_by_card_number
            members = search_member_by_card_number(keyword)

        # --- Otherwise, search by name ---
        else:
            members = search_member_by_name(keyword)

        if not members:
            QMessageBox.information(self, "No Results", "No members found for your search criteria.")
            self.member_table.setRowCount(0)
            return

        self.populate_table(members)

    # ---------------- POPULATE TABLE ----------------
    def populate_table(self, members):
        self.member_table.setRowCount(0)
        for row_index, member in enumerate(members):
            self.member_table.insertRow(row_index)
            self.member_table.setItem(row_index, 0, QTableWidgetItem(str(member["member_id"])))
            self.member_table.setItem(row_index, 1, QTableWidgetItem(member["first_name"]))
            self.member_table.setItem(row_index, 2, QTableWidgetItem(member["last_name"]))
            self.member_table.setItem(row_index, 3, QTableWidgetItem(member["email"]))
            self.member_table.setItem(row_index, 4, QTableWidgetItem(member["phone"]))
            self.member_table.setItem(row_index, 5, QTableWidgetItem(member["membership_card_no"]))
            self.member_table.setItem(row_index, 6, QTableWidgetItem(member["nic_no"]))
            self.member_table.setItem(row_index, 7, QTableWidgetItem(str(member["date_of_birth"])))
            self.member_table.setItem(row_index, 8, QTableWidgetItem(str(member["join_date"])))

            # --- Action Button (+) ---
            action_btn = QPushButton("+")
            action_btn.clicked.connect(lambda checked, m=member: self.show_action_menu(m))
            self.member_table.setCellWidget(row_index, 9, action_btn)

    def show_action_menu(self, member):
        menu = QMenu()
        menu.addAction("Membership", lambda: self.open_membership_window(member))
        menu.addAction("Tithe", lambda: self.open_tithe_window(member))
        menu.addAction("Donation", lambda: self.open_donation_window(member))
        menu.addAction("Thanksgiving", lambda: self.open_thanksgiving_window(member))
        menu.exec()

    def open_membership_window(self, member):
        """Open the membership management window for this member."""
        self.membership_window = MembershipWindow(member)
        # self.membership_window = MembershipWindow(member)
        self.membership_window.show()

    def open_tithe_window(self, member):
        from gui.tithe_window import TitheWindow
        self.tithe_window = TitheWindow(member)
        self.tithe_window.show()

    # ---------------- ADD MEMBER DIALOG ----------------
    def open_add_member_dialog(self):
        """Open dialog to add a new member."""
        dialog = AddMemberDialog(self)
        if dialog.exec():
            self.load_all_members()  # refresh after adding new member

    def open_donation_window(self, member):
        from gui.donation_window import DonationWindow
        self.donation_window = DonationWindow(member)
        self.donation_window.show()

    def open_thanksgiving_window(self, member):
        from gui.thanksgiving_window import ThanksgivingWindow
        self.thanksgiving_window = ThanksgivingWindow(member)
        self.thanksgiving_window.show()

# ---------------- ADD MEMBER DIALOG ----------------
class AddMemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Member")
        self.setFixedSize(400, 500)

        layout = QFormLayout()

        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.membership_card_no = QLineEdit()
        self.nic_no = QLineEdit()
        self.dob = QDateEdit()
        self.dob.setCalendarPopup(True)
        self.dob.setDate(QDate.currentDate())
        self.join_date = QDateEdit()
        self.join_date.setCalendarPopup(True)
        self.join_date.setDate(QDate.currentDate())

        self.submit_btn = QPushButton("Add Member")
        self.submit_btn.clicked.connect(self.add_member_to_db)

        layout.addRow("First Name:", self.first_name)
        layout.addRow("Last Name:", self.last_name)
        layout.addRow("Email:", self.email)
        layout.addRow("Phone:", self.phone)
        layout.addRow("Membership Card #:", self.membership_card_no)
        layout.addRow("NIC Number:", self.nic_no)
        layout.addRow("Date of Birth:", self.dob)
        layout.addRow("Join Date:", self.join_date)
        layout.addRow("", self.submit_btn)

        self.setLayout(layout)

    def add_member_to_db(self):
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        email = self.email.text().strip()
        phone = self.phone.text().strip()
        membership_card_no = self.membership_card_no.text().strip()
        nic_no = self.nic_no.text().strip()
        dob = self.dob.date().toString("yyyy-MM-dd")
        join_date = self.join_date.date().toString("yyyy-MM-dd")

        if not all([first_name, last_name, email, phone, membership_card_no, nic_no]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        success, message = add_member(
            first_name, last_name, email, phone, dob, join_date, nic_no, membership_card_no
        )

        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()  # close dialog and refresh table
        else:
            QMessageBox.warning(self, "Duplicate Member", message)

    def add_member_to_db(self):
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        email = self.email.text().strip()
        phone = self.phone.text().strip()
        nic_no = self.nic_no.text().strip()
        membership_card_no = self.membership_card_no.text().strip()
        dob = self.dob.date().toString("yyyy-MM-dd")
        join_date = self.join_date.date().toString("yyyy-MM-dd")

        if not all([first_name, last_name, email, phone]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        success, message = add_member(first_name, last_name, email, phone, dob, join_date, nic_no, membership_card_no)
        if success:
            QMessageBox.information(self, "Success", message)
            self.accept()  # close dialog and trigger refresh
        else:
            QMessageBox.warning(self, "Duplicate Member", message)
