"""
Related Item Card Widget - Compact item display with checkbox for selection
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QPushButton, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QCursor
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from models.item import Item, ItemType
from styles.panel_styles import PanelStyles
from styles.futuristic_theme import get_theme

logger = logging.getLogger(__name__)


class RelatedItemCard(QFrame):
    """Widget compacto para mostrar un item con checkbox de selección"""

    # Señales
    checkbox_toggled = pyqtSignal(object, bool)  # item (Item object), is_checked
    copy_clicked = pyqtSignal(object)  # item (Item object)
    edit_requested = pyqtSignal(object)  # item (Item object)

    def __init__(self, item: Item, show_labels: bool = True, show_tags: bool = False,
                 show_content: bool = False, show_description: bool = False, parent=None):
        super().__init__(parent)

        self.item = item
        self.show_labels = show_labels
        self.show_tags = show_tags
        self.show_content = show_content
        self.show_description = show_description

        self.theme = get_theme()

        # State tracking
        self.is_selected_state = False
        self.is_revealed = False  # For sensitive content reveal

        self.init_ui()

    def init_ui(self):
        """Inicializar la interfaz del card"""
        # Frame properties - altura dinámica según opciones
        # Calcular altura necesaria
        base_height = 45  # Altura base con solo label
        if self.show_tags:
            base_height += 20
        if self.show_content:
            base_height += 20
        if self.show_description:
            base_height += 20

        self.setMinimumHeight(base_height)
        self.setMaximumHeight(base_height + 10)
        self.setMinimumWidth(300)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        # Apply enhanced item style with hover and selection states
        self.setStyleSheet(self._get_card_style())

        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(
            PanelStyles.ITEM_PADDING_H,
            PanelStyles.ITEM_PADDING_V,
            PanelStyles.ITEM_PADDING_H,
            PanelStyles.ITEM_PADDING_V
        )
        main_layout.setSpacing(PanelStyles.ICON_SPACING)

        # ========== CHECKBOX ==========
        self.checkbox = QCheckBox()
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {self.theme.get_color('primary')};
                border-radius: 3px;
                background-color: {self.theme.get_color('background_deep')};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.theme.get_color('primary')};
                border-color: {self.theme.get_color('primary')};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.theme.get_color('accent')};
            }}
        """)
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        main_layout.addWidget(self.checkbox)

        # ========== TYPE ICON ==========
        type_emoji = PanelStyles.get_icon_type_emoji(self.item.type)
        type_color = PanelStyles.get_icon_type_color(self.item.type)
        self.type_icon = QLabel(type_emoji)
        self.type_icon.setFixedSize(PanelStyles.ICON_SIZE, PanelStyles.ICON_SIZE)
        self.type_icon.setStyleSheet(f"""
            QLabel {{
                color: {type_color};
                font-size: {PanelStyles.ICON_SIZE}px;
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """)
        self.type_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_icon.setToolTip(f"Tipo: {self.item.type}")
        main_layout.addWidget(self.type_icon)

        # ========== ITEM INFO (expandable) ==========
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 0, 0, 0)

        # Label (always shown if show_labels is True)
        if self.show_labels:
            self.label_widget = QLabel(self.item.label)
            self.label_widget.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme.get_color('text_primary')};
                    font-size: 10pt;
                    font-weight: bold;
                    background: transparent;
                }}
            """)
            self.label_widget.setWordWrap(False)
            self.label_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            info_layout.addWidget(self.label_widget)

        # Tags (if enabled and item has tags)
        if self.show_tags and hasattr(self.item, 'tags') and self.item.tags:
            tags_text = " ".join([f"#{tag}" for tag in self.item.tags])
            tags_label = QLabel(tags_text)
            tags_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme.get_color('secondary')};
                    font-size: 8pt;
                    background: transparent;
                }}
            """)
            tags_label.setWordWrap(False)
            info_layout.addWidget(tags_label)

        # Content preview (if enabled)
        if self.show_content and self.item.content:
            if self.item.is_sensitive:
                # Create horizontal layout for sensitive content with reveal button
                content_layout = QHBoxLayout()
                content_layout.setSpacing(5)
                content_layout.setContentsMargins(0, 0, 0, 0)

                self.content_label = QLabel("🔒 Contenido cifrado")
                self.content_label.setStyleSheet(f"""
                    QLabel {{
                        color: {self.theme.get_color('warning')};
                        font-size: 8pt;
                        background: transparent;
                    }}
                """)
                self.content_label.setWordWrap(False)
                content_layout.addWidget(self.content_label, 1)

                # Reveal button for sensitive content
                self.reveal_button = QPushButton("👁")
                self.reveal_button.setFixedSize(20, 20)
                self.reveal_button.setCursor(Qt.CursorShape.PointingHandCursor)
                self.reveal_button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {self.theme.get_color('warning')};
                        border: 1px solid {self.theme.get_color('warning')};
                        border-radius: 3px;
                        font-size: 10pt;
                        padding: 0px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.theme.get_color('warning')};
                        color: {self.theme.get_color('background_deep')};
                    }}
                """)
                self.reveal_button.setToolTip("Mostrar contenido sensible temporalmente")
                self.reveal_button.clicked.connect(self.toggle_reveal_sensitive)
                content_layout.addWidget(self.reveal_button)

                info_layout.addLayout(content_layout)
            else:
                content_preview = self.item.content[:80]
                if len(self.item.content) > 80:
                    content_preview += "..."

                self.content_label = QLabel(content_preview)
                self.content_label.setStyleSheet(f"""
                    QLabel {{
                        color: {self.theme.get_color('text_secondary')};
                        font-size: 8pt;
                        background: transparent;
                    }}
                """)
                self.content_label.setWordWrap(False)
                info_layout.addWidget(self.content_label)

        # Description (if enabled)
        if self.show_description and self.item.description:
            desc_label = QLabel(self.item.description[:100])
            desc_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme.get_color('text_secondary')};
                    font-size: 8pt;
                    font-style: italic;
                    background: transparent;
                }}
            """)
            desc_label.setWordWrap(False)
            info_layout.addWidget(desc_label)

        main_layout.addLayout(info_layout, 1)  # Stretch factor 1

        # ========== BADGES ==========
        # Favorite badge
        if hasattr(self.item, 'is_favorite') and self.item.is_favorite:
            fav_badge = QLabel("⭐")
            fav_badge.setStyleSheet(PanelStyles.get_badge_style('favorite'))
            fav_badge.setToolTip("Favorito")
            main_layout.addWidget(fav_badge)

        # Sensitive badge
        if self.item.is_sensitive:
            sensitive_badge = QLabel("🔒")
            sensitive_badge.setStyleSheet(PanelStyles.get_badge_style('default'))
            sensitive_badge.setToolTip("Contenido sensible")
            main_layout.addWidget(sensitive_badge)

        # ========== COPY BUTTON ==========
        self.copy_button = QPushButton("📋")
        self.copy_button.setFixedSize(30, 30)
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.get_color('background_deep')};
                color: {self.theme.get_color('text_primary')};
                border: 1px solid {self.theme.get_color('surface')};
                border-radius: 4px;
                font-size: 12pt;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.get_color('secondary')};
                border-color: {self.theme.get_color('primary')};
            }}
            QPushButton:pressed {{
                background-color: {self.theme.get_color('accent')};
            }}
        """)
        self.copy_button.setToolTip("Copiar al portapapeles")
        self.copy_button.clicked.connect(self.on_copy_clicked)
        main_layout.addWidget(self.copy_button)

        # Set tooltip
        self._update_tooltip()

    def _update_tooltip(self):
        """Actualizar tooltip del card"""
        tooltip_parts = []

        if self.item.description:
            tooltip_parts.append(self.item.description)

        if not self.item.is_sensitive and self.item.content:
            preview = self.item.content[:100]
            if len(self.item.content) > 100:
                preview += "..."
            tooltip_parts.append(f"\n{preview}")

        tooltip_parts.append(f"\nTipo: {self.item.type}")

        self.setToolTip("\n".join(tooltip_parts))

    def on_checkbox_changed(self, state):
        """Handle checkbox state change"""
        is_checked = state == Qt.CheckState.Checked.value
        self.is_selected_state = is_checked

        # Update card appearance based on selection
        self.setStyleSheet(self._get_card_style())

        self.checkbox_toggled.emit(self.item, is_checked)

    def on_copy_clicked(self):
        """Handle copy button click"""
        # Copy to clipboard
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.item.content)

        logger.info(f"Item copied to clipboard: {self.item.label}")

        # Visual feedback
        original_text = self.copy_button.text()
        self.copy_button.setText("✅")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.copy_button.setText(original_text))

        # Emit signal
        self.copy_clicked.emit(self.item)

    def set_checked(self, checked: bool):
        """Establecer el estado del checkbox programáticamente"""
        self.checkbox.setChecked(checked)

    def is_checked(self) -> bool:
        """Obtener el estado actual del checkbox"""
        return self.checkbox.isChecked()

    def toggle_reveal_sensitive(self):
        """Toggle reveal of sensitive content (temporary, auto-hide after 5 seconds)"""
        # Check if widget still exists
        try:
            if not self.isVisible():
                return
        except RuntimeError:
            # Widget has been deleted
            return

        if not self.item.is_sensitive or not self.show_content:
            return

        if self.is_revealed:
            # Hide content again
            self.content_label.setText("🔒 Contenido cifrado")
            self.content_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme.get_color('warning')};
                    font-size: 8pt;
                    background: transparent;
                }}
            """)
            self.reveal_button.setText("👁")
            self.is_revealed = False
            logger.info("Sensitive content hidden")
        else:
            # Show content
            content_preview = self.item.content[:80]
            if len(self.item.content) > 80:
                content_preview += "..."

            self.content_label.setText(content_preview)
            self.content_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.theme.get_color('success')};
                    font-size: 8pt;
                    background: transparent;
                    font-weight: bold;
                }}
            """)
            self.reveal_button.setText("🙈")
            self.is_revealed = True
            logger.info("Sensitive content revealed")

            # Auto-hide after 5 seconds
            QTimer.singleShot(5000, self.toggle_reveal_sensitive)

    def _get_card_style(self) -> str:
        """Obtener estilos del card según estado (normal, hover, seleccionado)"""
        base_bg = self.theme.get_color('background_mid')
        hover_bg = self.theme.get_color('surface')
        selected_bg = self.theme.get_color('primary_dark') if hasattr(self.theme, 'get_color') else '#1e3a5f'

        # Si está seleccionado, usar color de selección
        if self.is_selected_state:
            bg_color = selected_bg
            border_color = self.theme.get_color('primary')
        else:
            bg_color = base_bg
            border_color = self.theme.get_color('surface')

        return f"""
            RelatedItemCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                margin: 2px 0px;
            }}
            RelatedItemCard:hover {{
                background-color: {hover_bg};
                border-color: {self.theme.get_color('primary')};
            }}
        """

    def enterEvent(self, event):
        """Handle mouse enter event for hover effect"""
        try:
            super().enterEvent(event)
            if not self.is_selected_state:
                # Apply hover style
                self.setProperty("hover", True)
                self.style().unpolish(self)
                self.style().polish(self)
        except RuntimeError:
            # Widget ya fue eliminado - ignorar silenciosamente
            pass

    def leaveEvent(self, event):
        """Handle mouse leave event"""
        try:
            super().leaveEvent(event)
            if not self.is_selected_state:
                # Remove hover style
                self.setProperty("hover", False)
                self.style().unpolish(self)
                self.style().polish(self)
        except RuntimeError:
            # Widget ya fue eliminado - ignorar silenciosamente
            pass

    def mouseDoubleClickEvent(self, event):
        """Handle double click to edit item"""
        if event.button() == Qt.MouseButton.LeftButton:
            logger.info(f"Double click on item: {self.item.label}")
            self.edit_requested.emit(self.item)
        super().mouseDoubleClickEvent(event)
