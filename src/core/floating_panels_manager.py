"""
Floating Panels Manager - Gestiona paneles flotantes minimizados de forma independiente
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QCursor, QColor
import logging

logger = logging.getLogger(__name__)


class MinimizedPanelButton(QPushButton):
    """Botón que representa un panel minimizado"""

    restore_requested = pyqtSignal(object)  # Panel a restaurar
    close_requested = pyqtSignal(object)  # Panel a cerrar

    def __init__(self, panel, parent=None):
        super().__init__(parent)
        self.panel = panel
        self.entity_name = panel.entity_name
        self.entity_icon = panel.entity_icon

        # Configurar botón
        self.setText(f"{self.entity_icon} {self.entity_name}")
        self.setMinimumWidth(150)
        self.setMaximumWidth(250)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Estilo
        self.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #00ccff;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #00ff88;
            }
        """)

        # Conectar click para restaurar
        self.clicked.connect(self.on_restore_clicked)

        # Menú contextual para cerrar
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def on_restore_clicked(self):
        """Restaurar panel al hacer click"""
        self.restore_requested.emit(self.panel)

    def show_context_menu(self, position):
        """Mostrar menú contextual"""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()

        restore_action = menu.addAction("📖 Restaurar")
        restore_action.triggered.connect(lambda: self.restore_requested.emit(self.panel))

        close_action = menu.addAction("✕ Cerrar")
        close_action.triggered.connect(lambda: self.close_requested.emit(self.panel))

        menu.exec(self.mapToGlobal(position))


class FloatingPanelsManager(QWidget):
    """Widget que gestiona paneles flotantes minimizados - aparece en la parte inferior de la pantalla"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.minimized_panels = []  # Lista de paneles minimizados
        self.panel_buttons = {}  # Diccionario de botones por panel

        # IMPORTANTE: Mantener referencias a TODOS los paneles abiertos para evitar garbage collection
        # Key: f"{relation_type}_{entity_id}", Value: panel instance
        self.all_open_panels = {}

        self.init_ui()
        self.hide()  # Oculto por defecto

    def init_ui(self):
        """Inicializar UI del gestor"""
        # Window flags - ventana independiente en la parte inferior
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # Evita que aparezca en taskbar
        )

        # Tamaño fijo
        self.setFixedHeight(60)
        self.setMinimumWidth(200)

        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(8)

        # Label indicador
        self.label = QLabel("📋 Paneles minimizados:")
        self.label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 9pt;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.label)

        # Container para botones de paneles
        self.buttons_container = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_container)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(8)
        self.buttons_layout.addStretch()

        main_layout.addWidget(self.buttons_container, 1)

        # Estilo del widget
        self.setStyleSheet("""
            FloatingPanelsManager {
                background-color: #1e1e1e;
                border: 2px solid #00ccff;
                border-radius: 8px;
            }
        """)

        # Sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(-2)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)

        # Posicionar en la parte inferior central de la pantalla
        self.position_at_bottom()

    def position_at_bottom(self):
        """Posicionar el widget en la parte inferior central de la pantalla"""
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()

            # Calcular posición (centrado en la parte inferior)
            x = (screen_geometry.width() - self.width()) // 2
            y = screen_geometry.height() - self.height() - 10  # 10px de margen inferior

            self.move(x, y)

    def add_minimized_panel(self, panel):
        """Agregar un panel minimizado"""
        if panel in self.minimized_panels:
            return

        self.minimized_panels.append(panel)

        # Crear botón para el panel
        button = MinimizedPanelButton(panel)
        button.restore_requested.connect(self.restore_panel)
        button.close_requested.connect(self.close_panel)

        # Agregar botón al layout (antes del stretch)
        self.buttons_layout.insertWidget(self.buttons_layout.count() - 1, button)
        self.panel_buttons[panel] = button

        # Ajustar ancho del widget según cantidad de botones
        self.adjust_width()

        # Mostrar gestor si estaba oculto
        if not self.isVisible():
            self.show()
            self.position_at_bottom()

        logger.info(f"Panel minimizado agregado: {panel.entity_name}")

    def remove_minimized_panel(self, panel):
        """Remover un panel minimizado"""
        if panel not in self.minimized_panels:
            return

        self.minimized_panels.remove(panel)

        # Remover botón
        if panel in self.panel_buttons:
            button = self.panel_buttons[panel]
            self.buttons_layout.removeWidget(button)
            button.deleteLater()
            del self.panel_buttons[panel]

        # Ajustar ancho
        self.adjust_width()

        # Ocultar si no hay paneles
        if not self.minimized_panels:
            self.hide()

        logger.info(f"Panel minimizado removido: {panel.entity_name}")

    def restore_panel(self, panel):
        """Restaurar un panel minimizado"""
        if panel in self.minimized_panels:
            panel.showNormal()
            panel.activateWindow()
            self.remove_minimized_panel(panel)
            logger.info(f"Panel restaurado: {panel.entity_name}")

    def close_panel(self, panel):
        """Cerrar un panel completamente"""
        if panel in self.minimized_panels:
            self.remove_minimized_panel(panel)
            panel.close()
            logger.info(f"Panel cerrado: {panel.entity_name}")

    def adjust_width(self):
        """Ajustar ancho del widget según cantidad de paneles"""
        count = len(self.minimized_panels)
        if count == 0:
            new_width = 200
        else:
            # Ancho base + ancho por botón
            new_width = min(200 + (count * 180), 1200)  # Max 1200px

        self.setMinimumWidth(new_width)
        self.setMaximumWidth(new_width)

        # Reposicionar
        self.position_at_bottom()

    def resizeEvent(self, event):
        """Reposicionar al cambiar tamaño"""
        super().resizeEvent(event)
        self.position_at_bottom()

    def register_panel(self, panel, panel_key: str):
        """
        Registrar un panel abierto para mantener referencia y evitar garbage collection

        Args:
            panel: Instancia del panel flotante
            panel_key: Clave única (formato: "relation_type_entity_id")
        """
        # Si ya existe un panel con esta clave, traerlo al frente
        if panel_key in self.all_open_panels:
            existing_panel = self.all_open_panels[panel_key]
            if existing_panel and not existing_panel.isHidden():
                logger.info(f"Panel already registered: {panel_key}, bringing to front")
                existing_panel.raise_()
                existing_panel.activateWindow()
                return existing_panel

        # Registrar nuevo panel
        self.all_open_panels[panel_key] = panel
        logger.info(f"Panel registered: {panel_key} (Total: {len(self.all_open_panels)})")
        return panel

    def unregister_panel(self, panel_key: str):
        """
        Des-registrar un panel cuando se cierra

        Args:
            panel_key: Clave única del panel
        """
        if panel_key in self.all_open_panels:
            del self.all_open_panels[panel_key]
            logger.info(f"Panel unregistered: {panel_key} (Remaining: {len(self.all_open_panels)})")

    def get_registered_panel(self, panel_key: str):
        """
        Obtener un panel registrado por su clave

        Args:
            panel_key: Clave única del panel

        Returns:
            Panel instance o None si no existe
        """
        return self.all_open_panels.get(panel_key)


# Singleton global para el gestor
_panels_manager_instance = None


def get_panels_manager():
    """Obtener instancia única del gestor de paneles"""
    global _panels_manager_instance
    if _panels_manager_instance is None:
        _panels_manager_instance = FloatingPanelsManager()
    return _panels_manager_instance
