"""
Widget de tags de items para el Creador Masivo

Componentes:
- Área de chips seleccionados con scroll
- Campo de búsqueda con autocompletado
- Lista desplegable de resultados
- Creación rápida de tags
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QLineEdit, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont
from src.views.widgets.project_tag_chip import ProjectTagChip
from src.core.global_tag_manager import GlobalTagManager
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ItemTagsSection(QWidget):
    """
    Sección de tags generales de items con selector tipo chips

    Permite seleccionar tags existentes mediante búsqueda en tiempo real,
    mostrarlos como chips removibles y crear nuevos tags al vuelo.

    Señales:
        tags_changed: Emitida cuando cambian los tags seleccionados (list[str])
        create_tag_clicked: Emitida cuando se hace clic en crear tag
    """

    # Señales
    tags_changed = pyqtSignal(list)  # list[str] nombres de tags
    create_tag_clicked = pyqtSignal()

    def __init__(self, tag_manager: GlobalTagManager = None, parent=None):
        """
        Inicializa la sección de tags de items

        Args:
            tag_manager: Manager de tags globales (opcional)
            parent: Widget padre
        """
        super().__init__(parent)
        self.tag_manager = tag_manager
        self.selected_tags: List = []  # Lista de ProjectElementTag
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)

        self._setup_ui()
        self._apply_styles()
        self._connect_signals()

    def _setup_ui(self):
        """Configura la interfaz del widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)

        # Título con botón crear
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title = QLabel("🏷️ Tags de Items")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header_layout.addWidget(title)

        # Info label
        info_label = QLabel("(Aplica a todos los items)")
        info_label.setStyleSheet("color: #888; font-size: 10px; font-style: italic;")
        header_layout.addWidget(info_label)

        header_layout.addStretch()

        self.create_btn = QPushButton("+")
        self.create_btn.setFixedSize(30, 30)
        self.create_btn.setToolTip("Crear nuevo tag")
        header_layout.addWidget(self.create_btn)

        layout.addLayout(header_layout)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #444;")
        layout.addWidget(separator)

        # Área de chips seleccionados
        self.chips_frame = QFrame()
        self.chips_frame.setMaximumHeight(100)
        self.chips_frame.setMinimumHeight(50)
        self.chips_layout = QHBoxLayout(self.chips_frame)
        self.chips_layout.setContentsMargins(8, 8, 8, 8)
        self.chips_layout.setSpacing(6)
        self.chips_layout.addStretch()

        # Scroll para chips
        chips_scroll = QScrollArea()
        chips_scroll.setWidget(self.chips_frame)
        chips_scroll.setWidgetResizable(True)
        chips_scroll.setMaximumHeight(110)
        chips_scroll.setMinimumHeight(60)
        chips_scroll.setFrameShape(QFrame.Shape.NoFrame)
        chips_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
            }
            QScrollBar:horizontal {
                background-color: #2d2d2d;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background-color: #555;
                border-radius: 4px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #666;
            }
        """)

        layout.addWidget(chips_scroll)

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar o crear tag...")
        self.search_input.setMinimumHeight(35)
        self.search_input.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.search_input)

        # Lista de resultados (oculta por defecto)
        self.results_list = QListWidget()
        self.results_list.setFont(QFont("Segoe UI", 9))
        self.results_list.setMaximumHeight(180)
        self.results_list.hide()
        layout.addWidget(self.results_list)

        # Label de ayuda cuando no hay tags seleccionados
        self.empty_label = QLabel("No hay tags seleccionados. Usa el campo de búsqueda para agregar.")
        self.empty_label.setStyleSheet("color: #888; font-style: italic; padding: 10px;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        layout.addWidget(self.empty_label)

    def _apply_styles(self):
        """Aplica estilos CSS al widget"""
        self.setStyleSheet("""
            QPushButton#create_btn {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton#create_btn:hover {
                background-color: #1976D2;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid #5dade2;
                background-color: #353535;
            }
            QLineEdit::placeholder {
                color: #888;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        self.create_btn.setObjectName("create_btn")

        self.chips_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
            }
        """)

        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #3498db;
            }
            QListWidget::item:selected {
                background-color: #2980b9;
            }
        """)

    def _connect_signals(self):
        """Conecta señales internas"""
        self.create_btn.clicked.connect(self.create_tag_clicked.emit)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._on_enter_pressed)
        self.results_list.itemClicked.connect(self._on_tag_selected)

    def _on_search_text_changed(self, text: str):
        """Maneja cambio en texto de búsqueda (con debounce)"""
        self._search_timer.stop()
        if text.strip():
            self._search_timer.start(300)  # 300ms debounce
        else:
            self.results_list.hide()

    def _perform_search(self):
        """Realiza la búsqueda de tags"""
        if not self.tag_manager:
            logger.warning("No hay tag_manager configurado para búsqueda")
            return

        query = self.search_input.text().strip()

        if not query:
            self.results_list.hide()
            return

        # Buscar tags
        results = self.tag_manager.search_tags(query)

        # Filtrar tags ya seleccionados
        selected_ids = [tag.id for tag in self.selected_tags]
        results = [tag for tag in results if tag.id not in selected_ids]

        # Mostrar resultados
        self.results_list.clear()

        if results:
            for tag in results[:10]:  # Máximo 10 resultados
                item = QListWidgetItem(f"{tag.name}")
                item.setData(Qt.ItemDataRole.UserRole, tag)
                self.results_list.addItem(item)
            self.results_list.show()
        else:
            # Opción para crear nuevo tag
            item = QListWidgetItem(f"✨ Crear tag: '{query}'")
            item.setData(Qt.ItemDataRole.UserRole, None)
            self.results_list.addItem(item)
            self.results_list.show()

    def _on_tag_selected(self, item: QListWidgetItem):
        """Maneja selección de tag de la lista"""
        tag = item.data(Qt.ItemDataRole.UserRole)

        if tag is None:
            # Crear nuevo tag
            if not self.tag_manager:
                logger.error("No hay tag_manager para crear tags")
                return

            query = self.search_input.text().strip()
            tag = self.tag_manager.create_tag(name=query, color="#3498db")

            if not tag:
                logger.error(f"No se pudo crear tag: {query}")
                return

        # Agregar tag a seleccionados
        if tag.id not in [t.id for t in self.selected_tags]:
            self.selected_tags.append(tag)
            self._add_chip(tag)
            self._update_empty_label()
            self._emit_tags_changed()

        # Limpiar búsqueda
        self.search_input.clear()
        self.results_list.hide()

    def _on_enter_pressed(self):
        """Maneja presión de Enter en búsqueda"""
        if self.results_list.count() > 0:
            # Seleccionar primer resultado
            first_item = self.results_list.item(0)
            self._on_tag_selected(first_item)

    def _add_chip(self, tag):
        """Agrega un chip de tag a la vista"""
        chip = ProjectTagChip(tag, removable=True)
        chip.tag_removed.connect(self._on_chip_removed)

        # Insertar antes del stretch
        self.chips_layout.insertWidget(self.chips_layout.count() - 1, chip)

        logger.debug(f"Chip agregado: {tag.name}")

    def _on_chip_removed(self, tag_id: int):
        """Maneja remoción de chip"""
        # Remover tag de seleccionados
        self.selected_tags = [t for t in self.selected_tags if t.id != tag_id]

        # Remover chip visual
        for i in range(self.chips_layout.count()):
            widget = self.chips_layout.itemAt(i).widget()
            if isinstance(widget, ProjectTagChip) and widget.tag.id == tag_id:
                widget.deleteLater()
                break

        self._update_empty_label()
        self._emit_tags_changed()

        logger.debug(f"Chip removido: tag_id={tag_id}")

    def _emit_tags_changed(self):
        """Emite señal de cambio de tags"""
        tag_names = [tag.name for tag in self.selected_tags]
        self.tags_changed.emit(tag_names)
        logger.debug(f"Tags seleccionados: {tag_names}")

    def _update_empty_label(self):
        """Actualiza visibilidad del label de ayuda"""
        has_tags = len(self.selected_tags) > 0
        self.empty_label.setVisible(not has_tags)

    # === API PÚBLICA ===

    def get_selected_tags(self) -> list[str]:
        """
        Obtiene los tags seleccionados

        Returns:
            Lista de nombres de tags seleccionados
        """
        return [tag.name for tag in self.selected_tags]

    def set_selected_tags(self, tag_names: list[str]):
        """
        Establece los tags seleccionados

        Args:
            tag_names: Lista de nombres de tags a seleccionar
        """
        if not self.tag_manager:
            logger.warning("No hay tag_manager configurado")
            return

        # Limpiar selección actual
        self.clear_selection()

        # Cargar tags
        for tag_name in tag_names:
            tag = self.tag_manager.get_tag_by_name(tag_name)
            if tag:
                self.selected_tags.append(tag)
                self._add_chip(tag)
            else:
                # Si el tag no existe, crearlo
                logger.info(f"Tag '{tag_name}' no existe, creándolo...")
                tag = self.tag_manager.create_tag(name=tag_name, color="#3498db")
                if tag:
                    self.selected_tags.append(tag)
                    self._add_chip(tag)

        self._update_empty_label()
        logger.info(f"Tags establecidos: {tag_names}")

    def clear_selection(self):
        """Limpia la selección de todos los tags"""
        self.selected_tags.clear()

        # Remover todos los chips
        while self.chips_layout.count() > 1:  # Dejar el stretch
            item = self.chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.search_input.clear()
        self.results_list.hide()
        self._update_empty_label()

        logger.debug("Selección limpiada")

    def add_tag(self, tag_name: str, select: bool = True):
        """
        Agrega un nuevo tag a la lista

        Args:
            tag_name: Nombre del tag
            select: Si seleccionarlo automáticamente (siempre True para este selector)
        """
        if not self.tag_manager:
            logger.warning("No hay tag_manager configurado")
            return

        # Verificar que no exista ya
        existing_names = [tag.name for tag in self.selected_tags]
        if tag_name in existing_names:
            logger.info(f"Tag '{tag_name}' ya está seleccionado")
            return

        # Buscar o crear el tag
        tag = self.tag_manager.get_tag_by_name(tag_name)
        if not tag:
            tag = self.tag_manager.create_tag(name=tag_name, color="#3498db")

        if tag:
            self.selected_tags.append(tag)
            self._add_chip(tag)
            self._update_empty_label()
            self._emit_tags_changed()
            logger.info(f"Tag '{tag_name}' agregado")

    def load_tags(self, tags: list[str]):
        """
        Método de compatibilidad con la versión anterior
        Carga tags disponibles (no hace nada en el nuevo selector)

        Args:
            tags: Lista de nombres de tags (ignorado)
        """
        # En el nuevo selector, los tags se cargan dinámicamente desde la BD
        # Este método existe solo para compatibilidad
        logger.debug("load_tags() llamado - ignorado en nuevo selector")
        pass

    def to_list(self) -> list[str]:
        """
        Exporta los tags seleccionados a lista

        Returns:
            Lista de tags seleccionados
        """
        return self.get_selected_tags()

    def from_list(self, tag_names: list[str]):
        """
        Importa tags seleccionados desde lista

        Args:
            tag_names: Lista de nombres de tags a seleccionar
        """
        self.set_selected_tags(tag_names)

    def set_tag_manager(self, tag_manager: GlobalTagManager):
        """
        Establece el tag manager

        Args:
            tag_manager: Manager de tags globales
        """
        self.tag_manager = tag_manager
        logger.info("Tag manager establecido")

    def __repr__(self) -> str:
        """Representación del widget"""
        selected = len(self.selected_tags)
        return f"ItemTagsSection(selected={selected})"
