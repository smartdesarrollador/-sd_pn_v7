"""
Widget de selección de contexto COMPACTO para el Visor de Proyectos/Áreas

SOLO LECTURA: No permite crear proyectos ni áreas, solo seleccionar existentes.

Componentes:
- Selector de Proyecto (dropdown solo lectura)
- Selector de Área (dropdown solo lectura)

CRÍTICO: Proyecto y Área son MUTUAMENTE EXCLUYENTES
- Al seleccionar Proyecto → Área se resetea a "Ninguno"
- Al seleccionar Área → Proyecto se resetea a "Seleccionar proyecto..."

Señales:
- project_changed(int): Emitida cuando se selecciona un proyecto
- area_changed(int): Emitida cuando se selecciona un área

Versión: 1.0
Fecha: 2025-12-21
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class ContextSelectorCompact(QWidget):
    """
    Widget compacto para seleccionar Proyecto o Área (MUTUAMENTE EXCLUYENTES)

    Solo permite seleccionar elementos existentes. NO permite crear nuevos.

    Señales:
        project_changed(int): ID del proyecto seleccionado (o None)
        area_changed(int): ID del área seleccionada (o None)
    """

    # Señales
    project_changed = pyqtSignal(object)  # int or None
    area_changed = pyqtSignal(object)  # int or None

    def __init__(self, parent=None):
        """
        Inicializa el selector compacto

        Args:
            parent: Widget padre
        """
        super().__init__(parent)

        # Estado interno
        self._block_signals = False  # Para evitar bucles al resetear

        self._setup_ui()
        self._apply_styles()
        self._connect_signals()

        logger.debug("ContextSelectorCompact inicializado")

    def _setup_ui(self):
        """Configura la interfaz del widget"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header de la sección
        header = QLabel("📋 Contexto")
        header.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        header.setStyleSheet("color: #00BFFF; margin-bottom: 5px;")
        layout.addWidget(header)

        # Frame contenedor
        container = QFrame()
        container.setObjectName("contextContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)

        # Fila de Proyecto
        project_row = self._create_selector_row("Proyecto", "Seleccionar proyecto...")
        self.project_combo = project_row[1]
        container_layout.addLayout(project_row[0])

        # Fila de Área
        area_row = self._create_selector_row("Área", "Ninguno")
        self.area_combo = area_row[1]
        container_layout.addLayout(area_row[0])

        layout.addWidget(container)

    def _create_selector_row(self, label_text: str, placeholder: str):
        """
        Crea una fila con etiqueta + combobox

        Args:
            label_text: Texto de la etiqueta
            placeholder: Texto del placeholder

        Returns:
            tuple: (QHBoxLayout, QComboBox)
        """
        row = QHBoxLayout()
        row.setSpacing(10)

        # Etiqueta
        label = QLabel(label_text)
        label.setFixedWidth(70)
        label.setStyleSheet("""
            color: #ffffff;
            font-size: 11px;
            font-weight: 500;
        """)

        # ComboBox
        combo = QComboBox()
        combo.setPlaceholderText(placeholder)
        combo.setMinimumHeight(32)

        row.addWidget(label)
        row.addWidget(combo, 1)  # Stretch factor 1

        return (row, combo)

    def _apply_styles(self):
        """Aplica estilos CSS al widget"""
        self.setStyleSheet("""
            QFrame#contextContainer {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
            }

            QComboBox {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
            }

            QComboBox:hover {
                border-color: #00BFFF;
                background-color: #4d4d4d;
            }

            QComboBox:focus {
                border-color: #00BFFF;
            }

            QComboBox::drop-down {
                border: none;
                width: 20px;
            }

            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #999;
                margin-right: 5px;
            }

            QComboBox::down-arrow:hover {
                border-top-color: #00BFFF;
            }

            QComboBox QAbstractItemView {
                background-color: #3d3d3d;
                color: #ffffff;
                selection-background-color: #00BFFF;
                selection-color: #ffffff;
                border: 1px solid #555;
            }
        """)

    def _connect_signals(self):
        """Conecta señales internas"""
        self.project_combo.currentIndexChanged.connect(self._on_project_changed)
        self.area_combo.currentIndexChanged.connect(self._on_area_changed)

    # === CALLBACKS INTERNOS ===

    def _on_project_changed(self, index: int):
        """
        Callback cuando cambia la selección de proyecto

        CRÍTICO: Resetea área automáticamente (mutuamente excluyente)

        Args:
            index: Índice seleccionado en el combobox
        """
        if self._block_signals:
            return

        project_id = self.project_combo.currentData()

        if project_id:
            # OBLIGATORIO: Resetear área cuando se selecciona proyecto
            self.reset_area()
            logger.info(f"Proyecto seleccionado: {project_id} - Área reseteada")

            # Emitir señal
            self.project_changed.emit(project_id)
        else:
            # Se seleccionó placeholder
            logger.debug("Proyecto deseleccionado")
            self.project_changed.emit(None)

    def _on_area_changed(self, index: int):
        """
        Callback cuando cambia la selección de área

        CRÍTICO: Resetea proyecto automáticamente (mutuamente excluyente)

        Args:
            index: Índice seleccionado en el combobox
        """
        if self._block_signals:
            return

        area_id = self.area_combo.currentData()

        if area_id:
            # OBLIGATORIO: Resetear proyecto cuando se selecciona área
            self.reset_project()
            logger.info(f"Área seleccionada: {area_id} - Proyecto reseteado")

            # Emitir señal
            self.area_changed.emit(area_id)
        else:
            # Se seleccionó placeholder
            logger.debug("Área deseleccionada")
            self.area_changed.emit(None)

    # === MÉTODOS PÚBLICOS ===

    def load_projects(self, projects: list):
        """
        Cargar lista de proyectos en el dropdown

        Args:
            projects: Lista de tuplas [(id, name), ...]
        """
        logger.debug(f"🔄 load_projects() recibió: {projects}")
        logger.debug(f"🔄 Longitud: {len(projects)}")

        self._block_signals = True
        self.project_combo.clear()
        logger.debug("🔄 ComboBox limpiado")

        # Agregar placeholder
        self.project_combo.addItem("Seleccionar proyecto...", None)
        logger.debug("🔄 Placeholder agregado")

        # Agregar proyectos
        for project_id, project_name in projects:
            self.project_combo.addItem(project_name, project_id)
            logger.debug(f"🔄 Agregado: {project_name} (ID: {project_id})")

        self._block_signals = False
        logger.debug(f"✅ ComboBox tiene {self.project_combo.count()} items totales")

        # Log de todos los items
        for i in range(self.project_combo.count()):
            logger.debug(f"  Item {i}: {self.project_combo.itemText(i)} -> {self.project_combo.itemData(i)}")

    def load_areas(self, areas: list):
        """
        Cargar lista de áreas en el dropdown

        Args:
            areas: Lista de tuplas [(id, name), ...]
        """
        logger.debug(f"🔄 load_areas() recibió: {areas}")
        logger.debug(f"🔄 Longitud: {len(areas)}")

        self._block_signals = True
        self.area_combo.clear()
        logger.debug("🔄 ComboBox limpiado")

        # Agregar placeholder
        self.area_combo.addItem("Ninguno", None)
        logger.debug("🔄 Placeholder agregado")

        # Agregar áreas
        for area_id, area_name in areas:
            self.area_combo.addItem(area_name, area_id)
            logger.debug(f"🔄 Agregado: {area_name} (ID: {area_id})")

        self._block_signals = False
        logger.debug(f"✅ ComboBox tiene {self.area_combo.count()} items totales")

        # Log de todos los items
        for i in range(self.area_combo.count()):
            logger.debug(f"  Item {i}: {self.area_combo.itemText(i)} -> {self.area_combo.itemData(i)}")

    def get_selected_project_id(self):
        """
        Obtener ID del proyecto seleccionado

        Returns:
            int or None: ID del proyecto o None si no hay selección
        """
        return self.project_combo.currentData()

    def get_selected_area_id(self):
        """
        Obtener ID del área seleccionada

        Returns:
            int or None: ID del área o None si no hay selección
        """
        return self.area_combo.currentData()

    def reset_project(self):
        """
        Resetear selector de proyecto al placeholder

        Bloquea señales para evitar bucles al ser llamado desde _on_area_changed.
        """
        self._block_signals = True
        self.project_combo.setCurrentIndex(0)  # Placeholder
        self._block_signals = False
        logger.debug("Proyecto reseteado a placeholder")

    def reset_area(self):
        """
        Resetear selector de área al placeholder

        Bloquea señales para evitar bucles al ser llamado desde _on_project_changed.
        """
        self._block_signals = True
        self.area_combo.setCurrentIndex(0)  # Placeholder
        self._block_signals = False
        logger.debug("Área reseteada a placeholder")

    def has_project_selected(self) -> bool:
        """
        Verificar si hay un proyecto seleccionado

        Returns:
            bool: True si hay proyecto seleccionado, False si no
        """
        return self.get_selected_project_id() is not None

    def has_area_selected(self) -> bool:
        """
        Verificar si hay un área seleccionada

        Returns:
            bool: True si hay área seleccionada, False si no
        """
        return self.get_selected_area_id() is not None

    def validate_exclusivity(self) -> bool:
        """
        Validar que Proyecto y Área sean mutuamente excluyentes

        Returns:
            bool: True si la validación pasa (solo uno o ninguno seleccionado)

        Raises:
            AssertionError: Si ambos están seleccionados (no debería pasar)
        """
        has_project = self.has_project_selected()
        has_area = self.has_area_selected()

        # CRÍTICO: Nunca deben estar ambos seleccionados
        assert not (has_project and has_area), \
            "ERROR: Proyecto y Área no pueden estar seleccionados simultáneamente"

        return True


# === TEST ===
if __name__ == '__main__':
    """Test independiente del widget"""
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Crear widget
    widget = ContextSelectorCompact()

    # Cargar datos de prueba
    widget.load_projects([
        (1, "Proyecto Backend"),
        (2, "Proyecto Frontend"),
        (3, "Proyecto Mobile"),
    ])

    widget.load_areas([
        (1, "Área Desarrollo"),
        (2, "Área Testing"),
        (3, "Área DevOps"),
    ])

    # Conectar señales para testing
    widget.project_changed.connect(
        lambda pid: print(f"✓ Proyecto cambiado: {pid}")
    )
    widget.area_changed.connect(
        lambda aid: print(f"✓ Área cambiada: {aid}")
    )

    # Mostrar widget
    widget.setMinimumWidth(400)
    widget.show()

    sys.exit(app.exec())
