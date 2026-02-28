#!/usr/bin/env python3
"""
Accounting Connector - Main Application Entry Point
Enhanced version with left panel data tabs
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.controllers import MainController
from src.views import MainWindow

def main():
    """Application main entry point"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Accounting Connector")
    app.setOrganizationName("Accounting Solutions")
    
    # Set application style
    apply_styles(app)
    
    # Create and show main window
    controller = MainController()
    window = MainWindow(controller)
    window.show()
    
    sys.exit(app.exec())

def apply_styles(app):
    """Apply custom styles to the application"""
    # Use modern styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f7fa;
        }
        QTabWidget::pane {
            border: 1px solid #d1d9e6;
            background-color: white;
            border-radius: 6px;
            margin-top: 2px;
        }
        QTabBar::tab {
            background-color: #f0f2f5;
            border: 1px solid #d1d9e6;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 16px;
            margin-right: 2px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #2196F3;
            color: #2196F3;
        }
        QTabBar::tab:hover:!selected {
            background-color: #e8eaed;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #d1d9e6;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 12px;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: #5f6368;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #9e9e9e;
        }
        QLineEdit, QComboBox, QDateEdit {
            padding: 6px 10px;
            border: 1px solid #d1d9e6;
            border-radius: 4px;
            background-color: white;
            min-height: 32px;
        }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
            border-color: #2196F3;
            outline: none;
        }
        QStatusBar {
            background-color: #f8f9fa;
            color: #5f6368;
            border-top: 1px solid #d1d9e6;
        }
        QScrollArea {
            border: none;
            background-color: white;
        }
        QScrollBar:vertical {
            border: none;
            background: #f1f3f4;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #dadce0;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #bdc1c6;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QSplitter::handle {
            background-color: #d1d9e6;
        }
        QSplitter::handle:hover {
            background-color: #bdc1c6;
        }
    """)

if __name__ == "__main__":
    main()