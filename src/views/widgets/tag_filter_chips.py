"""
Widget para mostrar tags como chips clickeables para filtrar (SOLO LECTURA)

Muestra una colección de tags en formato de chips con FlowLayout.
Los tags se pueden seleccionar/deseleccionar para filtrar elementos.

NO permite crear nuevos tags, solo visualizar y filtrar por existentes.

Características:
- FlowLayout: Los chips se ajustan automáticamente en filas
- Modo OR: Filtra elementos que tengan AL MENOS uno de los tags seleccionados
- Mensaje "Sin tags disponibles" si no hay tags

Señales:
- tags_changed(list): Emitida cuando cambia la selección de tags

Versión: 1.0
Fecha: 2025-12-21
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QFont
from src.views.widgets.tag_chip_button import TagChipButton
import logging

logger = logging.getLogger(__name__)


class FlowLayout(QLayout):
    """
    Layout que acomoda widgets en flujo horizontal con wrap automático a múltiples filas

    Basado en el ejemplo oficial de Qt: https://doc.qt.io/qt-6/qtwidgets-layouts-flowlayout-example.html
    Los widgets se colocan de izquierda a derecha y cuando no hay espacio, se envuelven a la siguiente fila.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_list = []
        self.h_space = 8  # Espacio horizontal entre items
        self.v_space = 6  # Espacio vertical entre filas

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        """Agrega un item al layout"""
        self.item_list.append(item)

    def count(self):
        """Retorna el número de items en el layout"""
        return len(self.item_list)

    def itemAt(self, index):
        """Retorna el item en el índice especificado"""
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        """Remueve y retorna el item en el índice especificado"""
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def expandingDirections(self):
        """Retorna las direcciones en las que el layout puede expandirse"""
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        """Indica que el layout tiene una altura que depende del ancho"""
        return True

    def heightForWidth(self, width):
        """Calcula la altura necesaria para un ancho dado"""
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        """Establece la geometría del layout y posiciona todos los items"""
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        """Retorna el tamaño sugerido del layout"""
        return self.minimumSize()

    def minimumSize(self):
        """Calcula el tamaño mínimo del layout"""
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        """
        Realiza el layout de los items

        Args:
            rect: Rectángulo disponible para el layout
            test_only: Si es True, solo calcula la altura sin posicionar los items

        Returns:
            int: Altura total necesaria
        """
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self.item_list:
            widget = item.widget()
            if not widget:
                continue

            space_x = self.h_space
            space_y = self.v_space
            next_x = x + item.sizeHint().width() + space_x

            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QRect(x, y, item.sizeHint().width(), item.sizeHint().height())))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom


