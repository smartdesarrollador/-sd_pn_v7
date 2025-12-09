"""
Advanced Taskbar Manager - Barra de tareas avanzada para gestión de ventanas/paneles minimizados

Características:
- Soporte para cualquier tipo de ventana/panel (genérico)
- Scroll horizontal cuando hay muchas pestañas
- Vista de lista desplegable para navegación rápida
- Agrupación por tipo de ventana
- Búsqueda en tiempo real de ventanas minimizadas
- Drag & drop para reordenar pestañas
- Tooltips informativos
- Animaciones suaves
"""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                             QLabel, QScrollArea, QGraphicsDropShadowEffect,
                             QMenu, QListWidget, QListWidgetItem, QLineEdit,
                             QFrame, QToolButton)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QSize
from PyQt6.QtGui import QCursor, QColor, QIcon
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MinimizedWindowButton(QPushButton):
    """Botón que representa una ventana/panel minimizado en la taskbar"""

    restore_requested = pyqtSignal(object)  # Ventana a restaurar
    close_requested = pyqtSignal(object)    # Ventana a cerrar

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window
        self.window_title = self._get_window_title()
        self.window_icon = self._get_window_icon()
        self.window_type = self._get_window_type()

        # Configurar botón
        self._setup_button()

    def _get_window_title(self) -> str:
        """Obtener título de la ventana"""
        # Para paneles flotantes
        if hasattr(self.window, 'entity_name'):
            return f"{self.window.entity_icon} {self.window.entity_name}"
        # Para ventanas normales
        elif hasattr(self.window, 'windowTitle'):
            return self.window.windowTitle()
        else:
            return "Untitled Window"

    def _get_window_icon(self) -> str:
        """Obtener icono representativo de la ventana"""
        # Iconos personalizados por tipo
        if hasattr(self.window, 'entity_icon') and self.window.entity_icon:
            return self.window.entity_icon

        # Iconos por tipo de clase
        class_name = self.window.__class__.__name__
        icons_map = {
            'ProjectsWindow': '📁',
            'AreasWindow': '🗂️',
            'SettingsWindow': '⚙️',
            'CategoryManagerWindow': '📂',
            'ProcessBuilderWindow': '⚙️',
            'TablesManagerWindow': '📊',
            'NotebookWindow': '📓',
            'SimpleBrowserWindow': '🌐',
            'ImageGalleryWindow': '🖼️',
            'AdvancedSearchWindow': '🔍',
            'FavoritesFloatingPanel': '⭐',
            'StatsFloatingPanel': '📈',
            'ProcessFloatingPanel': '⚙️',
            'GlobalSearchPanel': '🔍',
            'RelatedItemsFloatingPanel': '📄',
        }
        return icons_map.get(class_name, '🪟')

    def _get_window_type(self) -> str:
        """Obtener tipo de ventana para agrupación"""
        class_name = self.window.__class__.__name__

        # Categorizar por tipo
        if 'Floating' in class_name or 'Panel' in class_name:
            return 'panel'
        elif 'Window' in class_name:
            return 'window'
        elif 'Dialog' in class_name:
            return 'dialog'
        else:
            return 'other'

    def _setup_button(self):
        """Configurar apariencia y comportamiento del botón"""
        # Texto del botón
        display_text = self.window_title
        max_chars = 15  # ↓ ANTES: 25 - Truncamiento más agresivo
        if len(display_text) > max_chars:
            display_text = display_text[:max_chars-2] + "..."

        self.setText(display_text)
        self.setToolTip(f"{self.window_title}\nTipo: {self.window_type.title()}\n\nClick: Restaurar\nClick derecho: Opciones")

        # Dimensiones
        self.setMinimumWidth(90)      # ↓ ANTES: 120px
        self.setMaximumWidth(150)     # ↓ ANTES: 200px
        self.setMinimumHeight(32)     # ↓ ANTES: 40px
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Estilo según tipo
        self._apply_style()

        # Conectar señales
        self.clicked.connect(self._on_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _apply_style(self):
        """Aplicar estilos según el tipo de ventana"""
        # Colores por tipo
        colors = {
            'panel': {'border': '#00ccff', 'hover': '#00ff88'},
            'window': {'border': '#ff00ff', 'hover': '#ff66ff'},
            'dialog': {'border': '#ffaa00', 'hover': '#ffcc00'},
            'other': {'border': '#888888', 'hover': '#aaaaaa'}
        }

        color = colors.get(self.window_type, colors['other'])

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid {color['border']};
                border-radius: 4px;           /* ↓ ANTES: 6px */
                padding: 4px 8px;             /* ↓ ANTES: 6px 10px */
                font-size: 8pt;               /* ↓ ANTES: 9pt */
                font-weight: bold;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #3d3d3d;
                border-color: {color['hover']};
            }}
            QPushButton:pressed {{
                background-color: #1d1d1d;
            }}
        """)

    def _on_clicked(self):
        """Manejar click para restaurar ventana"""
        self.restore_requested.emit(self.window)

    def _show_context_menu(self, position):
        """Mostrar menú contextual con opciones"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #00ccff;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #00ccff;
                color: #000000;
            }
        """)

        # Acciones
        restore_action = menu.addAction(f"📖 Restaurar {self.window_type}")
        restore_action.triggered.connect(lambda: self.restore_requested.emit(self.window))

        menu.addSeparator()

        info_action = menu.addAction(f"ℹ️ Información")
        info_action.triggered.connect(self._show_window_info)

        menu.addSeparator()

        close_action = menu.addAction("✕ Cerrar")
        close_action.triggered.connect(lambda: self.close_requested.emit(self.window))

        menu.exec(self.mapToGlobal(position))

    def _show_window_info(self):
        """Mostrar información de la ventana"""
        from PyQt6.QtWidgets import QMessageBox
        info = f"""
        <b>Ventana:</b> {self.window_title}<br>
        <b>Tipo:</b> {self.window_type.title()}<br>
        <b>Clase:</b> {self.window.__class__.__name__}<br>
        <b>Tamaño:</b> {self.window.width()}x{self.window.height()}px
        """
        QMessageBox.information(self, "Información de Ventana", info)


class WindowsListWidget(QWidget):
    """Widget desplegable que muestra lista de todas las ventanas minimizadas"""

    window_selected = pyqtSignal(object)  # Ventana seleccionada

    def __init__(self, parent=None):
        super().__init__(parent)
        self.windows = []
        self.init_ui()

    def init_ui(self):
        """Inicializar UI del widget de lista"""
        # Window flags
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint
        )

        # Tamaño
        self.setFixedSize(350, 400)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header = QLabel("📋 Ventanas Minimizadas")
        header.setStyleSheet("""
            QLabel {
                color: #00ccff;
                font-size: 11pt;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(header)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar ventana...")
        self.search_input.textChanged.connect(self._filter_windows)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #00ccff;
                border-radius: 4px;
                padding: 8px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border-color: #00ff88;
            }
        """)
        layout.addWidget(self.search_input)

        # Lista de ventanas
        self.windows_list = QListWidget()
        self.windows_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #00ccff;
                border-radius: 4px;
                padding: 5px;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 3px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #00ccff;
                color: #000000;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
        """)
        self.windows_list.itemClicked.connect(self._on_window_clicked)
        layout.addWidget(self.windows_list)

        # Estilo del widget
        self.setStyleSheet("""
            WindowsListWidget {
                background-color: #1e1e1e;
                border: 3px solid #00ccff;
                border-radius: 8px;
            }
        """)

        # Sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(shadow)

    def set_windows(self, windows: List):
        """Establecer lista de ventanas"""
        self.windows = windows
        self._populate_list()

    def _populate_list(self):
        """Poblar lista con ventanas"""
        self.windows_list.clear()

        # Agrupar por tipo
        grouped = {'panel': [], 'window': [], 'dialog': [], 'other': []}

        for window in self.windows:
            # Determinar tipo
            class_name = window.__class__.__name__
            if 'Floating' in class_name or 'Panel' in class_name:
                grouped['panel'].append(window)
            elif 'Window' in class_name:
                grouped['window'].append(window)
            elif 'Dialog' in class_name:
                grouped['dialog'].append(window)
            else:
                grouped['other'].append(window)

        # Agregar items agrupados
        for group_type, group_windows in grouped.items():
            if not group_windows:
                continue

            # Separador de grupo
            if self.windows_list.count() > 0:
                separator_item = QListWidgetItem("─" * 40)
                separator_item.setFlags(Qt.ItemFlag.NoItemFlags)
                separator_item.setForeground(QColor("#555555"))
                self.windows_list.addItem(separator_item)

            # Header de grupo
            group_names = {
                'panel': '📋 PANELES',
                'window': '🪟 VENTANAS',
                'dialog': '💬 DIÁLOGOS',
                'other': '📦 OTROS'
            }
            header_item = QListWidgetItem(group_names.get(group_type, 'OTROS'))
            header_item.setFlags(Qt.ItemFlag.NoItemFlags)
            header_item.setForeground(QColor("#00ccff"))
            header_item.setBackground(QColor("#1a1a1a"))
            self.windows_list.addItem(header_item)

            # Ventanas del grupo
            for window in group_windows:
                title = self._get_window_title(window)
                icon = self._get_window_icon(window)

                item = QListWidgetItem(f"{icon} {title}")
                item.setData(Qt.ItemDataRole.UserRole, window)
                self.windows_list.addItem(item)

    def _get_window_title(self, window) -> str:
        """Obtener título de ventana"""
        if hasattr(window, 'entity_name'):
            return window.entity_name
        elif hasattr(window, 'windowTitle'):
            return window.windowTitle()
        return "Untitled"

    def _get_window_icon(self, window) -> str:
        """Obtener icono de ventana"""
        if hasattr(window, 'entity_icon') and window.entity_icon:
            return window.entity_icon

        class_name = window.__class__.__name__
        icons_map = {
            'ProjectsWindow': '📁',
            'AreasWindow': '🗂️',
            'SettingsWindow': '⚙️',
            'CategoryManagerWindow': '📂',
            'ProcessBuilderWindow': '⚙️',
            'TablesManagerWindow': '📊',
            'NotebookWindow': '📓',
            'SimpleBrowserWindow': '🌐',
            'ImageGalleryWindow': '🖼️',
            'AdvancedSearchWindow': '🔍',
            'FavoritesFloatingPanel': '⭐',
            'StatsFloatingPanel': '📈',
            'ProcessFloatingPanel': '⚙️',
            'GlobalSearchPanel': '🔍',
            'RelatedItemsFloatingPanel': '📄',
        }
        return icons_map.get(class_name, '🪟')

    def _filter_windows(self, text: str):
        """Filtrar ventanas por texto de búsqueda"""
        search_text = text.lower()

        for i in range(self.windows_list.count()):
            item = self.windows_list.item(i)

            # No filtrar separadores ni headers
            if not (item.flags() & Qt.ItemFlag.ItemIsEnabled):
                continue

            # Filtrar por texto
            item_text = item.text().lower()
            matches = search_text in item_text
            item.setHidden(not matches)

    def _on_window_clicked(self, item: QListWidgetItem):
        """Manejar click en ventana de la lista"""
        window = item.data(Qt.ItemDataRole.UserRole)
        if window:
            self.window_selected.emit(window)
            self.hide()


