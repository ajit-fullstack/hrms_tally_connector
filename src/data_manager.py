"""
Data Manager with S.No column and increased table height
"""

from typing import List, Dict, Any
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QScrollArea, QFrame, QSplitter, QListWidget, QListWidgetItem,
    QTabWidget, QSizePolicy, QGridLayout, QGroupBox, QButtonGroup,
    QRadioButton
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QFont, QColor, QBrush

from src.mock_data import MockData

class DataTableWidget(QTableWidget):
    """Enhanced table widget with S.No column and increased height"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
    
    def setup_table(self):
        """Configure table appearance and behavior"""
        # Enable scrolling
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Enable selection
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Enable sorting
        self.setSortingEnabled(True)
        
        # Alternating row colors
        self.setAlternatingRowColors(True)
        
        # Auto resize
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Set proper header height
        self.horizontalHeader().setMinimumHeight(25)  # Increased header height
        self.verticalHeader().setDefaultSectionSize(40)  # Increased row height
        self.verticalHeader().setVisible(True)  # Show row numbers (will be S.No)
        
        # Set vertical header properties for S.No column
        self.verticalHeader().setMinimumWidth(60)  # Wider for "S.No"
        self.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        
        # Ensure scrollbars are always visible when needed
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Style - FIXED HEADER STYLING with S.No column
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                border: 2px solid #dee2e6;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px 10px;
                border-right: 1px solid #dee2e6;
                border-bottom: 1px solid #dee2e6;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QHeaderView::section {
                background-color: #f1f3f4;
                padding: 14px 12px;
                border: 1px solid #dee2e6;
                border-left: none;
                border-top: none;
                font-weight: bold;
                color: #333333;
                font-size: 14px;
                min-height: 25px;
            }
            QHeaderView::section:first {
                border-left: 1px solid #dee2e6;
            }
            QHeaderView::section:last {
                border-right: 1px solid #dee2e6;
            }
            QHeaderView::section:checked {
                background-color: #e0e0e0;
            }
            QHeaderView {
                background-color: #f1f3f4;
                border: none;
            }
            /* Vertical header (S.No column) styling */
            QHeaderView::section:vertical {
                background-color: #e9ecef;
                padding: 12px 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                color: #495057;
                font-size: 13px;
                min-width: 60px;
            }
            QHeaderView::section:vertical:first {
                border-top: 1px solid #dee2e6;
            }
            QHeaderView::section:vertical:last {
                border-bottom: 1px solid #dee2e6;
            }
        """)
        
        # Set selection behavior
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    def load_data(self, columns: List[str], data: List[List[Any]]):
        """Load data into table with S.No column"""
        self.clear()
        
        # Add S.No as first column
        all_columns = ["S.No"] + columns
        self.setColumnCount(len(all_columns))
        self.setHorizontalHeaderLabels(all_columns)
        self.setRowCount(len(data))
        
        # Set column widths based on content
        font_metrics = self.fontMetrics()
        
        # Set S.No column width
        self.setColumnWidth(0, 80)  # Fixed width for S.No column
        
        # Calculate initial column widths for other columns
        for col_idx, column_name in enumerate(columns, start=1):  # Start from 1 because 0 is S.No
            # Start with column name width
            max_width = font_metrics.horizontalAdvance(column_name) + 60
            
            # Set column width with min/max constraints
            self.setColumnWidth(col_idx, min(max(140, max_width), 400))
        

        # Set data with proper alignment and S.No
        for row_idx, row_data in enumerate(data):
            # Add S.No in first column (center aligned)
            sno_item = QTableWidgetItem(str(row_idx + 1))
            sno_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            sno_item.setFont(QFont(self.font().family(), self.font().pointSize(), QFont.Bold))
            sno_item.setForeground(QBrush(QColor("#495057")))  # Dark gray for S.No
            self.setItem(row_idx, 0, sno_item)
            
            # Add data columns
            for col_idx, cell_data in enumerate(list(row_data.values())):
                item = QTableWidgetItem(str(cell_data))
                data_col_idx = col_idx + 1  # +1 because column 0 is S.No
                
                # Format numeric columns (balance columns)
                # Adjust indices since we added S.No column
                if data_col_idx in [5, 6]:  # Opening Balance (now col 5) and Closing Balance (now col 6)
                    try:
                        # Remove commas and convert to float
                        clean_value = str(cell_data).replace(',', '')
                        float_value = float(clean_value)
                        formatted_value = f"{float_value:,.2f}"
                        item.setText(formatted_value)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    except:
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                self.setItem(row_idx, data_col_idx, item)
        
        # Set row heights (increased)
        for row in range(self.rowCount()):
            self.setRowHeight(row, 40)
        
        # Auto resize last column to fill space
        self.horizontalHeader().setStretchLastSection(True)
        
        # Ensure headers are visible
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)  # Hide default vertical header since we have S.No column
        
        # Set vertical header label for S.No
        self.verticalHeader().setFixedWidth(0)  # Hide it completely
        
        # Refresh the table
        self.viewport().update()
        
        # Force update to ensure display
        self.updateGeometry()

    def load_data_v1(self, columns: List[str], data: List[List[Any]]):
        """Load data into table with S.No column"""
        self.clear()
        
        # Add S.No as first column
        all_columns = ["S.No"] + columns
        self.setColumnCount(len(all_columns))
        self.setHorizontalHeaderLabels(all_columns)
        self.setRowCount(len(data))
        
        # Set column widths based on content
        font_metrics = self.fontMetrics()
        
        # Set S.No column width
        self.setColumnWidth(0, 80)  # Fixed width for S.No column
        
        # Calculate initial column widths for other columns
        for col_idx, column_name in enumerate(columns, start=1):  # Start from 1 because 0 is S.No
            # Start with column name width
            max_width = font_metrics.horizontalAdvance(column_name) + 60
            
            # Check data in this column
            # for row_idx in range(min(20, len(data))):  # Check first 20 rows
            #     cell_data = str(data[row_idx][col_idx-1]) if (col_idx-1) < len(data[row_idx]) else ""
            #     cell_width = font_metrics.horizontalAdvance(cell_data) + 40
            #     max_width = max(max_width, cell_width)
            
            # Set column width with min/max constraints
            self.setColumnWidth(col_idx, min(max(140, max_width), 400))
        

        # Set data with proper alignment and S.No
        for row_idx, row_data in enumerate(data):
            # Add S.No in first column (center aligned)
            sno_item = QTableWidgetItem(str(row_idx + 1))
            sno_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            sno_item.setFont(QFont(self.font().family(), self.font().pointSize(), QFont.Bold))
            sno_item.setForeground(QBrush(QColor("#495057")))  # Dark gray for S.No
            self.setItem(row_idx, 0, sno_item)
            
            
            # Add data columns
            for col_idx, cell_data in enumerate(list(row_data.values())):
                item = QTableWidgetItem(str(cell_data))
                data_col_idx = col_idx + 1  # +1 because column 0 is S.No
                
                # Format numeric columns (balance columns)
                # Adjust indices since we added S.No column
                if data_col_idx in [5, 6]:  # Opening Balance (now col 5) and Closing Balance (now col 6)
                    try:
                        # Remove commas and convert to float
                        clean_value = str(cell_data).replace(',', '')
                        float_value = float(clean_value)
                        formatted_value = f"{float_value:,.2f}"
                        item.setText(formatted_value)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    except:
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Color code status column
                # if data_col_idx == len(row_data):  # Last column (status)
                #     status_text = str(cell_data)
                #     if "Active" in status_text:
                #         item.setForeground(QBrush(QColor("#28a745")))  # Green
                #         item.setFont(QFont(self.font().family(), self.font().pointSize(), QFont.Bold))
                #     elif "Inactive" in status_text:
                #         item.setForeground(QBrush(QColor("#dc3545")))  # Red
                #         item.setFont(QFont(self.font().family(), self.font().pointSize(), QFont.Bold))
                #     elif "Pending" in status_text:
                #         item.setForeground(QBrush(QColor("#ffc107")))  # Yellow
                #         item.setFont(QFont(self.font().family(), self.font().pointSize(), QFont.Bold))
                
                # Make numeric columns stand out
                # if data_col_idx in [5, 6]:  # Balance columns
                #     item.setFont(QFont(self.font().family(), self.font().pointSize(), QFont.Bold))
                
                self.setItem(row_idx, data_col_idx, item)
        
        # Set row heights (increased)
        for row in range(self.rowCount()):
            self.setRowHeight(row, 40)
        
        # Auto resize last column to fill space
        self.horizontalHeader().setStretchLastSection(True)
        
        # Ensure headers are visible
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(False)  # Hide default vertical header since we have S.No column
        
        # Set vertical header label for S.No
        self.verticalHeader().setFixedWidth(0)  # Hide it completely
        
        # Refresh the table
        self.viewport().update()
        
        # Force update to ensure display
        self.updateGeometry()

