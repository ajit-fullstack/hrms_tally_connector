"""
UI with adjusted heights - smaller first row, larger second row
"""

import asyncio, logging, os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QGroupBox, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QDateEdit,
    QMessageBox, QDialog, QTextEdit, 
    QStatusBar, QGridLayout, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt, QDate, QTimer, Signal, QThread
from PySide6.QtGui import QFont, QColor, QTextCursor

from src.controllers import MainController
from src.models import ConnectorStatus, LogLevel, LogEntry, TallyConfig, BusyConfig
from src.data_manager import EnhancedDataView

from datetime import datetime
from utils.drop_down import country, state


def get_log_path():
    base_dir = os.path.join(os.getenv("APPDATA"), "TallyConnector")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "error.txt")

logging.basicConfig(filename=get_log_path(), format="%(asctime)s - %(message)s", level=logging.DEBUG)


class AsyncWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, coro):
        super().__init__()
        self.coro = coro

    def run(self):
        try:
            result = asyncio.run(self.coro)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class StatusIndicator(QLabel):
    """Custom status indicator widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.set_status(ConnectorStatus.DISCONNECTED)
    
    def set_status(self, status: ConnectorStatus):
        """Set status with color"""
        colors = {
            ConnectorStatus.CONNECTED: "#4CAF50",
            ConnectorStatus.DISCONNECTED: "#F44336",
            ConnectorStatus.PENDING: "#FF9800",
            ConnectorStatus.ERROR: "#9C27B0"
        }
        color = colors.get(status, "#757575")
        self.setStyleSheet(f"""
            StatusIndicator {{
                background-color: {color};
                border-radius: 6px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }}
        """)
        self.setToolTip(status.value.title())

class DashboardTab(QWidget):
    """Dashboard tab widget"""
    
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.init_ui()
        self.update_status()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Accounting Connector")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2196F3; margin: 20px 0;")
        
        layout.addWidget(title)
        
        # Connector Status Cards
        status_layout = QHBoxLayout()
        
        # Tally Status Card
        tally_card = self.create_status_card(
            "📊 Tally Connector",
            "Configure and manage Tally connections",
            "tally"
        )
        
        # BUSY Status Card
        busy_card = self.create_status_card(
            "💼 BUSY Connector",
            "Configure and manage BUSY connections",
            "busy"
        )
        
        # Logs Status Card
        logs_card = self.create_status_card(
            "📋 Logs",
            "View application logs and history",
            "logs"
        )
        
        status_layout.addWidget(tally_card)
        status_layout.addWidget(busy_card)
        status_layout.addWidget(logs_card)
        
        layout.addLayout(status_layout)
        
        # Last Sync Section
        sync_group = QGroupBox("Last Sync Information")
        sync_layout = QVBoxLayout()
        
        self.last_sync_label = QLabel("Last sync: Never")
        self.last_sync_label.setStyleSheet("font-size: 14px; padding: 10px;")
        
        sync_layout.addWidget(self.last_sync_label)
        sync_group.setLayout(sync_layout)
        
        layout.addWidget(sync_group)
        
        # Application Info
        info_group = QGroupBox("Application Information")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "This application allows you to configure and manage connections "
            "to Tally and BUSY accounting software.\n\n"
            "Features:\n"
            "• Configure connection settings\n"
            "• Select companies and data types\n"
            "• Export accounting data\n"
            "• Sync data between systems\n"
            "• View detailed logs\n"
            "• Enhanced data tables with scrollable views"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("padding: 10px;")
        
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        
        layout.addWidget(info_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        self.setLayout(layout)
    
    def create_status_card(self, title: str, description: str, connector_type: str) -> QFrame:
        """Create a status card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        card.setMinimumWidth(200)
        
        layout = QVBoxLayout()
        
        # Title with status indicator
        title_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # Add status indicator only for tally and busy
        if connector_type in ["tally", "busy"]:
            self.status_indicator = StatusIndicator()
            if connector_type == "tally":
                self.tally_status_indicator = self.status_indicator
            elif connector_type == "busy":
                self.busy_status_indicator = self.status_indicator
            
            title_layout.addWidget(title_label)
            title_layout.addStretch()
            title_layout.addWidget(self.status_indicator)
        else:
            title_layout.addWidget(title_label)
            title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(desc_label)
        
        # Status text for connectors
        if connector_type in ["tally", "busy"]:
            self.status_label = QLabel("Status: Checking...")
            layout.addWidget(self.status_label)
        
        card.setLayout(layout)
        return card
    
    def update_status(self):
        """Update status from controller"""
        # Update Tally status
        tally_status = self.controller.tally_status
        self.tally_status_indicator.set_status(tally_status)
        
        # Update BUSY status
        busy_status = self.controller.busy_status
        self.busy_status_indicator.set_status(busy_status)
        
        # Update last sync time
        last_sync = self.controller.get_last_sync_time()
        if last_sync:
            self.last_sync_label.setText(f"Last sync: {last_sync.strftime('%Y-%m-%d %H:%M:%S')}")

