import os
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from database.db_connection import get_connection
from config.db_config import DB_CONFIG


class BackupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Church Database Backup")
        self.setMinimumSize(600, 300)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # --- Title ---
        title_label = QLabel("<h2>💾 Church Database Backup</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # --- Info ---
        info_label = QLabel(
            f"<b>Database:</b> {DB_CONFIG['database']}<br>"
            f"<b>Host:</b> {DB_CONFIG['host']}<br>"
            f"<b>User:</b> {DB_CONFIG['user']}"
        )
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # --- Backup Button ---
        backup_btn = QPushButton("🧷 Create Database Backup")
        backup_btn.setFixedHeight(50)
        backup_btn.clicked.connect(self.create_backup)
        layout.addWidget(backup_btn)

        # --- Status ---
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # --- Container ---
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # ----------------------------------------------------------------
    # CREATE BACKUP (PURE PYTHON)
    # ----------------------------------------------------------------
    def create_backup(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            db_name = DB_CONFIG['database']
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Database Backup",
                f"{db_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                "SQL Files (*.sql)"
            )

            if not file_path:
                return

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"-- ChurchApp Database Backup\n")
                f.write(f"-- Database: {db_name}\n")
                f.write(f"-- Created: {datetime.now()}\n\n")

                # Get all tables
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]

                for table in tables:
                    # --- Table structure ---
                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                    create_stmt = cursor.fetchone()[1]
                    f.write(f"\n-- Table structure for `{table}`\n")
                    f.write(f"DROP TABLE IF EXISTS `{table}`;\n{create_stmt};\n\n")

                    # --- Table data ---
                    cursor.execute(f"SELECT * FROM `{table}`")
                    rows = cursor.fetchall()
                    if not rows:
                        continue

                    columns = [desc[0] for desc in cursor.description]
                    f.write(f"-- Data for table `{table}`\n")
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append("NULL")
                            else:
                                # escape quotes
                                values.append("'" + str(val).replace("'", "''") + "'")
                        insert_stmt = f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                        f.write(insert_stmt)

            QMessageBox.information(
                self, "Backup Successful", f"✅ Backup saved to:\n{file_path}"
            )
            self.status_label.setText(f"Backup completed: {os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.critical(
                self, "Backup Error", f"❌ Failed to create backup:\n{str(e)}"
            )

        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass
