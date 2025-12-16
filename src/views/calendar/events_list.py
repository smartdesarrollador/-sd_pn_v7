"""
Events List
Displays calendar events grouped by day with month navigation
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from collections import defaultdict
import logging

from .event_item_widget import EventItemWidget

logger = logging.getLogger(__name__)


class EventsList(QWidget):
    """
    Widget for displaying calendar events grouped by day
    Includes month navigation and event management
    """

    # Signals
    event_selected = pyqtSignal(dict)  # Emitted when event is selected
    create_event_requested = pyqtSignal()  # Emitted when "New Event" clicked
    edit_event_requested = pyqtSignal(dict)  # Emitted when edit requested
    refresh_needed = pyqtSignal()  # Emitted when list needs refresh

    def __init__(self, db_manager, parent=None):
        """
        Initialize events list

        Args:
            db_manager: DBManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.db = db_manager

        # Current month/year for navigation
        current_date = QDate.currentDate()
        self.current_year = current_date.year()
        self.current_month = current_date.month()

        self.setup_ui()
        self.apply_styles()
        self.load_events()

        logger.info(f"EventsList initialized for {self.current_year}-{self.current_month:02d}")

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Month navigation bar
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)

        # Previous month button
        self.btn_prev = QPushButton("◀")
        self.btn_prev.setFixedSize(40, 35)
        self.btn_prev.setToolTip("Mes anterior")
        self.btn_prev.clicked.connect(self.previous_month)

        # Month label
        self.month_label = QLabel()
        month_font = QFont()
        month_font.setPointSize(12)
        month_font.setBold(True)
        self.month_label.setFont(month_font)
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_month_label()

        # Next month button
        self.btn_next = QPushButton("▶")
        self.btn_next.setFixedSize(40, 35)
        self.btn_next.setToolTip("Mes siguiente")
        self.btn_next.clicked.connect(self.next_month)

        # Today button
        self.btn_today = QPushButton("Hoy")
        self.btn_today.setFixedWidth(80)
        self.btn_today.setToolTip("Ir al mes actual")
        self.btn_today.clicked.connect(self.go_to_today)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.month_label, 1)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addWidget(self.btn_today)

        layout.addLayout(nav_layout)

        # Events list
        self.events_list = QListWidget()
        self.events_list.setSpacing(2)
        layout.addWidget(self.events_list)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.btn_new_event = QPushButton("+ Nuevo Evento")
        self.btn_new_event.setMinimumHeight(35)
        self.btn_new_event.clicked.connect(self.create_event)

        self.btn_refresh = QPushButton("🔄 Actualizar")
        self.btn_refresh.setFixedWidth(120)
        self.btn_refresh.setMinimumHeight(35)
        self.btn_refresh.clicked.connect(self.load_events)

        buttons_layout.addWidget(self.btn_new_event, 1)
        buttons_layout.addWidget(self.btn_refresh)

        layout.addLayout(buttons_layout)

    def apply_styles(self):
        """Apply styles to the widget"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #cccccc;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #007acc;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            QListWidget {
                background-color: #252525;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: transparent;
                border: none;
            }
        """)

    def update_month_label(self):
        """Update the month label text"""
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        month_name = months[self.current_month - 1]
        self.month_label.setText(f"{month_name} {self.current_year}")

    def previous_month(self):
        """Navigate to previous month"""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        self.update_month_label()
        self.load_events()
        logger.debug(f"Navigated to previous month: {self.current_year}-{self.current_month:02d}")

    def next_month(self):
        """Navigate to next month"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1

        self.update_month_label()
        self.load_events()
        logger.debug(f"Navigated to next month: {self.current_year}-{self.current_month:02d}")

    def go_to_today(self):
        """Navigate to current month"""
        current_date = QDate.currentDate()
        self.current_year = current_date.year()
        self.current_month = current_date.month()

        self.update_month_label()
        self.load_events()
        logger.debug(f"Navigated to today: {self.current_year}-{self.current_month:02d}")

    def load_events(self):
        """Load events for current month from database"""
        try:
            logger.info(f"Loading events for {self.current_year}-{self.current_month:02d}")

            # Clear current list
            self.events_list.clear()

            # Get events from database
            events = self.db.get_events_by_month(self.current_year, self.current_month)

            if not events:
                # Show "no events" message
                item = QListWidgetItem("No hay eventos en este mes")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.events_list.addItem(item)
                logger.debug("No events found for this month")
                return

            # Group events by day
            events_by_day = defaultdict(list)
            for event in events:
                day = event['event_datetime'][:10]  # YYYY-MM-DD
                events_by_day[day].append(event)

            # Add events to list grouped by day
            for day in sorted(events_by_day.keys()):
                # Add day header
                self.add_day_header(day)

                # Add events for this day
                for event in events_by_day[day]:
                    self.add_event_item(event)

            logger.info(f"Loaded {len(events)} events in {len(events_by_day)} days")

        except Exception as e:
            logger.error(f"Error loading events: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar eventos: {str(e)}"
            )

    def add_day_header(self, day_str):
        """
        Add a day header to the list

        Args:
            day_str: Date string in YYYY-MM-DD format
        """
        # Parse date
        try:
            date_obj = datetime.strptime(day_str, "%Y-%m-%d")
            days_of_week = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            day_name = days_of_week[date_obj.weekday()]
            formatted_date = f"{day_name} {date_obj.day:02d}"
        except:
            formatted_date = day_str

        # Create header item
        header_text = f"📅 {formatted_date}"
        item = QListWidgetItem(header_text)
        item.setFlags(Qt.ItemFlag.NoItemFlags)  # Not selectable

        # Style the header
        header_font = QFont()
        header_font.setPointSize(10)
        header_font.setBold(True)
        item.setFont(header_font)
        item.setForeground(Qt.GlobalColor.white)
        item.setBackground(Qt.GlobalColor.darkGray)

        self.events_list.addItem(item)

    def add_event_item(self, event):
        """
        Add an event item to the list

        Args:
            event: Event dictionary
        """
        # Create EventItemWidget
        event_widget = EventItemWidget(event)

        # Connect signals
        event_widget.edit_requested.connect(self.on_edit_event)
        event_widget.delete_requested.connect(self.on_delete_event)

        # Create list item
        list_item = QListWidgetItem()
        list_item.setSizeHint(event_widget.sizeHint())
        list_item.setData(Qt.ItemDataRole.UserRole, event)

        # Add to list
        self.events_list.addItem(list_item)
        self.events_list.setItemWidget(list_item, event_widget)

    def create_event(self):
        """Handle new event button click"""
        logger.debug("Create event requested")
        self.create_event_requested.emit()

    def on_edit_event(self, event):
        """Handle edit event request"""
        logger.debug(f"Edit event: {event['id']}")
        self.edit_event_requested.emit(event)

    def on_delete_event(self, event):
        """Handle delete event request"""
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar el evento '{event.get('title', 'Sin título')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_calendar_event(event['id'])
                logger.info(f"Event deleted: {event['id']}")
                self.load_events()  # Refresh list
                self.refresh_needed.emit()
            except Exception as e:
                logger.error(f"Error deleting event: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error al eliminar evento: {str(e)}"
                )