class AccountingDataPanel(QWidget):
    """Left panel with single column accounting data tabs as buttons with icons"""
    
    tab_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        mock_obj =  MockData()
        self.tabs_data = mock_obj.get_accounting_tabs()
        self.current_tab = "Ledgers"
        self.init_ui()

    def reload_tabs_data(self, data):
        """Reload data from source (called after export)"""
        mock_obj = MockData()
        self.tabs_data = mock_obj.get_accounting_tabs(data)
    
    def init_ui(self):
        """Initialize the data panel UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("📊 Accounting Data")
        header_font = QFont()
        header_font.setPointSize(13)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background-color: #343a40;
                color: white;
                padding: 14px;
                border-bottom: 2px solid #495057;
                border-radius: 0px;
                qproperty-alignment: AlignCenter;
            }
        """)
        header.setMinimumHeight(50)
        layout.addWidget(header)
        
        # Create button group for single selection
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        
        # Create container for buttons with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                border-radius: 6px;
                min-height: 25px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Create widget for buttons container
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setContentsMargins(8, 12, 8, 12)
        buttons_layout.setSpacing(6)
        
        # Add tabs as radio buttons with icons
        tab_icons = {
            "Ledgers": "📊",
            "Stocks": "📦",
            "Sales": "💰",
            "Purchase": "🛒",
            "Credit Note": "📝",
            "Debit Note": "📋",
            "Receipt": "💵",
            "Payment": "💳",
            "Journal": "📒",
            "Contra": "🔄"
        }

        # self.reload_tabs_data()
        for tab_data in self.tabs_data:
            tab_name = tab_data['name']
            icon = tab_icons.get(tab_name, "📋")
            
            radio_btn = QRadioButton(f"{icon} {tab_name}")
            radio_btn.setMinimumHeight(42)
            radio_btn.setStyleSheet("""
                QRadioButton {
                    padding: 12px 16px;
                    font-size: 13px;
                    font-weight: 500;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    background-color: white;
                    margin: 2px;
                }
                QRadioButton:hover {
                    background-color: #f8f9fa;
                    border-color: #adb5bd;
                }
                QRadioButton:checked {
                    background-color: #007bff;
                    color: white;
                    border-color: #0056b3;
                }
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)
            radio_btn.setToolTip(tab_data['description'])
            radio_btn.setProperty("tab_name", tab_name)
            
            radio_btn.toggled.connect(lambda checked, btn=radio_btn: self.on_tab_selected(checked, btn))
            
            self.button_group.addButton(radio_btn)
            buttons_layout.addWidget(radio_btn)
        
        # Select first button
        if buttons_layout.count() > 0:
            first_btn = buttons_layout.itemAt(0).widget()
            first_btn.setChecked(True)
        
        buttons_layout.addStretch()
        buttons_container.setLayout(buttons_layout)
        scroll_area.setWidget(buttons_container)
        
        layout.addWidget(scroll_area, 1)
        
        self.setLayout(layout)
        self.setMinimumWidth(240)
        self.setMaximumWidth(280)
    
    def on_tab_selected(self, checked: bool, button):
        """Handle tab selection"""
        if checked:
            tab_name = button.property("tab_name")
            self.current_tab = tab_name
            self.tab_changed.emit(tab_name)
    
    def get_current_tab_data(self) -> Dict[str, Any]:
        """Get data for current tab"""
        for tab_data in self.tabs_data:
            if tab_data['name'] == self.current_tab:
                return tab_data
        return self.tabs_data[0]

class DataDisplayPanel(QWidget):
    """Right panel for displaying data tables - Reduced height to prevent cutting"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_table = None
        self.table_container = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the display panel UI with reduced height to prevent cutting"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create a container widget for the table
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        self.table_layout.setSpacing(0)
        
        # Create initial table with reduced height to prevent cutting
        self.current_table = DataTableWidget()
        self.current_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_table.setMinimumHeight(450)  # Reduced from 500 to prevent cutting
        
        self.table_layout.addWidget(self.current_table)
        
        # Add table container to main layout with maximum stretch
        layout.addWidget(self.table_container, 1)
        
        self.setLayout(layout)
        self.setMinimumHeight(480)  # Reduced from 550 to prevent cutting
    
    # def load_tab_data(self, tab_data: Dict[str, Any]):
    #     """Load data for the selected tab"""
    #     # Remove old table from layout
    #     if self.current_table:
    #         self.table_layout.removeWidget(self.current_table)
    #         self.current_table.deleteLater()
    #         self.current_table = None
        
    #     # Create new table with reduced height
    #     self.current_table = DataTableWidget()
    #     self.current_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    #     self.current_table.setMinimumHeight(450)  # Reduced from 500 to prevent cutting
        
    #     # Load data - Add S.No to columns
    #     columns = tab_data['columns']
    #     data = tab_data['data']
    #     self.current_table.load_data(columns, data)
        
    #     # Add new table to layout
    #     self.table_layout.addWidget(self.current_table)
        
    #     # Force update of layout
    #     self.table_container.updateGeometry()
    #     self.updateGeometry()
        
    #     # Set focus to table
    #     self.current_table.setFocus()

    def load_tab_data(self, tab_data: Dict[str, Any]):
        columns = tab_data['columns']
        data = tab_data['data']

        # Reuse existing table if possible
        if not self.current_table:
            self.current_table = DataTableWidget()
            self.current_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.current_table.setMinimumHeight(450)
            self.table_layout.addWidget(self.current_table)

        # Load new data
        self.current_table.load_data(columns, data)

        # Force refresh
        self.current_table.viewport().update()
        self.current_table.updateGeometry()

class EnhancedDataView(QWidget):
    """Main enhanced data view with left panel and data display"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_connections()

    def refresh_data(self, data):
        """
        Called after Export button click
        Reloads data for currently selected tab
        """
        # Reload data source
        self.data_panel.reload_tabs_data(data)

        # Get currently selected tab data
        tab_data = self.data_panel.get_current_tab_data()

        # Reload table
        self.display_panel.load_tab_data(tab_data)
    
    def init_ui(self):
        """Initialize the enhanced data view"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        
        # Left panel (data tabs as single column buttons with scroll)
        self.data_panel = AccountingDataPanel()
        self.data_panel.setMinimumWidth(240)
        self.data_panel.setMaximumWidth(280)
        self.data_panel.setMinimumHeight(450)
        
        # Right panel (data display) - Reduced height to prevent cutting
        self.display_panel = DataDisplayPanel()
        self.display_panel.setMinimumHeight(450)  # Reduced from 550
        
        # Add to main layout with stretch factor
        main_layout.addWidget(self.data_panel)
        main_layout.addWidget(self.display_panel, 1)
        
        self.setLayout(main_layout)
        self.setMinimumHeight(450)  # Reduced from 600 to prevent cutting
        
        # Load initial data
        self.load_current_tab_data()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.data_panel.tab_changed.connect(self.on_tab_changed)
    
    def on_tab_changed(self, tab_name: str):
        """Handle tab change event"""
        tab_data = self.data_panel.get_current_tab_data()
        self.display_panel.load_tab_data(tab_data)
    
    def load_current_tab_data(self):
        """Load data for current tab"""
        tab_data = self.data_panel.get_current_tab_data()
        self.display_panel.load_tab_data(tab_data)
        