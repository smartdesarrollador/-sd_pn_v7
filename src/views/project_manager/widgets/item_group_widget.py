"""
Widget contenedor de grupo de items

Agrupa items bajo un encabezado de grupo (categoría, lista o tag).
Para listas, incluye botones de "+ Agregar Item".

Autor: Widget Sidebar Team
Versión: 1.1
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from .headers.group_header import GroupHeaderWidget
from .items import TextItemWidget, CodeItemWidget, URLItemWidget, PathItemWidget, WebStaticItemWidget


class ItemGroupWidget(QWidget):
    """
    Widget contenedor de grupo de items

    Agrupa items bajo un encabezado de grupo.
    Renderiza cada item con el widget apropiado según su tipo.
    Para listas, incluye botones "+ Agregar Item".

    Nivel de jerarquía: Grupos (categorías, listas, tags de items)

    Señales:
        create_list_clicked: Emitida cuando se hace click en "+" del header (solo listas)
        add_item_clicked: Emitida cuando se hace click en "+ Agregar Item" (solo listas)
    """

    # Señales
    create_list_clicked = pyqtSignal()
    add_item_clicked = pyqtSignal()

    def __init__(self, group_name: str, group_type: str = "category", parent=None):
        """
        Inicializar widget de grupo de items

        Args:
            group_name: Nombre del grupo
            group_type: Tipo de grupo ('category', 'list', 'tag')
            parent: Widget padre
        """
        super().__init__(parent)

        self.group_name = group_name
        self.group_type = group_type
        self.items = []

        self.init_ui()

    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header del grupo
        self.header = GroupHeaderWidget()
        self.header.set_group_info(self.group_name, self.group_type)
        self.header.create_list_clicked.connect(self.create_list_clicked.emit)
        self.main_layout.addWidget(self.header)

        # Si es lista, agregar barra de "Items" con botones
        if self.group_type == "list":
            self._add_items_toolbar()

        # Layout de items
        self.items_layout = QVBoxLayout()
        self.items_layout.setSpacing(0)
        self.main_layout.addLayout(self.items_layout)

    def _add_items_toolbar(self):
        """Agregar barra de herramientas de items (solo para listas)"""
        toolbar = QFrame()
        toolbar.setObjectName("itemsToolbar")
        toolbar.setStyleSheet("""
            QFrame#itemsToolbar {
                background-color: #252525;
                border-top: 1px solid #333;
                border-bottom: 1px solid #333;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(40, 8, 15, 8)
        toolbar_layout.setSpacing(10)

        # Label "Items"
        items_label = QLabel("📦 Items")
        items_label.setStyleSheet("""
            color: #ffffff;
            font-size: 10px;
            font-weight: bold;
        """)
        toolbar_layout.addWidget(items_label)

        toolbar_layout.addStretch()

        # Botón "+ Agregar Item"
        add_item_btn = QPushButton("+ Agregar Item")
        add_item_btn.setFixedHeight(28)
        add_item_btn.setMinimumWidth(110)
        add_item_btn.setToolTip("Agregar nuevo item a esta lista")
        add_item_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_item_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565C0;
                color: #ffffff;
                border: 1px solid #1976D2;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        add_item_btn.clicked.connect(self.add_item_clicked.emit)
        toolbar_layout.addWidget(add_item_btn)

        self.main_layout.addWidget(toolbar)

    def add_item(self, item_data: dict):
        """
        Agregar item al grupo

        Crea el widget apropiado según el tipo de item
        y lo agrega al layout de items.

        Args:
            item_data: Diccionario con datos del item
        """
        item_type = item_data.get('type', 'TEXT')

        # Crear widget según tipo
        if item_type == 'CODE':
            item_widget = CodeItemWidget(item_data)
        elif item_type == 'URL':
            item_widget = URLItemWidget(item_data)
        elif item_type == 'PATH':
            item_widget = PathItemWidget(item_data)
        elif item_type == 'WEB_STATIC':
            item_widget = WebStaticItemWidget(item_data)
        else:  # TEXT o por defecto
            item_widget = TextItemWidget(item_data)

        # Conectar señal de copiado
        item_widget.item_copied.connect(self.on_item_copied)

        self.items.append(item_widget)
        self.items_layout.addWidget(item_widget)

    def on_item_copied(self, item_data: dict):
        """
        Manejar evento de item copiado

        Args:
            item_data: Datos del item copiado
        """
        label = item_data.get('label', 'Sin título')
        print(f"✓ Item copiado del grupo '{self.group_name}': {label}")

    def clear_items(self):
        """Limpiar todos los items del grupo"""
        for item in self.items:
            item.deleteLater()
        self.items.clear()

    def get_item_count(self) -> int:
        """
        Obtener cantidad de items en el grupo

        Returns:
            Número de items
        """
        return len(self.items)

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
            Tipo del grupo
        """
        return self.group_type
