# sensors/hc_sr04.py
import threading
import time
import logging

from gpiozero import DistanceSensor

import config
from core.settings import load_settings

log = logging.getLogger(__name__)


class HcSr04Sensors:
    def __init__(self, hardware=None, on_alerta=None):
        self._on_alerta = on_alerta
        self._sensores = {}
        self._stop_event = threading.Event()
        self._hilo_monitoreo = None

        for producto, pines in config.GPIO_SENSOR.items():
            try:
                self._sensores[producto] = DistanceSensor(
                    echo=pines["echo"], trigger=pines["trig"],
                    max_distance=1.0)
                log.info("Sensor %s inicializado (trig=%s, echo=%s)",
                          producto, pines["trig"], pines["echo"])
            except Exception as e:
                log.error("No se pudo inicializar sensor %s: %s", producto, e)

        log.info("HcSr04Sensors inicializado (%d sensores)", len(self._sensores))

    def _distancia_cm(self, producto_id):
        sensor = self._sensores.get(producto_id)
        if sensor is None:
            raise ValueError(f"Sensor no configurado para {producto_id}")
        return sensor.distance * 100  # gpiozero da metros, convertimos a cm

    def leer_nivel(self, producto_id):
        cal = config.NIVEL_CALIBRACION.get(producto_id)
        if not cal:
            log.warning("Sin calibracion para %s, devuelvo 50%%", producto_id)
            return 50.0

        try:
            distancia = self._distancia_cm(producto_id)
        except Exception as e:
            log.error("Error leyendo sensor %s: %s", producto_id, e)
            return 50.0

        vacio, lleno = cal["vacio"], cal["lleno"]
        porcentaje = (vacio - distancia) / (vacio - lleno) * 100
        return max(0.0, min(100.0, porcentaje))

    def leer_todos(self):
        return {p: self.leer_nivel(p) for p in config.GPIO_SENSOR}

    def iniciar_monitoreo(self, intervalo_seg=300):
        if self._hilo_monitoreo is not None:
            log.warning("Monitoreo ya estaba iniciado")
            return
        self._stop_event.clear()
        self._hilo_monitoreo = threading.Thread(
            target=self._loop_monitoreo, args=(intervalo_seg,), daemon=True)
        self._hilo_monitoreo.start()
        log.info("Monitoreo de niveles iniciado (cada %ss)", intervalo_seg)

    def _loop_monitoreo(self, intervalo_seg):
        while not self._stop_event.is_set():
            try:
                niveles = self.leer_todos()
                settings = load_settings()
                umbrales = settings.get("umbrales_alerta", {})

                alertas = [
                    p for p, nivel in niveles.items()
                    if nivel <= umbrales.get(p, 0)
                ]
                if alertas and self._on_alerta:
                    log.warning("Niveles bajos detectados: %s", alertas)
                    self._on_alerta(alertas, niveles)
            except Exception:
                log.error("Error en loop de monitoreo", exc_info=True)

            self._stop_event.wait(intervalo_seg)

    def detener_monitoreo(self):
        self._stop_event.set()
        if self._hilo_monitoreo is not None:
            self._hilo_monitoreo.join(timeout=2)
            self._hilo_monitoreo = None