class TagFilterChips(QWidget):
    """
    Widget para mostrar tags como chips clickeables para filtrar (SOLO LECTURA)

    No permite crear nuevos tags, solo visualizar y filtrar por existentes.

    Señales:
        tags_changed(list): Lista de nombres de tags seleccionados
    """

    # Señales
    tags_changed = pyqtSignal(list)  # Lista de tag_names seleccionados

    def __init__(self, parent=None):
        """
        Inicializa el widget de chips filtrables

        Args:
            parent: Widget padre
        """
        super().__init__(parent)

        # Estado interno
        self.tag_chips = {}  # {tag_name: TagChipButton}

        self._setup_ui()
        self._apply_styles()

        logger.debug("TagFilterChips inicializado")

    def _setup_ui(self):
        """Configura la interfaz del widget"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        # Header de la sección
        header = QLabel("🏷️ Tags de Proyecto/Área")
        header.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        header.setStyleSheet("color: #FFB300; margin-bottom: 5px;")
        main_layout.addWidget(header)

        # Frame contenedor
        self.container = QFrame()
        self.container.setObjectName("tagsContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(8)

        # FlowLayout para los chips
        self.flow_layout = FlowLayout()
        self.flow_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addLayout(self.flow_layout)

        # Label de mensaje (visible cuando no hay tags)
        self.no_tags_label = QLabel("No hay tags disponibles")
        self.no_tags_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_tags_label.setStyleSheet("""
            color: #808080;
            font-size: 10px;
            font-style: italic;
            padding: 10px;
        """)
        self.no_tags_label.setVisible(True)  # Visible por defecto
        container_layout.addWidget(self.no_tags_label)

        main_layout.addWidget(self.container)

    def _apply_styles(self):
        """Aplica estilos CSS al widget"""
        self.setStyleSheet("""
            QFrame#tagsContainer {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
            }
        """)

    def load_tags(self, tags: list):
        """
        Cargar lista de tags como chips

        Args:
            tags: Lista de diccionarios [{'name': str, 'color': str}, ...]
                  o lista de tuplas [(name, color), ...]
                  o lista de strings [name, ...]
        """
        # Limpiar chips existentes
        self.clear()

        if not tags:
            # No hay tags: mostrar mensaje
            self.no_tags_label.setVisible(True)
            logger.debug("No hay tags para cargar")
            return

        # Ocultar mensaje de "sin tags"
        self.no_tags_label.setVisible(False)

        # Crear chips para cada tag
        for tag_data in tags:
            # Manejar diferentes formatos de entrada
            if isinstance(tag_data, dict):
                tag_name = tag_data.get('name', '')
                tag_color = tag_data.get('color', '#808080')
            elif isinstance(tag_data, tuple):
                tag_name = tag_data[0]
                tag_color = tag_data[1] if len(tag_data) > 1 else '#808080'
            else:
                tag_name = str(tag_data)
                tag_color = '#808080'

            # Crear chip
            chip = TagChipButton(tag_name, tag_color)
            chip.state_changed.connect(self._on_chip_toggled)

            # Agregar al flow layout y al diccionario
            self.flow_layout.addWidget(chip)
            self.tag_chips[tag_name] = chip

        logger.info(f"Cargados {len(tags)} tags como chips")

    def _on_chip_toggled(self, checked: bool):
        """
        Callback cuando un chip cambia de estado

        Emite señal tags_changed con la lista de tags seleccionados.

        Args:
            checked: True si se activó, False si se desactivó
        """
        selected_tags = self.get_selected_tags()
        self.tags_changed.emit(selected_tags)
        logger.debug(f"Tags seleccionados: {selected_tags}")

    def get_selected_tags(self) -> list:
        """
        Obtener lista de nombres de tags seleccionados

        Returns:
            list: Lista de nombres de tags activos
        """
        selected = []
        for tag_name, chip in self.tag_chips.items():
            if chip.is_active():
                selected.append(tag_name)
        return selected

    def clear_selection(self):
        """Deseleccionar todos los tags"""
        for chip in self.tag_chips.values():
            chip.set_active(False)
        logger.debug("Selección de tags limpiada")

    def clear(self):
        """
        Limpiar todos los chips del widget

        Remueve todos los chips y limpia el diccionario.
        """
        # Remover todos los widgets del flow layout
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Limpiar diccionario
        self.tag_chips.clear()

        # Mostrar mensaje de "sin tags"
        self.no_tags_label.setVisible(True)

        logger.debug("Chips limpiados")

    def set_tags_active(self, tag_names: list):
        """
        Establecer tags específicos como activos

        Args:
            tag_names: Lista de nombres de tags a activar
        """
        for tag_name in tag_names:
            if tag_name in self.tag_chips:
                self.tag_chips[tag_name].set_active(True)

    def has_tags(self) -> bool:
        """
        Verificar si hay tags cargados

        Returns:
            bool: True si hay tags, False si no
        """
        return len(self.tag_chips) > 0


# === TEST ===
if __name__ == '__main__':
    """Test independiente del widget"""
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Crear widget
    widget = TagFilterChips()

    # Cargar datos de prueba
    test_tags = [
        {'name': 'python', 'color': '#3776ab'},
        {'name': 'backend', 'color': '#00ff88'},
        {'name': 'api', 'color': '#ff6b6b'},
        {'name': 'database', 'color': '#4ecdc4'},
        {'name': 'async', 'color': '#ffe66d'},
        {'name': 'testing', 'color': '#a8dadc'},
        {'name': 'docker', 'color': '#1d3557'},
    ]

    widget.load_tags(test_tags)

    # Conectar señal para testing
    widget.tags_changed.connect(
        lambda tags: print(f"✓ Tags seleccionados: {tags}")
    )

    # Mostrar widget
    widget.setMinimumWidth(400)
    widget.setStyleSheet("background-color: #1e1e1e;")
    widget.show()

    sys.exit(app.exec())
