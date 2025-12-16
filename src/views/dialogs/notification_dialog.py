"""
Notification Dialog
Popup notification for triggered alerts
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QScreen
import logging

logger = logging.getLogger(__name__)


class NotificationDialog(QDialog):
    """
    Popup notification dialog for alerts
    Appears in bottom-right corner with alert information
    """

    def __init__(self, alert, item, parent=None):
        """
        Initialize notification dialog

        Args:
            alert: Alert dictionary
            item: Item dictionary associated with alert
            parent: Parent widget
        """
        super().__init__(parent)
        self.alert = alert
        self.item = item

        self.setup_window()
        self.setup_ui()
        self.apply_styles()
        self.position_dialog()

        logger.info(f"NotificationDialog shown for alert: {alert.get('id')}")

    def setup_window(self):
        """Configure window properties"""
        self.setWindowTitle("Alerta")
        self.setMinimumSize(380, 180)
        self.setMaximumSize(380, 300)

        # Frameless window, always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Make it not steal focus
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header with close button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Alert icon and title
        icon_label = QLabel("🔔")
        icon_font = QFont()
        icon_font.setPointSize(20)
        icon_label.setFont(icon_font)
        header_layout.addWidget(icon_label)

        header_text = QLabel("Alerta Programada")
        header_font = QFont()
        header_font.setPointSize(11)
        header_font.setBold(True)
        header_text.setFont(header_font)
        header_layout.addWidget(header_text, 1)

        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(25, 25)
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)

        layout.addLayout(header_layout)

        # Separator line
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #3d3d3d;")
        layout.addWidget(separator)

        # Alert title
        alert_title = self.alert.get('alert_title', 'Sin título')
        title_label = QLabel(alert_title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Alert message
        alert_message = self.alert.get('alert_message', '')
        if alert_message:
            message_label = QLabel(alert_message)
            message_font = QFont()
            message_font.setPointSize(10)
            message_label.setFont(message_font)
            message_label.setWordWrap(True)
            message_label.setStyleSheet("color: #cccccc;")
            layout.addWidget(message_label)

        # Item info
        item_info = QLabel(f"📌 Item: {self.item.get('label', 'Desconocido')}")
        item_font = QFont()
        item_font.setPointSize(9)
        item_info.setFont(item_font)
        item_info.setStyleSheet("color: #999999;")
        layout.addWidget(item_info)

        # Priority badge
        priority = self.alert.get('priority', 'medium')
        priority_text = {
            'low': '🟢 Prioridad Baja',
            'medium': '🟡 Prioridad Media',
            'high': '🔴 Prioridad Alta'
        }.get(priority, '🟡 Prioridad Media')

        priority_label = QLabel(priority_text)
        priority_font = QFont()
        priority_font.setPointSize(9)
        priority_label.setFont(priority_font)

        if priority == 'high':
            priority_label.setStyleSheet("color: #ff5252;")
        elif priority == 'low':
            priority_label.setStyleSheet("color: #4caf50;")
        else:
            priority_label.setStyleSheet("color: #ffc107;")

        layout.addWidget(priority_label)

        layout.addStretch()

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.view_item_btn = QPushButton("👁 Ver Item")
        self.view_item_btn.setMinimumHeight(35)
        self.view_item_btn.clicked.connect(self.view_item)

        self.dismiss_btn = QPushButton("✓ Cerrar")
        self.dismiss_btn.setMinimumHeight(35)
        self.dismiss_btn.clicked.connect(self.accept)

        buttons_layout.addWidget(self.view_item_btn)
        buttons_layout.addWidget(self.dismiss_btn)

        layout.addLayout(buttons_layout)

        # Auto-close timer (optional - after 30 seconds)
        # Commented out for now, can be enabled if desired
        # self.auto_close_timer = QTimer()
        # self.auto_close_timer.timeout.connect(self.reject)
        # self.auto_close_timer.start(30000)  # 30 seconds

    def apply_styles(self):
        """Apply dark theme styles"""
        priority = self.alert.get('priority', 'medium')

        # Different border color based on priority
        if priority == 'high':
            border_color = "#ff5252"
        elif priority == 'low':
            border_color = "#4caf50"
        else:
            border_color = "#ffc107"

        self.setStyleSheet(f"""
            QDialog {{
                background-color: #2b2b2b;
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: #ffffff;
                background-color: transparent;
            }}
            QPushButton {{
                background-color: #3d3d3d;
                color: #cccccc;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #4d4d4d;
                border-color: #007acc;
            }}
            QPushButton:pressed {{
                background-color: #2d2d2d;
            }}
            #closeButton {{
                background-color: transparent;
                border: none;
                color: #cccccc;
                font-size: 18pt;
                font-weight: bold;
                border-radius: 12px;
            }}
            #closeButton:hover {{
                background-color: #e81123;
                color: #ffffff;
            }}
        """)

    def position_dialog(self):
        """Position dialog in bottom-right corner of screen"""
        try:
            # Get primary screen
            screen = self.screen()
            if screen is None:
                from PyQt6.QtWidgets import QApplication
                screen = QApplication.primaryScreen()

            screen_geometry = screen.availableGeometry()

            # Calculate position (bottom-right corner with margins)
            x = screen_geometry.width() - self.width() - 20
            y = screen_geometry.height() - self.height() - 20

            self.move(x, y)
            logger.debug(f"Notification positioned at ({x}, {y})")

        except Exception as e:
            logger.error(f"Error positioning notification: {e}", exc_info=True)

    def view_item(self):
        """Handle view item button click"""
        logger.info(f"View item requested: {self.item.get('id')}")
        # TODO: Implement item viewing (could open FloatingPanel or copy to clipboard)
        # For now, just accept the dialog
        self.accept()

    def showEvent(self, event):
        """Handle show event to ensure proper positioning"""
        super().showEvent(event)
        # Reposition after show to ensure correct placement
        QTimer.singleShot(10, self.position_dialog)
