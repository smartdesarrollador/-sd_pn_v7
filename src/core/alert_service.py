"""
Alert Service - Servicio de background para gestión de alertas

Este servicio corre en background usando QTimer y revisa periódicamente
si hay alertas que deben dispararse.

Versión SIMPLIFICADA:
- QTimer cada 60 segundos (no QThread)
- Revisa alertas pendientes próximas (5 minutos adelante)
- Emite señal cuando hay alertas para disparar
- Marca alertas como 'triggered' después de disparar
- Registra en historial
"""

import logging
from typing import Dict, List
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)


class AlertService(QObject):
    """
    Servicio simple de alertas con QTimer

    Revisa cada 60 segundos si hay alertas pendientes que deben dispararse.
    Cuando encuentra una, emite la señal alert_triggered.
    """

    # Señal emitida cuando se dispara una alerta
    # Parámetros: (alerta: Dict, item: Dict)
    alert_triggered = pyqtSignal(dict, dict)

    def __init__(self, db_manager, check_interval: int = 60000):
        """
        Inicializar servicio de alertas

        Args:
            db_manager: Instancia de DBManager
            check_interval: Intervalo de chequeo en milisegundos (default: 60000 = 1 minuto)
        """
        super().__init__()
        self.db = db_manager
        self.check_interval = check_interval

        # QTimer para chequeos periódicos
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alerts)

        # Estado
        self.is_running = False
        self.alerts_checked = 0
        self.alerts_triggered = 0

        logger.info(f"AlertService inicializado (intervalo: {check_interval}ms)")

    def start(self):
        """Iniciar el servicio de alertas"""
        if not self.is_running:
            self.timer.start(self.check_interval)
            self.is_running = True
            logger.info("AlertService iniciado")

            # Chequear inmediatamente al iniciar
            self.check_alerts()
        else:
            logger.warning("AlertService ya está corriendo")

    def stop(self):
        """Detener el servicio de alertas"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
            logger.info(f"AlertService detenido (alertas revisadas: {self.alerts_checked}, disparadas: {self.alerts_triggered})")
        else:
            logger.warning("AlertService ya está detenido")

    def check_alerts(self):
        """
        Revisar alertas pendientes y disparar las que correspondan

        Este método se ejecuta periódicamente cada vez que el timer expira.
        Busca alertas activas cuya hora de disparo esté en los próximos 5 minutos.
        """
        try:
            self.alerts_checked += 1

            # Obtener alertas pendientes (próximos 5 minutos)
            pending_alerts = self.db.get_pending_alerts(minutes_ahead=5)

            if pending_alerts:
                logger.debug(f"Revisando {len(pending_alerts)} alertas pendientes")

                for alert in pending_alerts:
                    try:
                        # Obtener información del item
                        item = self.db.get_item(alert['item_id'])

                        if item:
                            # Emitir señal con la alerta y el item
                            logger.info(f"Disparando alerta ID={alert['id']}: {alert.get('alert_title', 'Sin título')}")
                            self.alert_triggered.emit(alert, item)

                            # Marcar alerta como triggered
                            self.db.update_item_alert(alert['id'], status='triggered')

                            # Registrar en historial
                            self.db.add_alert_history(
                                alert_id=alert['id'],
                                item_id=alert['item_id'],
                                user_action='triggered'
                            )

                            self.alerts_triggered += 1

                        else:
                            logger.warning(f"Item {alert['item_id']} no encontrado para alerta {alert['id']}")

                    except Exception as e:
                        logger.error(f"Error al procesar alerta {alert.get('id')}: {e}", exc_info=True)

            else:
                logger.debug("No hay alertas pendientes")

        except Exception as e:
            logger.error(f"Error en check_alerts: {e}", exc_info=True)

    def set_check_interval(self, interval_ms: int):
        """
        Cambiar el intervalo de chequeo

        Args:
            interval_ms: Nuevo intervalo en milisegundos
        """
        self.check_interval = interval_ms

        if self.is_running:
            self.timer.setInterval(interval_ms)
            logger.info(f"Intervalo de chequeo actualizado a {interval_ms}ms")

    def get_stats(self) -> Dict:
        """
        Obtener estadísticas del servicio

        Returns:
            Dict con estadísticas del servicio
        """
        return {
            'is_running': self.is_running,
            'check_interval_ms': self.check_interval,
            'alerts_checked': self.alerts_checked,
            'alerts_triggered': self.alerts_triggered
        }

    def force_check(self):
        """Forzar chequeo inmediato de alertas (útil para testing)"""
        logger.debug("Forzando chequeo de alertas...")
        self.check_alerts()
