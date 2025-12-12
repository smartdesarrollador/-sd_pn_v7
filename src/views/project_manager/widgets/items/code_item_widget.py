"""
Widget para items de tipo CODE

Muestra items de código con syntax highlighting.
Para contenido extenso (>800 chars) usa scroll vertical.

Autor: Widget Sidebar Team
Versión: 1.0
"""

from PyQt6.QtWidgets import QTextEdit, QLabel, QSizePolicy
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt, QRegularExpression
from .base_item_widget import BaseItemWidget
from ...styles.full_view_styles import FullViewStyles


class CodeSyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter simple para código

    Soporta highlighting básico para:
    - Keywords de programación
    - Strings
    - Comentarios
    - Comandos de terminal
    """

    def __init__(self, parent=None):
        """
        Inicializar syntax highlighter

        Args:
            parent: QTextDocument padre
        """
        super().__init__(parent)
        self.highlighting_rules = []

        # Formato para keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#FF79C6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        keywords = [
            "\\bfunction\\b", "\\bvar\\b", "\\blet\\b", "\\bconst\\b",
            "\\bif\\b", "\\belse\\b", "\\bfor\\b", "\\bwhile\\b",
            "\\breturn\\b", "\\bimport\\b", "\\bfrom\\b", "\\bdef\\b",
            "\\bclass\\b", "\\btry\\b", "\\bexcept\\b", "\\basync\\b",
            "\\bawait\\b", "\\bgit\\b", "\\bnpm\\b", "\\bpip\\b",
            "\\bpublic\\b", "\\bprivate\\b", "\\bstatic\\b", "\\bvoid\\b"
        ]

        for keyword in keywords:
            self.highlighting_rules.append((
                QRegularExpression(keyword),
                keyword_format
            ))

        # Formato para strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#F1FA8C"))
        self.highlighting_rules.append((
            QRegularExpression('"[^"]*"'),
            string_format
        ))
        self.highlighting_rules.append((
            QRegularExpression("'[^']*'"),
            string_format
        ))

        # Formato para comentarios
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6272A4"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            QRegularExpression("//[^\n]*"),
            comment_format
        ))
        self.highlighting_rules.append((
            QRegularExpression("#[^\n]*"),
            comment_format
        ))

        # Formato para comandos ($ al inicio)
        command_format = QTextCharFormat()
        command_format.setForeground(QColor("#7CFC00"))
        command_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            QRegularExpression("^\\$.*$"),
            command_format
        ))

    def highlightBlock(self, text):
        """
        Aplicar highlighting al bloque de texto

        Args:
            text: Texto del bloque a resaltar
        """
        for pattern, format_style in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    format_style
                )


class CodeItemWidget(BaseItemWidget):
    """
    Widget para items de tipo CODE

    Características:
    - Muestra código con syntax highlighting
    - Font monospace (Consolas, Courier New)
    - Para contenido corto (<800 chars): altura ajustada al contenido
    - Para contenido extenso (≥800 chars): scroll vertical
    - Altura máxima con scroll: 250px
    """

    MAX_CONTENT_LENGTH = 800  # Límite para mostrar contenido sin scroll

    def __init__(self, item_data: dict, parent=None):
        """
        Inicializar widget de item de código

        Args:
            item_data: Diccionario con datos del item
            parent: Widget padre
        """
        super().__init__(item_data, parent)
        self.apply_styles()

    def render_content(self):
        """Renderizar contenido de código"""
        # Título (si existe)
        label = self.get_item_label()
        if label and label != 'Sin título':
            title_label = QLabel(f"$ {label}")
            title_label.setStyleSheet("""
                color: #7CFC00;
                font-size: 13px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
                padding-bottom: 6px;
            """)
            self.content_layout.addWidget(title_label)

        # Editor de código
        content = self.get_item_content()
        if content:
            self.code_editor = QTextEdit()
            self.code_editor.setObjectName("code_content")
            self.code_editor.setPlainText(content)
            self.code_editor.setReadOnly(True)
            self.code_editor.setFrameStyle(0)

            # Límite de altura máxima: 300px
            self.code_editor.setMaximumHeight(300)

            # Establecer altura mínima para mejor visualización
            self.code_editor.setMinimumHeight(60)

            # Política de tamaño: expandir horizontalmente, altura fija
            self.code_editor.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed
            )

            # Habilitar scrollbars vertical y horizontal según sea necesario
            self.code_editor.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            self.code_editor.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )

            # Deshabilitar word wrap para permitir scroll horizontal
            self.code_editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

            # Aplicar syntax highlighting
            self.highlighter = CodeSyntaxHighlighter(
                self.code_editor.document()
            )

            self.content_layout.addWidget(self.code_editor)

    def apply_styles(self):
        """Aplicar estilos CSS"""
        self.setStyleSheet(FullViewStyles.get_code_item_style())
