"""
Project Tag Filter Widget - Widget para filtrar elementos por tags

Widget estilo Dashboard con lista de checkboxes de tags para filtrar
elementos de proyecto en tiempo real.
"""

from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QScrollArea, QPushButton, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from src.core.project_element_tag_manager import ProjectElementTagManager


class TagCheckBox(QCheckBox):
    """
    Checkbox personalizado para tags con estilos dinámicos

    Esta clase garantiza que los estilos se apliquen correctamente
    cada vez que se crea o actualiza el checkbox.
    """

    def __init__(self, tag_name: str, tag_color: str, parent=None):
        super().__init__(tag_name, parent)
        self.tag_color = tag_color
        self.setFont(QFont("Segoe UI", 9))
        self._apply_styles()

        # Conectar señal de cambio de estado para forzar actualización visual
        self.stateChanged.connect(self._on_state_changed)

    def _apply_styles(self):
        """Aplica los estilos CSS al checkbox"""
        # Estilos mejorados con indicadores visuales MUY claros
        self.setStyleSheet(f"""
            QCheckBox {{
                color: #ecf0f1;
                spacing: 8px;
                padding: 8px 12px;
                border-radius: 4px;
                background-color: #2c3e50;
                border: 1px solid transparent;
                margin: 2px 0px;
            }}
            QCheckBox:checked {{
                background-color: {self.tag_color}60;
                border: 2px solid {self.tag_color};
                font-weight: bold;
                color: #ffffff;
            }}
            QCheckBox:hover {{
                background-color: {self.tag_color}30;
                border: 1px solid {self.tag_color}80;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {self.tag_color}80;
                border-radius: 4px;
                background-color: #1a1a1a;
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.tag_color};
                border: 3px solid {self.tag_color};
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #34495e;
                border: 2px solid {self.tag_color}40;
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.tag_color};
                border-width: 3px;
            }}
        """)

    def _on_state_changed(self, state):
        """Callback cuando cambia el estado - fuerza actualización visual"""
        # Forzar repaint para asegurar que los estilos se apliquen
        self.update()
        self.repaint()


class TagItemWidget(QWidget):
    """
    Widget contenedor para un tag con controles de reordenamiento
    """
    
    # Señales para reordenamiento
    move_up_requested = pyqtSignal(int)   # tag_id
    move_down_requested = pyqtSignal(int) # tag_id

    def __init__(self, tag_id: int, tag_name: str, tag_color: str, parent=None):
        super().__init__(parent)
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.tag_color = tag_color
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Checkbox (ocupa la mayor parte del espacio)
        self.checkbox = TagCheckBox(self.tag_name, self.tag_color)
        layout.addWidget(self.checkbox, 1)

        # Botones de reordenamiento (visibles solo al hacer hover sobre el widget, o siempre visibles)
        # Para simplificar, los haremos siempre visibles pero sutiles
        
        btn_style = """
            QPushButton {
                background-color: transparent;
                color: #95a5a6;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
                color: #ecf0f1;
            }
        """

        self.up_btn = QPushButton("▲")
        self.up_btn.setFixedSize(20, 20)
        self.up_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.up_btn.setToolTip("Mover arriba")
        self.up_btn.setStyleSheet(btn_style)
        self.up_btn.clicked.connect(lambda: self.move_up_requested.emit(self.tag_id))
        layout.addWidget(self.up_btn)

        self.down_btn = QPushButton("▼")
        self.down_btn.setFixedSize(20, 20)
        self.down_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.down_btn.setToolTip("Mover abajo")
        self.down_btn.setStyleSheet(btn_style)
        self.down_btn.clicked.connect(lambda: self.move_down_requested.emit(self.tag_id))
        layout.addWidget(self.down_btn)

    def isChecked(self):
        return self.checkbox.isChecked()

    def setChecked(self, checked):
        self.checkbox.setChecked(checked)


