"""
Alert Item Widget
Displays a single alert in the list
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AlertItemWidget(QWidget):
    """
    Widget for displaying a single alert
    Shows datetime, message, priority, status, and action buttons
    """

    # Signals
    edit_requested = pyqtSignal(dict)  # Emitted when edit button clicked
    dismiss_requested = pyqtSignal(dict)  # Emitted when dismiss button clicked
    delete_requested = pyqtSignal(dict)  # Emitted when delete requested

    def __init__(self, alert, parent=None):
        """
        Initialize alert item widget

        Args:
            alert: Dictionary with alert data
            parent: Parent widget
        """
        super().__init__(parent)
        self.alert = alert

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # DateTime label
        datetime_str = self.alert['alert_datetime']
        try:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            formatted_datetime = dt.strftime("%d/%m %H:%M")
        except:
            formatted_datetime = datetime_str[:16] if len(datetime_str) >= 16 else datetime_str

        self.datetime_label = QLabel(formatted_datetime)
        self.datetime_label.setFixedWidth(80)
        datetime_font = QFont()
        datetime_font.setPointSize(10)
        datetime_font.setBold(True)
        self.datetime_label.setFont(datetime_font)
        layout.addWidget(self.datetime_label)

        # Content section (title + message)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        # Title
        title = self.alert.get('alert_title', 'Alerta sin título')
        self.title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        self.title_label.setFont(title_font)
        content_layout.addWidget(self.title_label)

        # Message (if exists)
        message = self.alert.get('alert_message', '').strip()
        if message:
            self.message_label = QLabel(message)
            msg_font = QFont()
            msg_font.setPointSize(9)
            self.message_label.setFont(msg_font)
            self.message_label.setStyleSheet("color: #999999;")
            # Truncate long messages
            if len(message) > 80:
                self.message_label.setText(message[:77] + "...")
            content_layout.addWidget(self.message_label)

        layout.addLayout(content_layout, 1)  # Stretch to fill space

        # Priority badge
        priority = self.alert.get('priority', 'medium')
        priority_text = {
            'low': '🟢 Baja',
            'medium': '🟡 Media',
            'high': '🔴 Alta'
        }.get(priority, '🟡 Media')

        self.priority_label = QLabel(priority_text)
        self.priority_label.setFixedWidth(90)
        priority_font = QFont()
        priority_font.setPointSize(9)
        self.priority_label.setFont(priority_font)
        layout.addWidget(self.priority_label)

        # Status badge
        status = self.alert.get('status', 'active')
        is_enabled = self.alert.get('is_enabled', 1)

        if status == 'triggered':
            self.status_label = QLabel('🔔 Disparada')
            self.status_label.setStyleSheet("color: #ff9800;")
        elif status == 'dismissed':
            self.status_label = QLabel('✓ Descartada')
            self.status_label.setStyleSheet("color: #4caf50;")
        elif not is_enabled:
            self.status_label = QLabel('⏸ Deshabilitada')
            self.status_label.setStyleSheet("color: #757575;")
        else:
            self.status_label = QLabel('⏱ Activa')
            self.status_label.setStyleSheet("color: #2196f3;")

        self.status_label.setFixedWidth(110)
        status_font = QFont()
        status_font.setPointSize(9)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)

        # Dismiss button (only for active alerts)
        if status == 'active' and is_enabled:
            self.btn_dismiss = QPushButton("✓")
            self.btn_dismiss.setFixedSize(30, 30)
            self.btn_dismiss.setToolTip("Descartar alerta")
            self.btn_dismiss.clicked.connect(self.on_dismiss_clicked)
            buttons_layout.addWidget(self.btn_dismiss)

        # Edit button
        self.btn_edit = QPushButton("✏")
        self.btn_edit.setFixedSize(30, 30)
        self.btn_edit.setToolTip("Editar alerta")
        self.btn_edit.clicked.connect(self.on_edit_clicked)
        buttons_layout.addWidget(self.btn_edit)

        # Delete button
        self.btn_delete = QPushButton("🗑")
        self.btn_delete.setFixedSize(30, 30)
        self.btn_delete.setToolTip("Eliminar alerta")
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        buttons_layout.addWidget(self.btn_delete)

        layout.addLayout(buttons_layout)

    def apply_styles(self):
        """Apply styles to the widget"""
        # Different background based on status
        status = self.alert.get('status', 'active')
        if status == 'triggered':
            bg_color = "#3d2d1d"  # Darker orange tint
        elif status == 'dismissed':
            bg_color = "#1d2d1d"  # Darker green tint
        else:
            bg_color = "#2d2d2d"  # Normal

        self.setStyleSheet(f"""
            AlertItemWidget {{
                background-color: {bg_color};
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }}
            AlertItemWidget:hover {{
                background-color: #333333;
                border-color: #007acc;
            }}
            QPushButton {{
                background-color: #3d3d3d;
                color: #cccccc;
                border: 1px solid #4d4d4d;
                border-radius: 3px;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #4d4d4d;
                border-color: #007acc;
            }}
            QLabel {{
                color: #cccccc;
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
        """)

    def on_dismiss_clicked(self):
        """Handle dismiss button click"""
        logger.debug(f"Dismiss alert requested: {self.alert['id']}")
        self.dismiss_requested.emit(self.alert)

    def on_edit_clicked(self):
        """Handle edit button click"""
        logger.debug(f"Edit alert requested: {self.alert['id']}")
        self.edit_requested.emit(self.alert)

    def on_delete_clicked(self):
        """Handle delete button click"""
        logger.debug(f"Delete alert requested: {self.alert['id']}")
        self.delete_requested.emit(self.alert)

    def mouseDoubleClickEvent(self, event):
        """Handle double click to edit"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_edit_clicked()
