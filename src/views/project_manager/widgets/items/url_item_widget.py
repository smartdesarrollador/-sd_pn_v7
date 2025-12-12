"""
Widget para items de tipo URL

Muestra items de URL con formato de enlace clickeable.

Autor: Widget Sidebar Team
Versión: 1.0
"""

from PyQt6.QtWidgets import QLabel, QHBoxLayout, QTextEdit, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from .base_item_widget import BaseItemWidget
from ...styles.full_view_styles import FullViewStyles
import webbrowser


class URLItemWidget(BaseItemWidget):
    """
    Widget para items de tipo URL

    Características:
    - Muestra URL como enlace azul claro
    - Click en URL abre en navegador predeterminado
    - Icono 🔗 para identificación visual
    - Botón de copiar para copiar URL al portapapeles
    """

    def __init__(self, item_data: dict, parent=None):
        """
        Inicializar widget de item de URL

        Args:
            item_data: Diccionario con datos del item
            parent: Widget padre
        """
        super().__init__(item_data, parent)
        self.apply_styles()

    def render_content(self):
        """Renderizar contenido de URL"""
        # Layout horizontal para icono + título
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        # Icono de enlace
        icon_label = QLabel("🔗")
        icon_label.setStyleSheet("font-size: 16px;")
        title_layout.addWidget(icon_label)

        # Título
        label = self.get_item_label()
        if label and label != 'Sin título':
            title_label = QLabel(label)
            title_label.setStyleSheet("""
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            """)
            title_layout.addWidget(title_label)

        title_layout.addStretch()
        self.content_layout.addLayout(title_layout)

        # URL clickeable con scroll
        content = self.get_item_content()
        if content:
            url_text = QTextEdit()
            url_text.setObjectName("url_text")
            url_text.setPlainText(content)
            url_text.setReadOnly(True)
            url_text.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

            # Límite de altura máxima: 120px
            url_text.setMaximumHeight(120)

            # Establecer altura mínima para mejor visualización
            url_text.setMinimumHeight(40)

            # Política de tamaño: expandir horizontalmente, altura fija
            url_text.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )

            # Habilitar scrollbars según sea necesario
            url_text.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            url_text.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )

            # Deshabilitar word wrap para permitir scroll horizontal
            url_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

            url_text.mousePressEvent = lambda event: self.open_url(content)
            url_text.setToolTip("Click para abrir en navegador")

            url_text.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    border: none;
                    color: #5BA4E5;
                    font-size: 13px;
                    text-decoration: underline;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QTextEdit:hover {
                    color: #6BB6FF;
                }
                QScrollBar:vertical {
                    background-color: #2A2A2A;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background-color: #505050;
                    border-radius: 4px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #606060;
                }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
                QScrollBar:horizontal {
                    background-color: #2A2A2A;
                    height: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:horizontal {
                    background-color: #505050;
                    border-radius: 4px;
                    min-width: 20px;
                }
                QScrollBar::handle:horizontal:hover {
                    background-color: #606060;
                }
                QScrollBar::add-line:horizontal,
                QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                }
            """)

            self.content_layout.addWidget(url_text)

        # Descripción (si existe)
        description = self.get_item_description()
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                color: #808080;
                font-size: 12px;
                font-style: italic;
                padding-top: 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
            """)
            desc_label.setWordWrap(True)
            self.content_layout.addWidget(desc_label)

    def open_url(self, url: str):
        """
        Abrir URL en navegador predeterminado

        Args:
            url: URL a abrir
        """
        try:
            webbrowser.open(url)
            print(f"✓ URL abierta: {url}")
        except Exception as e:
            print(f"✗ Error al abrir URL: {e}")

    def apply_styles(self):
        """Aplicar estilos CSS"""
        self.setStyleSheet(FullViewStyles.get_url_item_style())
