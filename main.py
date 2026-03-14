"""Main application entry point."""

import sys
from PyQt6.QtWidgets import QApplication

from ai_xiaosuo.models import init_db
from ai_xiaosuo.ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Initialize database
    init_db()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("AI番茄写作助手")
    app.setOrganizationName("AI Xiaosuo")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
