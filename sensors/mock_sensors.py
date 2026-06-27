# sensors/mock_sensors.py
import logging
log = logging.getLogger(__name__)

class MockSensors:
    def __init__(self, hardware=None, on_alerta=None):
        self._niveles = {
            "jabon_verde": 75.0,
            "jabon_azul":  60.0,
            "suavizante":  45.0,
            "limpiador":   90.0,
        }
        self._on_alerta = on_alerta
        log.info("MockSensors inicializado")

    def leer_nivel(self, producto_id):
        return self._niveles.get(producto_id, 50.0)

    def leer_todos(self):
        return dict(self._niveles)

    def iniciar_monitoreo(self, intervalo_seg=300):
        log.info(f"[MOCK] Monitoreo simulado cada {intervalo_seg}s")
