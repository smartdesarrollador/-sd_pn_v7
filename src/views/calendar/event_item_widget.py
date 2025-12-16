"""
Event Item Widget
Displays a single calendar event in the list
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EventItemWidget(QWidget):
    """
    Widget for displaying a single calendar event
    Shows time, title, priority, and edit button
    """

    # Signals
    edit_requested = pyqtSignal(dict)  # Emitted when edit button clicked
    delete_requested = pyqtSignal(dict)  # Emitted when delete requested

    def __init__(self, event, parent=None):
        """
        Initialize event item widget

        Args:
            event: Dictionary with event data
            parent: Parent widget
        """
        super().__init__(parent)
        self.event = event

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Time label
        time_str = self.event['event_datetime'][11:16] if len(self.event['event_datetime']) >= 16 else "00:00"
        self.time_label = QLabel(time_str)
        self.time_label.setFixedWidth(50)
        time_font = QFont()
        time_font.setPointSize(10)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        layout.addWidget(self.time_label)

        # Content section (title + description)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)

        # Title
        title = self.event.get('title', 'Sin título')
        self.title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(10)
        self.title_label.setFont(title_font)
        content_layout.addWidget(self.title_label)

        # Description (if exists)
        description = self.event.get('description', '').strip()
        if description:
            self.desc_label = QLabel(description)
            desc_font = QFont()
            desc_font.setPointSize(9)
            self.desc_label.setFont(desc_font)
            self.desc_label.setStyleSheet("color: #999999;")
            # Truncate long descriptions
            if len(description) > 80:
                self.desc_label.setText(description[:77] + "...")
            content_layout.addWidget(self.desc_label)

        layout.addLayout(content_layout, 1)  # Stretch to fill space

        # Priority badge
        priority = self.event.get('priority', 'medium')
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
        status = self.event.get('status', 'pending')
        if status == 'completed':
            self.status_label = QLabel('✓ Completado')
            self.status_label.setStyleSheet("color: #4caf50;")
        elif status == 'cancelled':
            self.status_label = QLabel('✗ Cancelado')
            self.status_label.setStyleSheet("color: #f44336;")
        else:
            self.status_label = QLabel('⏱ Pendiente')
            self.status_label.setStyleSheet("color: #2196f3;")

        self.status_label.setFixedWidth(100)
        status_font = QFont()
        status_font.setPointSize(9)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)

        # Edit button
        self.btn_edit = QPushButton("✏")
        self.btn_edit.setFixedSize(30, 30)
        self.btn_edit.setToolTip("Editar evento")
        self.btn_edit.clicked.connect(self.on_edit_clicked)
        layout.addWidget(self.btn_edit)

        # Delete button
        self.btn_delete = QPushButton("🗑")
        self.btn_delete.setFixedSize(30, 30)
        self.btn_delete.setToolTip("Eliminar evento")
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        layout.addWidget(self.btn_delete)

    def apply_styles(self):
        """Apply styles to the widget"""
        self.setStyleSheet("""
            EventItemWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            EventItemWidget:hover {
                background-color: #333333;
                border-color: #007acc;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #cccccc;
                border: 1px solid #4d4d4d;
                border-radius: 3px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #007acc;
            }
            QLabel {
                color: #cccccc;
                background-color: transparent;
                border: none;
                padding: 0px;
            }
        """)

    def on_edit_clicked(self):
        """Handle edit button click"""
        logger.debug(f"Edit event requested: {self.event['id']}")
        self.edit_requested.emit(self.event)

    def on_delete_clicked(self):
        """Handle delete button click"""
        logger.debug(f"Delete event requested: {self.event['id']}")
        self.delete_requested.emit(self.event)

    def mouseDoubleClickEvent(self, event):
        """Handle double click to edit"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_edit_clicked()
