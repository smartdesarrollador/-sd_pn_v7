"""
Taskbar Minimizable Mixin - Mixin para agregar soporte de minimización a ventanas/paneles

Este mixin permite que cualquier ventana/panel pueda minimizarse a la barra de tareas avanzada.

Uso:
    class MyWindow(QMainWindow, TaskbarMinimizableMixin):
        def __init__(self):
            super().__init__()
            self.setup_taskbar_minimization()  # Configurar soporte de minimización

        # Luego usar:
        # self.minimize_to_taskbar()  # Minimizar a taskbar
        # self.restore_from_taskbar()  # Restaurar desde taskbar
"""
from PyQt6.QtWidgets import QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
import logging

logger = logging.getLogger(__name__)


class TaskbarMinimizableMixin:
    """
    Mixin que proporciona funcionalidad de minimización a barra de tareas

    Métodos proporcionados:
        - setup_taskbar_minimization(): Configurar soporte (llamar en __init__)
        - minimize_to_taskbar(): Minimizar ventana a taskbar
        - restore_from_taskbar(): Restaurar ventana desde taskbar
        - add_minimize_button(): Agregar botón de minimizar al header (opcional)

    Atributos requeridos en la clase que usa el mixin:
        - windowTitle() o entity_name: Para identificar la ventana
        - (Opcional) entity_icon: Icono personalizado
    """

    # Señal emitida cuando se minimiza
    minimized_to_taskbar = pyqtSignal()

    # Señal emitida cuando se restaura
    restored_from_taskbar = pyqtSignal()

    def setup_taskbar_minimization(self, auto_minimize_on_hide: bool = False):
        """
        Configurar soporte de minimización a taskbar

        Args:
            auto_minimize_on_hide: Si True, minimiza automáticamente cuando se oculta la ventana
        """
        self._auto_minimize_on_hide = auto_minimize_on_hide
        self._is_minimized_to_taskbar = False

        logger.debug(f"Taskbar minimization setup for {self._get_window_identifier()}")

    def minimize_to_taskbar(self):
        """Minimizar esta ventana a la barra de tareas avanzada"""
        try:
            from src.core.advanced_taskbar_manager import get_advanced_taskbar

            # Obtener gestor de taskbar
            taskbar = get_advanced_taskbar()

            # Ocultar ventana
            self.hide()

            # Agregar a taskbar
            taskbar.add_minimized_window(self)

            # Marcar como minimizada
            self._is_minimized_to_taskbar = True

            # Emitir señal
            if hasattr(self, 'minimized_to_taskbar'):
                self.minimized_to_taskbar.emit()

            logger.info(f"Window minimized to taskbar: {self._get_window_identifier()}")

        except Exception as e:
            logger.error(f"Error minimizing to taskbar: {e}", exc_info=True)

    def restore_from_taskbar(self):
        """Restaurar esta ventana desde la barra de tareas"""
        try:
            from src.core.advanced_taskbar_manager import get_advanced_taskbar

            # Obtener gestor de taskbar
            taskbar = get_advanced_taskbar()

            # Restaurar ventana
            taskbar.restore_window(self)

            # Marcar como no minimizada
            self._is_minimized_to_taskbar = False

            # Emitir señal
            if hasattr(self, 'restored_from_taskbar'):
                self.restored_from_taskbar.emit()

            logger.info(f"Window restored from taskbar: {self._get_window_identifier()}")

        except Exception as e:
            logger.error(f"Error restoring from taskbar: {e}", exc_info=True)

    def add_minimize_button(self, header_layout: QHBoxLayout, position: int = -1):
        """
        Agregar botón de minimizar a un layout de header

        Args:
            header_layout: Layout donde agregar el botón (usualmente QHBoxLayout del header)
            position: Posición donde insertar (-1 para el final)

        Returns:
            QPushButton: El botón creado
        """
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        minimize_btn.setToolTip("Minimizar a barra de tareas")
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ccff;
                color: #000000;
                border-color: #00ccff;
            }
        """)
        minimize_btn.clicked.connect(self.minimize_to_taskbar)

        # Agregar al layout
        if position == -1:
            header_layout.addWidget(minimize_btn)
        else:
            header_layout.insertWidget(position, minimize_btn)

        return minimize_btn

    def _get_window_identifier(self) -> str:
        """Obtener identificador único de la ventana"""
        if hasattr(self, 'entity_name'):
            return self.entity_name
        elif hasattr(self, 'windowTitle'):
            return self.windowTitle()
        else:
            return self.__class__.__name__

    def hideEvent(self, event):
        """
        Override hideEvent para auto-minimizar si está configurado

        IMPORTANTE: Si la clase que usa el mixin ya tiene un hideEvent,
        debe llamar a super().hideEvent(event) o a TaskbarMinimizableMixin.hideEvent(self, event)
        """
        # Auto-minimizar si está habilitado y no está ya minimizada
        if (hasattr(self, '_auto_minimize_on_hide') and
            self._auto_minimize_on_hide and
            not getattr(self, '_is_minimized_to_taskbar', False)):
            self.minimize_to_taskbar()

        # Llamar al hideEvent original si existe
        if hasattr(super(), 'hideEvent'):
            super().hideEvent(event)

    def closeEvent(self, event):
        """
        Override closeEvent para remover de taskbar al cerrar

        IMPORTANTE: Si la clase que usa el mixin ya tiene un closeEvent,
        debe llamar a super().closeEvent(event) o a TaskbarMinimizableMixin.closeEvent(self, event)
        """
        try:
            # Si está minimizada, remover de taskbar
            if getattr(self, '_is_minimized_to_taskbar', False):
                from src.core.advanced_taskbar_manager import get_advanced_taskbar
                taskbar = get_advanced_taskbar()
                taskbar.remove_minimized_window(self)

        except Exception as e:
            logger.error(f"Error removing from taskbar on close: {e}")

        # Llamar al closeEvent original si existe
        if hasattr(super(), 'closeEvent'):
            super().closeEvent(event)


# === FUNCIÓN HELPER PARA AGREGAR MINIMIZACIÓN A VENTANAS EXISTENTES ===

def make_window_minimizable(window, auto_minimize: bool = False) -> None:
    """
    Función helper para agregar soporte de minimización a una ventana existente

    Esta función es útil cuando no puedes usar herencia múltiple (mixin)
    y quieres agregar dinámicamente soporte de minimización a una ventana.

    Args:
        window: Instancia de QWidget/QMainWindow/QDialog
        auto_minimize: Si True, minimiza automáticamente al ocultar

    Ejemplo:
        window = ProjectsWindow()
        make_window_minimizable(window, auto_minimize=True)
        window.minimize_to_taskbar()  # Ahora disponible
    """
    # Agregar métodos al objeto
    window._auto_minimize_on_hide = auto_minimize
    window._is_minimized_to_taskbar = False

    # Método minimize_to_taskbar
    def minimize_to_taskbar():
        from src.core.advanced_taskbar_manager import get_advanced_taskbar
        taskbar = get_advanced_taskbar()
        window.hide()
        taskbar.add_minimized_window(window)
        window._is_minimized_to_taskbar = True
        logger.info(f"Window minimized to taskbar (dynamic)")

    # Método restore_from_taskbar
    def restore_from_taskbar():
        from src.core.advanced_taskbar_manager import get_advanced_taskbar
        taskbar = get_advanced_taskbar()
        taskbar.restore_window(window)
        window._is_minimized_to_taskbar = False
        logger.info(f"Window restored from taskbar (dynamic)")

    # Método add_minimize_button
    def add_minimize_button(header_layout, position=-1):
        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        minimize_btn.setToolTip("Minimizar a barra de tareas")
        minimize_btn.clicked.connect(window.minimize_to_taskbar)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                font-size: 14pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ccff;
                color: #000000;
                border-color: #00ccff;
            }
        """)
        if position == -1:
            header_layout.addWidget(minimize_btn)
        else:
            header_layout.insertWidget(position, minimize_btn)
        return minimize_btn

    # Agregar métodos al objeto window
    window.minimize_to_taskbar = minimize_to_taskbar
    window.restore_from_taskbar = restore_from_taskbar
    window.add_minimize_button = add_minimize_button

    # Override hideEvent si auto_minimize está habilitado
    if auto_minimize:
        original_hide_event = window.hideEvent

        def new_hide_event(event):
            if not window._is_minimized_to_taskbar:
                window.minimize_to_taskbar()
            original_hide_event(event)

        window.hideEvent = new_hide_event

    # Override closeEvent para limpiar
    original_close_event = window.closeEvent

    def new_close_event(event):
        if window._is_minimized_to_taskbar:
            from src.core.advanced_taskbar_manager import get_advanced_taskbar
            taskbar = get_advanced_taskbar()
            taskbar.remove_minimized_window(window)
        original_close_event(event)

    window.closeEvent = new_close_event

    logger.info(f"Window made minimizable dynamically: {window.__class__.__name__}")
