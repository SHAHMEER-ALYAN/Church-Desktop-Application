from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtCore import Qt
from datetime import datetime

class ReceiptDialog(QDialog):
    def __init__(self, title: str, receipt_text: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(500, 550)

        layout = QVBoxLayout()
        self.text_box = QTextEdit()
        self.text_box.setPlainText(receipt_text)
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

        # Buttons
        button_layout = QHBoxLayout()
        self.print_btn = QPushButton("🖨 Print Receipt")
        self.print_btn.clicked.connect(self.print_receipt)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.print_btn)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def print_receipt(self):
        """Send the displayed receipt to a connected printer."""
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.Accepted:
            self.text_box.print_(printer)
            QMessageBox.information(self, "Print", "✅ Receipt sent to printer successfully.")