class ProjectTagFilterWidget(QWidget):
    """
    Widget para filtrar elementos por tags - Estilo Dashboard

    Muestra lista de tags disponibles con checkboxes para
    filtrar elementos del proyecto.
    """

    # Señales
    filter_changed = pyqtSignal(list, bool)  # tag_ids, match_all

    def __init__(self, tag_manager: ProjectElementTagManager, project_id: int = None, parent=None):
        """
        Inicializa el widget

        Args:
            tag_manager: Manager de tags
            project_id: ID del proyecto (None = mostrar todos los tags)
            parent: Widget padre
        """
        super().__init__(parent)
        self.tag_manager = tag_manager
        self.project_id = project_id
        self.tag_items = {}  # {tag_id: TagItemWidget}
        self.match_all = False  # False = OR logic, True = AND logic
        self._setup_ui()
        self._load_tags()

        # Conectar señal de cache invalidado para refrescar
        self.tag_manager.cache_invalidated.connect(self._on_cache_invalidated)

    def _setup_ui(self):
        """Configura la UI del widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(4)

        # Título
        title = QLabel("🏷️ Filtro por Tags")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #ecf0f1; background: transparent; border: none;")
        header_layout.addWidget(title)

        # Contador
        self.count_label = QLabel("(0 tags)")
        self.count_label.setFont(QFont("Segoe UI", 9))
        self.count_label.setStyleSheet("color: #95a5a6; background: transparent; border: none;")
        header_layout.addWidget(self.count_label)

        layout.addWidget(header_frame)

        # Área scrolleable de tags
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                border-radius: 6px;
            }
            QScrollBar:vertical {
                background-color: #2c3e50;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #7f8c8d;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #95a5a6;
            }
        """)

        # Container de checkboxes
        self.tags_container = QWidget()
        self.tags_layout = QVBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(8, 8, 8, 8)
        self.tags_layout.setSpacing(6)
        self.tags_layout.addStretch()

        scroll.setWidget(self.tags_container)
        layout.addWidget(scroll, 1)  # Expandir

        # Checkbox "Coincidir todos"
        self.match_all_checkbox = QCheckBox("Coincidir todos (AND)")
        self.match_all_checkbox.setFont(QFont("Segoe UI", 9))
        self.match_all_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ecf0f1;
                spacing: 8px;
                padding: 6px;
                background-color: #2c3e50;
                border-radius: 4px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #7f8c8d;
                border-radius: 3px;
                background-color: #34495e;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
            QCheckBox::indicator:hover {
                border-color: #5dade2;
            }
        """)
        self.match_all_checkbox.stateChanged.connect(self._on_match_all_changed)
        layout.addWidget(self.match_all_checkbox)

        # Botones de control
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.select_all_btn = QPushButton("✓ Todos")
        self.select_all_btn.setFont(QFont("Segoe UI", 9))
        self.select_all_btn.clicked.connect(self._select_all)
        buttons_layout.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton("✗ Ninguno")
        self.select_none_btn.setFont(QFont("Segoe UI", 9))
        self.select_none_btn.clicked.connect(self._select_none)
        buttons_layout.addWidget(self.select_none_btn)

        layout.addLayout(buttons_layout)

        self._apply_button_styles()

    def _apply_button_styles(self):
        """Aplica estilos a los botones"""
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """
        self.select_all_btn.setStyleSheet(button_style)
        self.select_none_btn.setStyleSheet(button_style)

    def _load_tags(self):
        """Carga los tags disponibles"""
        # Guardar estado actual de checkboxes antes de limpiar
        current_selected = self.get_selected_tag_ids()

        # Limpiar widgets existentes
        for item_widget in self.tag_items.values():
            item_widget.deleteLater()
        self.tag_items.clear()

        # Remover widgets del layout (excepto el stretch)
        while self.tags_layout.count() > 1:
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Obtener tags según el proyecto
        if self.project_id is not None:
            # Solo tags del proyecto específico (ya vienen ordenados)
            tags_sorted = self.tag_manager.get_tags_for_project(self.project_id)
        else:
            # Todos los tags
            tags = self.tag_manager.get_all_tags(refresh=True)
            tags_sorted = self.tag_manager.get_tags_sorted()

        # Actualizar contador
        self.count_label.setText(f"({len(tags_sorted)} tags)")

        # Crear widgets usando TagItemWidget
        self.current_tags_order = [] # Lista de IDs en orden actual
        
        for tag in tags_sorted:
            self.current_tags_order.append(tag.id)
            
            # Usar TagItemWidget que incluye botones de reordenamiento
            item_widget = TagItemWidget(tag.id, tag.name, tag.color, parent=self.tags_container)

            # Restaurar estado si estaba seleccionado antes
            if tag.id in current_selected:
                item_widget.setChecked(True)

            # Conectar señal de checkbox
            item_widget.checkbox.stateChanged.connect(self._on_filter_changed)
            
            # Conectar señales de reordenamiento (solo si hay proyecto seleccionado)
            if self.project_id is not None:
                item_widget.move_up_requested.connect(self._move_tag_up)
                item_widget.move_down_requested.connect(self._move_tag_down)
                item_widget.up_btn.setVisible(True)
                item_widget.down_btn.setVisible(True)
            else:
                item_widget.up_btn.setVisible(False)
                item_widget.down_btn.setVisible(False)

            # Guardar referencia
            self.tag_items[tag.id] = item_widget

            # Insertar antes del stretch
            self.tags_layout.insertWidget(self.tags_layout.count() - 1, item_widget)

        # Forzar actualización del layout
        self.tags_container.updateGeometry()
        self.tags_container.update()

    def _move_tag_up(self, tag_id: int):
        """Mueve un tag hacia arriba"""
        if self.project_id is None or tag_id not in self.current_tags_order:
            return
            
        idx = self.current_tags_order.index(tag_id)
        if idx > 0:
            # Swap en la lista local
            self.current_tags_order[idx], self.current_tags_order[idx-1] = \
                self.current_tags_order[idx-1], self.current_tags_order[idx]
            
            # Guardar nuevo orden
            self.tag_manager.set_project_tags_order(self.project_id, self.current_tags_order)
            
            # Recargar UI
            self._load_tags()

    def _move_tag_down(self, tag_id: int):
        """Mueve un tag hacia abajo"""
        if self.project_id is None or tag_id not in self.current_tags_order:
            return
            
        idx = self.current_tags_order.index(tag_id)
        if idx < len(self.current_tags_order) - 1:
            # Swap en la lista local
            self.current_tags_order[idx], self.current_tags_order[idx+1] = \
                self.current_tags_order[idx+1], self.current_tags_order[idx]
            
            # Guardar nuevo orden
            self.tag_manager.set_project_tags_order(self.project_id, self.current_tags_order)
            
            # Recargar UI
            self._load_tags()

    def _on_filter_changed(self):
        """Maneja cambio en filtros"""
        selected_tag_ids = self.get_selected_tag_ids()
        self.filter_changed.emit(selected_tag_ids, self.match_all)

    def _on_match_all_changed(self, state):
        """Maneja cambio en checkbox de match_all"""
        self.match_all = state == Qt.CheckState.Checked.value
        self._on_filter_changed()

    def _on_cache_invalidated(self):
        """Callback cuando se invalida el caché del tag manager"""
        # Recargar tags manteniendo selección actual
        self._load_tags()

    def _select_all(self):
        """Selecciona todos los tags"""
        # Bloquear señales temporalmente para evitar múltiples emisiones
        for item_widget in self.tag_items.values():
            item_widget.checkbox.blockSignals(True)
            item_widget.setChecked(True)
            item_widget.checkbox.blockSignals(False)

        # Emitir señal una sola vez
        self._on_filter_changed()

    def _select_none(self):
        """Deselecciona todos los tags"""
        # Bloquear señales temporalmente para evitar múltiples emisiones
        for item_widget in self.tag_items.values():
            item_widget.checkbox.blockSignals(True)
            item_widget.setChecked(False)
            item_widget.checkbox.blockSignals(False)

        # Emitir señal una sola vez
        self._on_filter_changed()

    def get_selected_tag_ids(self) -> List[int]:
        """
        Obtiene los IDs de tags seleccionados

        Returns:
            Lista de IDs de tags seleccionados
        """
        return [
            tag_id for tag_id, item_widget in self.tag_items.items()
            if item_widget.isChecked()
        ]

    def set_selected_tag_ids(self, tag_ids: List[int]):
        """
        Establece los tags seleccionados

        Args:
            tag_ids: Lista de IDs de tags a seleccionar
        """
        for tag_id, item_widget in self.tag_items.items():
            item_widget.checkbox.blockSignals(True)
            item_widget.setChecked(tag_id in tag_ids)
            item_widget.checkbox.blockSignals(False)

        # Emitir señal una vez al final
        self._on_filter_changed()

    def clear_filters(self):
        """Limpia todos los filtros"""
        self._select_none()
        self.match_all_checkbox.setChecked(False)

    def refresh(self):
        """Refresca la lista de tags manteniendo selección"""
        self._load_tags()

    def set_project(self, project_id: int = None):
        """
        Cambia el proyecto y recarga los tags

        Args:
            project_id: ID del proyecto a mostrar (None = limpiar filtro)
        """
        self.project_id = project_id

        # NO limpiar filtros aquí - mantener selección del usuario
        # Solo recargar la lista de tags
        self._load_tags()
