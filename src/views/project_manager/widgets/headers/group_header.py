"""
Widget de encabezado de grupo de items para vista completa

Muestra el nombre del grupo (categoría, lista o tag de items).
Para listas, incluye botón "+" para crear lista.

Autor: Widget Sidebar Team
Versión: 1.1
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from ...styles.full_view_styles import FullViewStyles


class GroupHeaderWidget(QFrame):
    """
    Widget de encabezado de grupo de items

    Nivel 3 de jerarquía: Muestra el nombre del grupo de items
    (categoría, lista o tag de items).

    Para listas, incluye botón "+" para crear nueva lista.

    Señales:
        create_list_clicked: Emitida cuando se hace click en el botón "+" (solo para listas)
    """

    # Señales
    create_list_clicked = pyqtSignal()

    def __init__(self, parent=None):
        """
        Inicializar widget de encabezado de grupo

        Args:
            parent: Widget padre
        """
        super().__init__(parent)

        self.group_name = ""
        self.group_type = "category"  # 'category', 'list', 'tag'
        self.create_list_btn = None  # Solo para listas

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(30, 5, 10, 5)
        self.layout.setSpacing(8)

        # Título del grupo
        self.title_label = QLabel()
        self.title_label.setObjectName("group_title")
        self.layout.addWidget(self.title_label)

        # Spacer para alinear a la izquierda
        self.layout.addStretch()

    def apply_styles(self):
        """Aplicar estilos CSS"""
        self.setStyleSheet(FullViewStyles.get_group_header_style())

    def set_group_info(self, name: str, group_type: str = "category"):
        """
        Establecer información del grupo

        Args:
            name: Nombre del grupo
            group_type: Tipo de grupo ('category', 'list', 'tag')
        """
        self.group_name = name
        self.group_type = group_type

        # Remover botón anterior si existe
        if self.create_list_btn:
            self.create_list_btn.deleteLater()
            self.create_list_btn = None

        # Formato según tipo
        if group_type == "category":
            self.title_label.setText(f"[ Categoría: {name} ]")
        elif group_type == "list":
            self.title_label.setText(f"[ Lista: {name} ]")
            # Agregar botón "+" para crear lista
            self._add_create_list_button()
        elif group_type == "tag":
            self.title_label.setText(f"[ Tag: {name} ]")
        else:
            self.title_label.setText(f"[ {name} ]")

    def _add_create_list_button(self):
        """Agregar botón '+' para crear lista (solo cuando es tipo 'list')"""
        if self.create_list_btn:
            return  # Ya existe

        self.create_list_btn = QPushButton("+")
        self.create_list_btn.setFixedSize(24, 24)
        self.create_list_btn.setToolTip("Crear nueva lista")
        self.create_list_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d5d2e;
                color: #00ff88;
                border: 2px solid #00ff88;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a7a3c;
                border-color: #7CFC00;
            }
            QPushButton:pressed {
                background-color: #1a4d2e;
            }
        """)
        self.create_list_btn.clicked.connect(self.create_list_clicked.emit)

        # Insertar botón antes del spacer
        self.layout.insertWidget(self.layout.count() - 1, self.create_list_btn)

    def get_group_name(self) -> str:
        """
        Obtener nombre del grupo

        Returns:
            Nombre del grupo
        """
        return self.group_name

    def get_group_type(self) -> str:
        """
        Obtener tipo del grupo

        Returns:
            Tipo del grupo ('category', 'list', 'tag')
        """
        return self.group_type