class TallyConnectorTab(QWidget):
    """Tally connector with reduced first row height"""
    
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.config = TallyConfig()
        self.init_ui()
        
        # Connect signals
        self.controller.tally_status_changed.connect(self.on_status_changed)

        # Manually added 
        self.exported_data = dict()
    
    def init_ui(self):
        """Initialize UI with smaller first row"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)  # Reduced spacing
        
        # Top Section: First Row - SMALLER HEIGHT
        top_section = QWidget()
        top_section.setMaximumHeight(200)  # Reduced from ~250-300 to 200
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)  # Reduced spacing

        # ===============================
        # Group Box
        # ===============================
        conn_group = QGroupBox("🧮 Connection Settings")
        conn_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #cccccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 2px;
                min-width: 600px;
                max-width: 600px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #333333;
            }
        """)

        conn_layout = QVBoxLayout()
        conn_layout.setSpacing(6)

        INPUT_HEIGHT = 20

        # ===============================
        # Cloud Username + Password
        # ===============================
        cloud_layout = QGridLayout()
        cloud_layout.setHorizontalSpacing(8)
        cloud_layout.setVerticalSpacing(6)

        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.username_input = QLineEdit("")
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(INPUT_HEIGHT)
        self.username_input.setFixedWidth(200)
        self.username_input.setStyleSheet("font-size: 12px; padding: 2px;")

        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.password_input = QLineEdit("")
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(INPUT_HEIGHT)
        self.password_input.setFixedWidth(200)
        self.password_input.setStyleSheet("font-size: 12px; padding: 2px;")

        # Same row layout (saves height)
        cloud_layout.addWidget(username_label, 0, 0)
        cloud_layout.addWidget(self.username_input, 0, 1)

        cloud_layout.addWidget(password_label, 0, 2)
        cloud_layout.addWidget(self.password_input, 0, 3)

        cloud_layout.setColumnStretch(1, 1)
        cloud_layout.setColumnStretch(3, 1)

        conn_layout.addLayout(cloud_layout)

        # ===============================
        # Host + Port
        # ===============================
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(8)
        form_layout.setVerticalSpacing(6)

        # Host
        host_label = QLabel("Host:")
        host_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.host_input = QLineEdit("localhost")
        self.host_input.setFixedHeight(INPUT_HEIGHT)
        self.host_input.setFixedWidth(200)
        self.host_input.setStyleSheet("font-size: 12px; padding: 2px;")

        # Port
        port_label = QLabel("Port:")
        port_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.port_input = QLineEdit("9000")
        self.port_input.setFixedHeight(INPUT_HEIGHT)
        self.port_input.setFixedWidth(200)
        self.port_input.setStyleSheet("font-size: 12px; padding: 2px;")

        form_layout.addWidget(host_label, 0, 0)
        form_layout.addWidget(self.host_input, 0, 1)
        form_layout.addWidget(port_label, 0, 2)
        form_layout.addWidget(self.port_input, 0, 3)

        form_layout.setColumnStretch(1, 1)
        conn_layout.addLayout(form_layout)

        # ===============================
        # Status + Test Button
        # ===============================
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        status_text = QLabel("Status:")
        status_text.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.status_label = QLabel("Not Connected")
        self.status_label.setStyleSheet(
            "color: #F44336; font-weight: bold; font-size: 12px;"
        )

        action_layout.addWidget(status_text)
        action_layout.addWidget(self.status_label)
        action_layout.addStretch()

        # Test Button (compact)
        self.test_btn = QPushButton("🔗 Test Connection")
        self.test_btn.setFixedHeight(30)
        self.test_btn.setFixedWidth(160)

        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 6px;   
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

        self.test_btn.clicked.connect(self.test_connection)

        action_layout.addWidget(self.test_btn)
        conn_layout.addLayout(action_layout)

        # ===============================
        # Final Apply
        # ===============================
        conn_group.setLayout(conn_layout)
        top_layout.addWidget(conn_group)


        # 2. Date Range Group - COMPACT
        date_group = QGroupBox("📅 Date Range")
        date_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #cccccc;
                border-radius: 6px;
                margin-top: 10px;
                padding: 12px;
                min-width: 500px;
                max-width: 500px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #333333;
            }
        """)
        
        date_layout = QVBoxLayout()
        date_layout.setSpacing(8)  # Reduced spacing
        
        # From date - COMPACT
        from_layout = QVBoxLayout()
        from_label = QLabel("From:")
        from_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        from_layout.addWidget(from_label)
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setMinimumHeight(30)  # Reduced from 35
        self.date_from.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        from_layout.addWidget(self.date_from)
        date_layout.addLayout(from_layout)
        
        # To date - COMPACT
        to_layout = QVBoxLayout()
        to_label = QLabel("To:")
        to_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        to_layout.addWidget(to_label)
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setMinimumHeight(30)  # Reduced from 35
        self.date_to.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        to_layout.addWidget(self.date_to)
        date_layout.addLayout(to_layout)
        
        date_group.setLayout(date_layout)
        top_layout.addWidget(date_group)
                
        # Action Buttons (Right side, in ONE COLUMN) - COMPACT
        action_widget = QWidget()
        action_layout = QVBoxLayout()
        action_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        action_layout.setSpacing(10)  # Reduced spacing
        
        self.export_btn = QPushButton("📤 Import Data")
        self.export_btn.setEnabled(False)
        self.export_btn.setMinimumHeight(38)  # Reduced from 45
        self.export_btn.setMinimumWidth(130)  # Reduced from 140
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 16px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.export_btn.clicked.connect(self.on_export_clicked)
        
        self.sync_btn = QPushButton("🔄 Sync")
        self.sync_btn.setEnabled(False)
        self.sync_btn.setMinimumHeight(38)  # Reduced from 45
        self.sync_btn.setMinimumWidth(130)  # Reduced from 140
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 16px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.sync_btn.clicked.connect(self.on_sync_clicked)
        
        # Add buttons vertically
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.sync_btn)
        
        action_widget.setLayout(action_layout)
        
        # Add action widget
        top_layout.addWidget(action_widget, 0, Qt.AlignLeft | Qt.AlignTop)
        
        top_section.setLayout(top_layout)
        main_layout.addWidget(top_section)
        
        # Bottom Section: Enhanced Data View - LARGER HEIGHT
        bottom_section = QWidget()
        bottom_layout = QVBoxLayout()
        
        # Section Title
        section_title = QLabel("📋 Preview")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #333333;
                padding: 0 0 8px 0;
            }
        """)
        bottom_layout.addWidget(section_title)
        
        # Enhanced Data View - WILL TAKE MORE SPACE
        self.data_view = EnhancedDataView()
        bottom_layout.addWidget(self.data_view, 1)  # Stretch factor 1 for data view
        
        bottom_section.setLayout(bottom_layout)
        
        # Add sections to main layout with stretch factors
        main_layout.addWidget(bottom_section, 1)  # Stretch factor 1 for remaining space
        
        self.setLayout(main_layout)
    
    def test_connection(self):
        """Test Tally connection"""
        host = self.host_input.text()
        user_name = self.username_input.text()
        password = self.password_input.text()

        try:
            port = int(self.port_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Port", "Please enter a valid port number")
            return
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Connecting...")
        
        # Call controller to test connection
        try:
            self.controller.connect_tally(host, port, user_name, password)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def on_status_changed(self, status: ConnectorStatus):
        """Handle status changes"""
        self.status_label.setText(status.value.title())
        
        if status == ConnectorStatus.CONNECTED:
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
            self.export_btn.setEnabled(True)
            self.sync_btn.setEnabled(True)
        elif status == ConnectorStatus.PENDING:
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 12px;")
        else:
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12px;")
            self.export_btn.setEnabled(False)
            self.sync_btn.setEnabled(False)
        
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔗 Test Connection")
    
    def on_export_clicked(self):
        # asyncio.run(self.export_data())
        self.export_btn.setEnabled(False)
        self.export_btn.setText("Importing...")

        self.worker = AsyncWorker(self.export_data())

        self.worker.finished.connect(self.on_export_success)
        self.worker.error.connect(self.on_export_error)

        self.worker.start()

    def on_export_success(self, result):
        self.enable_buttons()

    def on_export_error(self, error):
        QMessageBox.warning(self, "Error", error)
        self.enable_buttons()

    async def export_data(self):
        """Export Tally data"""

        # Collect configuration
        config = TallyConfig(
            host=self.host_input.text(),
            port=int(self.port_input.text()),
            company="",
            selected_data_types=[],
            date_from=self.date_from.date().toPython(),
            date_to=self.date_to.date().toPython()
        )

        # Disable buttons during export
        self.export_btn.setEnabled(False)
        self.sync_btn.setEnabled(False)
        self.export_btn.setText("Importing...")
                
        try:
            # Call controller to export
            success = await self.controller.export_tally_data(config)

            # Format data to show on ui
            formated_data = await self.format_data(success)
            self.exported_data = formated_data
            self.data_view.refresh_data(formated_data)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            QTimer.singleShot(500, self.enable_buttons)
            return
        
        # Re-enable buttons after delay
        QTimer.singleShot(500, self.enable_buttons)
        return success
    
    async def format_data(self, data):
        try:
            formated_data = {}

            # format ledger
            fomated_ledger_data = []
            for ledger in data.get('ledgers'):
                temp_dict = {}
                temp_dict.update(ledger)

                if ledger.get('ledgerState'):
                    if ledger.get('ledgerState').isdigit():
                        ledger_state = state[int(ledger.get('ledgerState'))]
                        temp_dict['ledgerState'] = ledger_state

                if ledger.get('ledgerCountry'):
                    if ledger.get('ledgerCountry').isdigit():
                        ledger_country = country[int(ledger.get('ledgerCountry'))]
                        temp_dict['ledgerCountry'] = ledger_country
                        
                fomated_ledger_data.append(temp_dict)

            formated_data['ledgers'] = fomated_ledger_data

            # format journal
            fomated_journal_data = []
            for journal in data.get('journal'):
                temp_dict = {}

                if journal.get('amount'):
                    voucher_date = datetime.strptime(journal.get('slary_date'), '%Y-%m-%d')
                    voucher_no = f"{journal.get('contact_no')}{voucher_date.strftime('%m%Y')}"
                    
                    temp_dict['voucher_no'] = voucher_no
                    temp_dict['voucher_date'] = voucher_date.strftime('%d-%m-%Y')
                    temp_dict['party_name'] = journal.get('employ_name')
                    temp_dict['nature'] = "Salary"
                    temp_dict['amount'] = float(journal.get('amount'))
                    temp_dict['narration'] = ""

                    fomated_journal_data.append(temp_dict)

            formated_data['journal'] = fomated_journal_data

            return formated_data
        except Exception as e:
            logging.exception(e)
    
    def on_sync_clicked(self):
        # asyncio.run(self.sync_data())
        self.sync_btn.setEnabled(False)
        self.sync_btn.setText("Syncing...")

        self.worker = AsyncWorker(self.sync_data())

        self.worker.finished.connect(self.on_sync_success)
        self.worker.error.connect(self.on_sync_error)

        self.worker.start()

    def on_sync_success(self, result):
        self.enable_buttons()

    def on_sync_error(self, error):
        QMessageBox.warning(self, "Error", error)
        self.enable_buttons()

    async def sync_data(self):
        """Sync Tally data"""

        # Collect configuration
        config = TallyConfig(
            host=self.host_input.text(),
            port=int(self.port_input.text()),
            company="",
            selected_data_types=[],
            date_from=self.date_from.date().toPython(),
            date_to=self.date_to.date().toPython()
        )

        # Disable buttons during sync
        self.export_btn.setEnabled(False)
        self.sync_btn.setEnabled(False)
        self.sync_btn.setText("Syncing...")
        
        try:
            # Call controller to sync
            await self.controller.sync_tally_data(config, self.exported_data)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            QTimer.singleShot(500, self.enable_buttons)
            return
        
        # Re-enable buttons after delay
        QTimer.singleShot(500, self.enable_buttons)
    
    def enable_buttons(self):
        """Re-enable action buttons"""
        if self.controller.tally_status == ConnectorStatus.CONNECTED:
            self.export_btn.setEnabled(True)
            self.sync_btn.setEnabled(True)
        
        self.export_btn.setText("📤 Import Data")
        self.sync_btn.setText("🔄 Sync")

class BusyConnectorTab(QWidget):
    """BUSY connector with reduced first row height"""
    
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.config = BusyConfig()
        self.init_ui()
        
        # Connect signals
        self.controller.busy_status_changed.connect(self.on_status_changed)

        # Manually added 
        self.exported_data = dict()
    
    def init_ui(self):
        """Initialize UI with smaller first row"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)  # Reduced spacing
        
        # Top Section: First Row - SMALLER HEIGHT
        top_section = QWidget()
        top_section.setMaximumHeight(200)  # Reduced from ~250-300 to 200
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)  # Reduced spacing
        
        # 1. Connection Settings Group - COMPACT
        conn_group = QGroupBox("💼 ODBC Connection Settings")
        conn_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #cccccc;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 2px;
                min-width: 400px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #333333;
            }
        """)
        
        conn_layout = QVBoxLayout()
        conn_layout.setSpacing(8)  # Reduced spacing
        
        # ORACLE INN Label - COMPACT
        oracle_label = QLabel("ORACLE INN:")
        oracle_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 12px;")
        conn_layout.addWidget(oracle_label)
        
        # DSN ComboBox - COMPACT
        dsn_layout = QHBoxLayout()
        dsn_label = QLabel("Idename:")
        dsn_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        dsn_layout.addWidget(dsn_label)
        self.dsn_combo = QComboBox()
        self.dsn_combo.addItems([
            "Account1", "Account2", "Account3", "Account4", "Account5",
            "Account6", "Account7", "Account8", "Account9", "Account10",
            "Account11", "Account12"
        ])
        self.dsn_combo.setMinimumHeight(30)  # Reduced from 35
        self.dsn_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                min-width: 180px;
                font-size: 12px;
            }
        """)
        dsn_layout.addWidget(self.dsn_combo)
        dsn_layout.addStretch()
        conn_layout.addLayout(dsn_layout)
        
        # Static Path Info - COMPACT
        static_label = QLabel("STATIC PATH:")
        static_label.setStyleSheet("font-weight: bold; color: #333333; font-size: 12px; margin-top: 6px;")
        conn_layout.addWidget(static_label)
        
        path_label = QLabel("Not in ABB directory")
        path_label.setStyleSheet("color: #666666; font-style: italic; font-size: 11px; margin-left: 8px;")
        conn_layout.addWidget(path_label)
        
        # Test Connection Button - COMPACT
        self.test_btn = QPushButton("🔗 Test Connection")
        self.test_btn.setMinimumHeight(35)  # Reduced from 40
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                margin-top: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.test_btn.clicked.connect(self.test_connection)
        conn_layout.addWidget(self.test_btn)
        
        # Connection Status - COMPACT
        status_layout = QHBoxLayout()
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        status_layout.addWidget(status_label)
        self.status_label = QLabel("Not Connected")
        self.status_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        conn_layout.addLayout(status_layout)
        
        conn_group.setLayout(conn_layout)
        top_layout.addWidget(conn_group)
        
        # 2. Date Range Group - COMPACT
        date_group = QGroupBox("📅 Date Range")
        date_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #cccccc;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
                min-width: 400px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #333333;
            }
        """)
        
        date_layout = QVBoxLayout()
        date_layout.setSpacing(8)  # Reduced spacing
        
        # From date - COMPACT
        from_layout = QVBoxLayout()
        from_label = QLabel("From:")
        from_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        from_layout.addWidget(from_label)
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat("dd/MM/yyyy")
        self.date_from.setMinimumHeight(30)  # Reduced from 35
        self.date_from.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        from_layout.addWidget(self.date_from)
        date_layout.addLayout(from_layout)
        
        # To date - COMPACT
        to_layout = QVBoxLayout()
        to_label = QLabel("To:")
        to_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        to_layout.addWidget(to_label)
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat("dd/MM/yyyy")
        self.date_to.setMinimumHeight(30)  # Reduced from 35
        self.date_to.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        to_layout.addWidget(self.date_to)
        date_layout.addLayout(to_layout)
        
        date_group.setLayout(date_layout)
        top_layout.addWidget(date_group)
        
        # 3. Data Selection Group - COMPACT
        data_group = QGroupBox("📊 Data Selection")
        data_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #cccccc;
                border-radius: 6px;
                background-color: #ffffff;
                min-width: 400px;
                max-width: 400px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: #333333;
            }
        """)
        
        outer_layout = QGridLayout()
        outer_layout.setSpacing(8)  # Reduced spacing
        outer_layout.setContentsMargins(12, 8, 12, 8)  # Reduced margins
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(140)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #ffffff;
            }
        """)

        scroll_container = QWidget()
        scroll_container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        data_layout = QGridLayout(scroll_container)
        data_layout.setSpacing(8)
        data_layout.setContentsMargins(4, 4, 4, 4)

        # Create checkboxes for data types with icons - 2 columns, COMPACT
        data_types = [
            ("Select All", "Select All"),
            ("📊 Ledgers", "Ledgers"),
            ("📦 Stocks", "Stocks"),
            ("💰 Sales", "Sales"),
            ("🛒 Purchase", "Purchase"),
            ("📝 Credit Note", "Credit Note"),
            ("📋 Debit Note", "Debit Note"),
            ("💵 Receipt", "Receipt"),
            ("💳 Payment", "Payment"),
            ("🔄 Contra", "Contra"),
            ("📒 Journal", "Journal"),
            ("📑 Sale Order", "Sale Order"),
            ("🧾 Purchase Order", "Purchase Order"),
            ("🏭 Stock Journal", "Stock Journal"),
            ("🚚 Delivery Challan", "Delivery Challan"),
        ]
        
        row, col = 0, 0
        self.data_checkboxes = []
        for icon_text, data_type in data_types:
            if data_type == "Select All":
                select_all_cb = QCheckBox(icon_text)
                select_all_cb.setToolTip("Check / Uncheck All")

                select_all_cb.setProperty("data_type", data_type)
                select_all_cb.setMinimumHeight(25)
                select_all_cb.setStyleSheet("""
                    QCheckBox {
                        font-weight: bold;
                        font-size: 13px;
                        padding: 6px;
                        border-radius: 4px;
                    }
                    QCheckBox:hover {
                        background-color: #f5f7fa;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                    }
                """)

                self.data_checkboxes.append(select_all_cb)
                data_layout.addWidget(select_all_cb, row, col)
                col += 1
                select_all_cb.stateChanged.connect(self.toggle_all_data)
            else:
                cb = QCheckBox(icon_text)
                cb.setProperty("data_type", data_type)
                cb.setMinimumHeight(25)

                cb.setStyleSheet("""
                    QCheckBox {
                        padding: 6px;
                        font-size: 12px;
                        border-radius: 4px;
                        background-color: none;
                    }
                    QCheckBox:hover {
                        background-color: #f5f7fa;
                    }
                    QCheckBox::indicator {
                        width: 16px;
                        height: 16px;
                    }
                """)

                # if data_type in ["Ledgers", "Stocks"]:
                #     cb.setChecked(True)
                if data_type in ["Sales"]:
                    cb.setChecked(True)

                self.data_checkboxes.append(cb)
                data_layout.addWidget(cb, row, col)

                col += 1
                if col > 1:
                    col = 0
                    row += 1

        scroll.setWidget(scroll_container)
        outer_layout.addWidget(scroll)    
        
        data_group.setLayout(outer_layout)
        top_layout.addWidget(data_group)
        
        # Action Buttons (Right side, in ONE COLUMN) - COMPACT
        action_widget = QWidget()
        action_layout = QVBoxLayout()
        action_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        action_layout.setSpacing(10)  # Reduced spacing
        
        self.export_btn = QPushButton("📤 Export Data")
        self.export_btn.setEnabled(False)
        self.export_btn.setMinimumHeight(38)  # Reduced from 45
        self.export_btn.setMinimumWidth(130)  # Reduced from 140
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 16px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.export_btn.clicked.connect(self.on_export_clicked)
        
        self.sync_btn = QPushButton("🔄 Sync")
        self.sync_btn.setEnabled(False)
        self.sync_btn.setMinimumHeight(38)  # Reduced from 45
        self.sync_btn.setMinimumWidth(130)  # Reduced from 140
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 16px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.sync_btn.clicked.connect(self.on_sync_clicked)
        
        # Add buttons vertically
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.sync_btn)
        
        action_widget.setLayout(action_layout)
        
        # Add action widget
        top_layout.addWidget(action_widget, 0, Qt.AlignRight | Qt.AlignTop)
        
        top_section.setLayout(top_layout)
        main_layout.addWidget(top_section)
        
        # Bottom Section: Enhanced Data View - LARGER HEIGHT
        bottom_section = QWidget()
        bottom_layout = QVBoxLayout()
        
        # Section Title
        section_title = QLabel("📋 Preview")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #333333;
                padding: 8px 0;
            }
        """)
        bottom_layout.addWidget(section_title)
        
        # Enhanced Data View - WILL TAKE MORE SPACE
        self.data_view = EnhancedDataView()
        bottom_layout.addWidget(self.data_view, 1)  # Stretch factor 1 for data view
        
        bottom_section.setLayout(bottom_layout)
        
        # Add sections to main layout with stretch factors
        main_layout.addWidget(bottom_section, 1)  # Stretch factor 1 for remaining space
        
        self.setLayout(main_layout)
    
    def toggle_all_data(self, state):
        """Header checkbox → Select/Deselect all"""

        checked = bool(state)
        for cb in self.data_checkboxes:
            cb.blockSignals(True)
            cb.setChecked(checked)
            cb.blockSignals(False)
    
    def test_connection(self):
        """Test BUSY connection"""
        dsn = self.dsn_combo.currentText()
        username = "admin"  # Default username
        password = "password"  # Default password
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Connecting...")
        
        # Call controller to test connection
        self.controller.connect_busy(dsn, username, password)
    
    def on_status_changed(self, status: ConnectorStatus):
        """Handle status changes"""
        self.status_label.setText(status.value.title())
        
        if status == ConnectorStatus.CONNECTED:
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")
            self.export_btn.setEnabled(True)
            self.sync_btn.setEnabled(True)
        elif status == ConnectorStatus.PENDING:
            self.status_label.setStyleSheet("color: #FF9800; font-weight: bold; font-size: 12px;")
        else:
            self.status_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 12px;")
            self.export_btn.setEnabled(False)
            self.sync_btn.setEnabled(False)
        
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔗 Test Connection")
    
    def on_export_clicked(self):
        asyncio.run(self.export_data())

    async def export_data(self):
        """Export BUSY data"""
        # Collect configuration
        config = BusyConfig(
            dsn=self.dsn_combo.currentText(),
            username="admin",
            company="",
            selected_data_types=self.get_selected_data_types(),
            date_from=self.date_from.date().toPython(),
            date_to=self.date_to.date().toPython()
        )
        
        # Disable buttons during export
        self.export_btn.setEnabled(False)
        self.sync_btn.setEnabled(False)
        self.export_btn.setText("Exporting...")
        
        # Call controller to export
        try:
            success = self.controller.export_busy_data(config)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            QTimer.singleShot(500, self.enable_buttons)
            return
        
        # Re-enable buttons after delay
        QTimer.singleShot(1000, self.enable_buttons)
    
    def on_sync_clicked(self):
        asyncio.run(self.sync_data())

    async def sync_data(self):
        """Sync BUSY data"""
        # Collect configuration
        config = BusyConfig(
            dsn=self.dsn_combo.currentText(),
            username="admin",
            company="",
            selected_data_types=self.get_selected_data_types(),
            date_from=self.date_from.date().toPython(),
            date_to=self.date_to.date().toPython()
        )
        
        # Disable buttons during sync
        self.export_btn.setEnabled(False)
        self.sync_btn.setEnabled(False)
        self.sync_btn.setText("Syncing...")
        
        # Call controller to sync
        try:
            success = self.controller.sync_busy_data(config)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            QTimer.singleShot(500, self.enable_buttons)
            return
        
        # Re-enable buttons after delay
        QTimer.singleShot(1000, self.enable_buttons)
    
    def get_selected_data_types(self):
        """Get selected data types from checkboxes"""
        selected = []
        for checkbox in self.findChildren(QCheckBox):
            if checkbox.isChecked():
                selected.append(checkbox.property("data_type"))
        return selected
    
    def enable_buttons(self):
        """Re-enable action buttons"""
        if self.controller.busy_status == ConnectorStatus.CONNECTED:
            self.export_btn.setEnabled(True)
            self.sync_btn.setEnabled(True)
        
        self.export_btn.setText("📤 Export Data")
        self.sync_btn.setText("🔄 Sync")

class LogsTab(QWidget):
    """Logs viewer tab"""
    
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.init_ui()
        
        # Connect signals
        self.controller.log_updated.connect(self.add_log_entry)
        
        # Load existing logs
        self.load_existing_logs()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📜 Application Logs")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2196F3; padding: 10px 0;")
        layout.addWidget(header)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # toolbar_layout.addWidget(QLabel("Log Level Filter:"))
        
        # self.log_level_combo = QComboBox()
        # self.log_level_combo.addItems(["All", "📘 INFO", "⚠️ WARNING", "❌ ERROR", "✅ SUCCESS"])
        # self.log_level_combo.currentTextChanged.connect(self.filter_logs)
        # toolbar_layout.addWidget(self.log_level_combo)
        
        toolbar_layout.addStretch()
        
        self.clear_btn = QPushButton("🗑️ Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        toolbar_layout.addWidget(self.clear_btn)
        
        # self.save_btn = QPushButton("💾 Save Logs")
        # self.save_btn.clicked.connect(self.save_logs)
        # toolbar_layout.addWidget(self.save_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Log viewer with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(QFont("Consolas", 10))
        
        # Set up syntax highlighting colors
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 2px solid #3c3c3c;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        scroll_area.setWidget(self.log_viewer)
        layout.addWidget(scroll_area, 1)  # Stretch factor 1
        
        self.setLayout(layout)
    
    def load_existing_logs(self):
        """Load existing logs from controller"""
        logs = self.controller.get_logs()
        for log in logs:
            self.add_log_entry(log)
    
    def add_log_entry(self, log: LogEntry):
        """Add a log entry to the viewer"""
        # Determine color based on log level
        colors = {
            LogLevel.INFO: "#569cd6",      # Blue
            LogLevel.WARNING: "#dcdcaa",    # Yellow
            LogLevel.ERROR: "#f44747",      # Red
            LogLevel.SUCCESS: "#4ec9b0"     # Green
        }
        
        # Add icons to log level
        level_icons = {
            LogLevel.INFO: "📘",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.SUCCESS: "✅"
        }
        
        color = colors.get(log.level, "#d4d4d4")
        icon = level_icons.get(log.level, "📝")
        log_text = f"[{log.timestamp.strftime('%H:%M:%S')}] [{icon} {log.level.value}] [{log.source}] {log.message}"
        
        # Apply colored text
        self.log_viewer.moveCursor(QTextCursor.End)
        
        # Set text color and insert text
        self.log_viewer.setTextColor(QColor(color))
        self.log_viewer.insertPlainText(log_text + "\n")
        
        # Auto-scroll to bottom
        self.log_viewer.ensureCursorVisible()
    
    def filter_logs(self):
        """Filter logs by level"""
        # TODO: Implement log filtering
        pass
    
    def clear_logs(self):
        """Clear all logs"""
        self.controller.clear_logs()
        self.log_viewer.clear()
    
    def save_logs(self):
        """Save logs to file"""
        # TODO: Implement log saving to file
        QMessageBox.information(
            self,
            "Save Logs",
            "Log saving functionality would be implemented here.\n"
            "In production, this would save logs to a file with timestamp."
        )

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Accounting Connector")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget with tabs
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create tabs
        # self.dashboard_tab = DashboardTab(self.controller)
        self.tally_tab = TallyConnectorTab(self.controller)
        # self.busy_tab = BusyConnectorTab(self.controller)
        self.logs_tab = LogsTab(self.controller)
        
        # Add tabs to tab widget with icons
        # self.central_widget.addTab(self.dashboard_tab, "🏠 Dashboard")
        self.central_widget.addTab(self.tally_tab, "🧮 Tally Connector")
        # self.central_widget.addTab(self.busy_tab, "💼 BUSY Connector")
        self.central_widget.addTab(self.logs_tab, "📜 Logs")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add status indicators to status bar
        self.status_bar.addPermanentWidget(QLabel("Tally:"))
        self.tally_status_widget = StatusIndicator()
        self.status_bar.addPermanentWidget(self.tally_status_widget)
        
        # self.status_bar.addPermanentWidget(QLabel("BUSY:"))
        # self.busy_status_widget = StatusIndicator()
        # self.status_bar.addPermanentWidget(self.busy_status_widget)
        
        # Initial status update
        self.update_status_bar()
        
        # Show welcome message
        self.status_bar.showMessage("Ready - Enhanced Accounting Connector with Data Tables", 3000)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect status change signals
        self.controller.tally_status_changed.connect(
            lambda status: self.tally_status_widget.set_status(status)
        )
        # self.controller.busy_status_changed.connect(
        #     lambda status: self.busy_status_widget.set_status(status)
        # )
        
        # Connect log updates to status bar
        self.controller.log_updated.connect(self.on_log_updated)
    
    def update_status_bar(self):
        """Update status bar indicators"""
        self.tally_status_widget.set_status(self.controller.tally_status)
        # self.busy_status_widget.set_status(self.controller.busy_status)
    
    def on_log_updated(self, log: LogEntry):
        """Handle log updates"""
        # Show error logs in status bar
        if log.level == LogLevel.ERROR:
            self.status_bar.showMessage(log.message, 5000)
