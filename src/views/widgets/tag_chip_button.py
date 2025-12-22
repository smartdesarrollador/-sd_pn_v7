"""
Widget de botón chip para representar un tag filtrable

Componente visual clickeable que representa un tag con dos estados:
- Normal (gris): Tag no seleccionado
- Activo (verde): Tag seleccionado para filtrar

SOLO LECTURA: No permite editar ni eliminar tags.

Versión: 1.0
Fecha: 2025-12-21
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class TagChipButton(QPushButton):
    """
    Botón con estilo de chip para representar un tag filtrable

    Estados:
    - Normal: Borde gris, fondo oscuro
    - Activo: Borde verde, fondo verde oscuro
    - Hover: Borde más claro

    Señales:
        toggled(bool): Emitida cuando cambia el estado activo/inactivo
    """

    # Señal personalizada (además de la nativa toggled de QPushButton)
    state_changed = pyqtSignal(bool)  # True = activo, False = inactivo

    def __init__(self, tag_name: str, tag_color: str = "#808080", parent=None):
        """
        Inicializa el chip button

        Args:
            tag_name: Nombre del tag a mostrar
            tag_color: Color del tag (opcional, por defecto gris)
            parent: Widget padre
        """
        super().__init__(tag_name, parent)

        self.tag_name = tag_name
        self.tag_color = tag_color
        self._is_active = False  # Estado de selección

        # Configurar como checkable para toggle
        self.setCheckable(True)
        self.setChecked(False)

        # Configurar apariencia
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 9))
        self.setFixedHeight(26)
        self.setMinimumWidth(60)

        # Aplicar estilos iniciales
        self._apply_styles()

        # Conectar señal nativa toggled a handler personalizado
        self.toggled.connect(self._on_toggled)

        logger.debug(f"TagChipButton creado: {tag_name}")

    def _on_toggled(self, checked: bool):
        """
        Handler cuando el botón cambia de estado

        Args:
            checked: True si está checked, False si no
        """
        self._is_active = checked
        self._apply_styles()
        self.state_changed.emit(checked)
        logger.debug(f"Tag '{self.tag_name}' {'activado' if checked else 'desactivado'}")

    def _apply_styles(self):
        """Aplica estilos CSS según el estado"""
        if self._is_active:
            # Estilo activo (verde)
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1a4d2e;
                    color: #00ff88;
                    border: 1px solid #00ff88;
                    border-radius: 13px;
                    padding: 4px 12px;
                    font-size: 9px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #2a5d3e;
                    border-color: #7CFC00;
                }}
                QPushButton:pressed {{
                    background-color: #0a3d1e;
                }}
            """)
        else:
            # Estilo normal (gris)
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #666;
                    border-radius: 13px;
                    padding: 4px 12px;
                    font-size: 9px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: #4d4d4d;
                    border-color: #999;
                }}
                QPushButton:pressed {{
                    background-color: #2d2d2d;
                }}
            """)

    def set_active(self, active: bool):
        """
        Establecer estado activo del chip

        Args:
            active: True para activar, False para desactivar
        """
        self.setChecked(active)
        # _on_toggled se llamará automáticamente

    def is_active(self) -> bool:
        """
        Verificar si el chip está activo

        Returns:
            bool: True si está activo, False si no
        """
        return self._is_active

    def get_tag_name(self) -> str:
        """
        Obtener nombre del tag

        Returns:
            str: Nombre del tag
        """
        return self.tag_name


# === TEST ===
if __name__ == '__main__':
    """Test independiente del chip button"""
    import sys
    from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout

    app = QApplication(sys.argv)

    # Crear ventana de test
    window = QWidget()
    window.setWindowTitle("Test TagChipButton")
    window.setStyleSheet("background-color: #1e1e1e;")
    layout = QHBoxLayout(window)

    # Crear varios chips de ejemplo
    tags = ["python", "backend", "api", "database", "async"]

    for tag in tags:
        chip = TagChipButton(tag)
        chip.state_changed.connect(
            lambda active, t=tag: print(f"✓ Tag '{t}': {'ACTIVO' if active else 'inactivo'}")
        )
        layout.addWidget(chip)

    layout.addStretch()

    window.resize(500, 100)
    window.show()

    sys.exit(app.exec())