class AdvancedTaskbarManager(QWidget):
    """
    Gestor avanzado de barra de tareas para ventanas/paneles minimizados

    Características:
    - Scroll horizontal cuando hay muchas pestañas
    - Vista de lista desplegable
    - Agrupación por tipo
    - Búsqueda integrada
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.minimized_windows = []  # Lista de ventanas minimizadas
        self.window_buttons = {}  # Diccionario de botones por ventana

        # Registro global de ventanas abiertas
        self.all_open_windows = {}  # Key: window_id, Value: window instance

        # Vista de lista desplegable
        self.list_widget = None

        self.init_ui()
        self.hide()  # Oculto por defecto

        logger.info("AdvancedTaskbarManager initialized")

    def init_ui(self):
        """Inicializar UI del gestor avanzado"""
        # Window flags
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # No aparece en taskbar del sistema
        )

        # Atributos
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Tamaño
        self.setFixedHeight(50)  # ↓ ANTES: 70px - Diseño más compacto
        self.setMinimumWidth(300)

        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 4, 6, 4)  # ↓ ANTES: 10, 8, 10, 8 - Márgenes reducidos
        main_layout.setSpacing(6)  # ↓ ANTES: 10 - Menos espacio entre elementos

        # === SECCIÓN IZQUIERDA: Label + Botón de lista ===
        left_section = QWidget()
        left_layout = QHBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Label indicador
        self.label = QLabel("📋 Minimizados:")
        self.label.setStyleSheet("""
            QLabel {
                color: #00ccff;
                font-size: 8pt;          /* ↓ ANTES: 10pt - Texto compacto */
                font-weight: bold;
                padding: 2px 4px;        /* ↓ Padding agregado */
            }
        """)
        left_layout.addWidget(self.label)

        # Contador de ventanas
        self.counter_label = QLabel("0")
        self.counter_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #00ccff;
                font-size: 7pt;          /* ↓ ANTES: 9pt - Contador compacto */
                font-weight: bold;
                padding: 2px 6px;        /* ↓ ANTES: 4px 8px - Padding reducido */
                border-radius: 8px;      /* ↓ ANTES: 10px - Bordes más sutiles */
            }
        """)
        left_layout.addWidget(self.counter_label)

        # Botón para mostrar lista desplegable
        self.list_button = QToolButton()
        self.list_button.setText("▼")
        self.list_button.setToolTip("Ver lista de todas las ventanas minimizadas")
        self.list_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.list_button.clicked.connect(self._toggle_list_widget)
        self.list_button.setStyleSheet("""
            QToolButton {
                background-color: #2d2d2d;
                color: #00ccff;
                border: 2px solid #00ccff;
                border-radius: 4px;      /* ↓ ANTES: 6px - Diseño compacto */
                padding: 4px 6px;        /* ↓ ANTES: 6px 10px - Padding reducido */
                font-size: 9pt;          /* ↓ ANTES: 10pt - Fuente compacta */
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #3d3d3d;
                border-color: #00ff88;
            }
            QToolButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        left_layout.addWidget(self.list_button)

        main_layout.addWidget(left_section)

        # === SECCIÓN CENTRAL: Scroll area con botones de ventanas ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFixedHeight(40)  # ↓ ANTES: 55px - Altura compacta
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:horizontal {
                background-color: #2d2d2d;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background-color: #00ccff;
                border-radius: 4px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #00ff88;
            }
        """)

        # Container para botones
        self.buttons_container = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(8)
        self.buttons_layout.addStretch()

        self.scroll_area.setWidget(self.buttons_container)
        main_layout.addWidget(self.scroll_area, 1)

        # === SECCIÓN DERECHA: Botones de control ===
        right_section = QWidget()
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # Botón para restaurar todas
        restore_all_btn = QToolButton()
        restore_all_btn.setText("📖")
        restore_all_btn.setToolTip("Restaurar todas las ventanas")
        restore_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        restore_all_btn.clicked.connect(self.restore_all_windows)
        restore_all_btn.setStyleSheet("""
            QToolButton {
                background-color: #2d2d2d;
                color: #00ff88;
                border: 2px solid #00ff88;
                border-radius: 4px;      /* ↓ ANTES: 6px */
                padding: 4px 6px;        /* ↓ ANTES: 6px 10px */
                font-size: 9pt;          /* ↓ ANTES: 12pt */
            }
            QToolButton:hover {
                background-color: #3d3d3d;
            }
        """)
        right_layout.addWidget(restore_all_btn)

        # Botón para cerrar todas
        close_all_btn = QToolButton()
        close_all_btn.setText("✕")
        close_all_btn.setToolTip("Cerrar todas las ventanas minimizadas")
        close_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_all_btn.clicked.connect(self.close_all_windows)
        close_all_btn.setStyleSheet("""
            QToolButton {
                background-color: #2d2d2d;
                color: #ff4444;
                border: 2px solid #ff4444;
                border-radius: 4px;      /* ↓ ANTES: 6px */
                padding: 4px 6px;        /* ↓ ANTES: 6px 10px */
                font-size: 9pt;          /* ↓ ANTES: 12pt */
            }
            QToolButton:hover {
                background-color: #3d3d3d;
            }
        """)
        right_layout.addWidget(close_all_btn)

        main_layout.addWidget(right_section)

        # Estilo del widget principal
        self.setStyleSheet("""
            AdvancedTaskbarManager {
                background-color: #1e1e1e;
                border: 3px solid #00ccff;
                border-radius: 10px;
            }
        """)

        # Sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(-3)
        shadow.setColor(QColor(0, 204, 255, 100))
        self.setGraphicsEffect(shadow)

        # Posicionar en la parte inferior
        self.position_at_bottom()

    def position_at_bottom(self):
        """Posicionar el widget en la parte inferior central de la pantalla"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()

            # Calcular posición (centrado en la parte inferior)
            x = (screen_geometry.width() - self.width()) // 2
            y = screen_geometry.height() - self.height() - 15  # 15px de margen

            self.move(x, y)

    def add_minimized_window(self, window):
        """
        Agregar una ventana minimizada a la taskbar

        Args:
            window: Instancia de QWidget/QMainWindow/QDialog
        """
        if window in self.minimized_windows:
            logger.warning(f"Window already minimized: {window}")
            return

        self.minimized_windows.append(window)

        # Crear botón para la ventana
        button = MinimizedWindowButton(window)
        button.restore_requested.connect(self.restore_window)
        button.close_requested.connect(self.close_window)

        # Agregar botón al layout (antes del stretch)
        self.buttons_layout.insertWidget(self.buttons_layout.count() - 1, button)
        self.window_buttons[window] = button

        # Actualizar contador
        self._update_counter()

        # Ajustar ancho del widget
        self._adjust_width()

        # Actualizar textos de todos los botones (truncamiento dinámico)
        self._update_all_button_texts()

        # Mostrar taskbar con animación
        if not self.isVisible():
            self._show_with_animation()

        logger.info(f"Window minimized: {button.window_title}")

    def remove_minimized_window(self, window):
        """Remover una ventana minimizada de la taskbar"""
        if window not in self.minimized_windows:
            return

        self.minimized_windows.remove(window)

        # Remover botón
        if window in self.window_buttons:
            button = self.window_buttons[window]
            self.buttons_layout.removeWidget(button)
            button.deleteLater()
            del self.window_buttons[window]

        # Actualizar contador
        self._update_counter()

        # Ajustar ancho
        self._adjust_width()

        # Actualizar textos de todos los botones (truncamiento dinámico)
        self._update_all_button_texts()

        # Ocultar si no hay ventanas
        if not self.minimized_windows:
            self._hide_with_animation()

        logger.info(f"Window removed from taskbar")

    def restore_window(self, window):
        """Restaurar una ventana minimizada"""
        if window in self.minimized_windows:
            window.showNormal()
            window.activateWindow()
            window.raise_()
            self.remove_minimized_window(window)
            logger.info(f"Window restored")

    def close_window(self, window):
        """Cerrar una ventana completamente"""
        if window in self.minimized_windows:
            self.remove_minimized_window(window)
            window.close()
            logger.info(f"Window closed")

    def restore_all_windows(self):
        """Restaurar todas las ventanas minimizadas"""
        windows_to_restore = self.minimized_windows.copy()
        for window in windows_to_restore:
            self.restore_window(window)
        logger.info(f"All windows restored: {len(windows_to_restore)}")

    def close_all_windows(self):
        """Cerrar todas las ventanas minimizadas"""
        from PyQt6.QtWidgets import QMessageBox

        if not self.minimized_windows:
            return

        reply = QMessageBox.question(
            self,
            "Cerrar todas las ventanas",
            f"¿Cerrar {len(self.minimized_windows)} ventana(s) minimizada(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            windows_to_close = self.minimized_windows.copy()
            for window in windows_to_close:
                self.close_window(window)
            logger.info(f"All windows closed: {len(windows_to_close)}")

    def _update_counter(self):
        """Actualizar contador de ventanas"""
        count = len(self.minimized_windows)
        self.counter_label.setText(str(count))

    def _adjust_width(self):
        """Ajustar ancho del widget según cantidad de ventanas"""
        count = len(self.minimized_windows)
        if count == 0:
            new_width = 300
        else:
            # Ancho base + ancho por botón (con máximo)
            new_width = min(300 + (count * 140), 1400)  # Max 1400px

        self.setMinimumWidth(new_width)
        self.setMaximumWidth(new_width)

        # Reposicionar
        self.position_at_bottom()

    def _calculate_max_text_length(self) -> int:
        """
        Calcular longitud máxima de texto según cantidad de ventanas

        Returns:
            int: Máximo de caracteres a mostrar
        """
        window_count = len(self.minimized_windows)

        if window_count <= 3:
            return 20  # Texto completo
        elif window_count <= 6:
            return 15  # Texto medio
        elif window_count <= 10:
            return 12  # Texto corto
        else:
            return 8   # Texto muy corto

    def _update_all_button_texts(self):
        """Actualizar texto de todos los botones según espacio disponible"""
        max_chars = self._calculate_max_text_length()

        for window, button in self.window_buttons.items():
            title = button.window_title
            if len(title) > max_chars:
                button.setText(title[:max_chars-2] + "...")
            else:
                button.setText(title)

        logger.debug(f"Button texts updated: max_chars={max_chars}, count={len(self.minimized_windows)}")

    def _show_with_animation(self):
        """Mostrar taskbar con animación de entrada"""
        self.show()
        self.position_at_bottom()

        # Animación de fade in
        self.setWindowOpacity(0.0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()

    def _hide_with_animation(self):
        """Ocultar taskbar con animación de salida"""
        # Animación de fade out
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()

    def _toggle_list_widget(self):
        """Mostrar/ocultar widget de lista desplegable"""
        if not self.list_widget:
            self.list_widget = WindowsListWidget()
            self.list_widget.window_selected.connect(self.restore_window)

        if self.list_widget.isVisible():
            self.list_widget.hide()
        else:
            # Actualizar lista de ventanas
            self.list_widget.set_windows(self.minimized_windows)

            # Posicionar arriba del botón
            button_pos = self.list_button.mapToGlobal(self.list_button.rect().topLeft())
            list_x = button_pos.x()
            list_y = button_pos.y() - self.list_widget.height() - 10

            self.list_widget.move(list_x, list_y)
            self.list_widget.show()
            self.list_widget.search_input.setFocus()

    def resizeEvent(self, event):
        """Reposicionar al cambiar tamaño"""
        super().resizeEvent(event)
        self.position_at_bottom()

    # === MÉTODOS PARA REGISTRO GLOBAL DE VENTANAS ===

    def register_window(self, window, window_id: str):
        """
        Registrar una ventana abierta para mantener referencia

        Args:
            window: Instancia de la ventana
            window_id: ID único para la ventana

        Returns:
            window instance
        """
        if window_id in self.all_open_windows:
            existing = self.all_open_windows[window_id]
            if existing and not existing.isHidden():
                logger.info(f"Window already registered: {window_id}")
                existing.raise_()
                existing.activateWindow()
                return existing

        self.all_open_windows[window_id] = window
        logger.info(f"Window registered: {window_id}")
        return window

    def unregister_window(self, window_id: str):
        """Des-registrar una ventana cuando se cierra"""
        if window_id in self.all_open_windows:
            del self.all_open_windows[window_id]
            logger.info(f"Window unregistered: {window_id}")

    def get_registered_window(self, window_id: str):
        """Obtener ventana registrada por ID"""
        return self.all_open_windows.get(window_id)


# === SINGLETON GLOBAL ===
_advanced_taskbar_instance = None


def get_advanced_taskbar():
    """Obtener instancia única del gestor avanzado de taskbar"""
    global _advanced_taskbar_instance
    if _advanced_taskbar_instance is None:
        _advanced_taskbar_instance = AdvancedTaskbarManager()
        logger.info("Advanced Taskbar Manager singleton created")
    return _advanced_taskbar_instance
