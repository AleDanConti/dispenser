# core/notificaciones.py
import logging
log = logging.getLogger(__name__)

def enviar_alertas(alertas, niveles_actuales=None):
    for alerta in alertas:
        log.warning(f"ALERTA: {alerta}")
