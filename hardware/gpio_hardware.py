# hardware/gpio_hardware.py
import time
import logging
import threading

from gpiozero import LED

import config

log = logging.getLogger(__name__)


class GpioHardware:
    def __init__(self):
        self._lock = threading.Lock()
        self._bomba_activa = None

        self._bombas = {
            producto: LED(pin)
            for producto, pin in config.GPIO_BOMBA.items()
        }

        self._leds = {
            "qr":   LED(config.GPIO_LED_QR),
            "boot": LED(config.GPIO_LED_BOOT),
            "pago": LED(config.GPIO_LED_PAGO),
        }

        self._leds["boot"].on()
        log.info("GpioHardware inicializado (bombas=%s, leds=%s)",
                  list(self._bombas.keys()), list(self._leds.keys()))

    def encender_bomba(self, producto_id):
        with self._lock:
            if self._bomba_activa:
                log.warning("Bomba %s activa, ignorando %s",
                            self._bomba_activa, producto_id)
                return False
            bomba = self._bombas.get(producto_id)
            if bomba is None:
                log.error("Bomba no configurada para %s", producto_id)
                return False
            self._bomba_activa = producto_id
            bomba.on()
            log.info("Bomba %s ON", producto_id)
            return True

    def apagar_bomba(self, producto_id):
        with self._lock:
            bomba = self._bombas.get(producto_id)
            if bomba is not None:
                bomba.off()
            self._bomba_activa = None
            log.info("Bomba %s OFF", producto_id)

    def calcular_tiempo_dispensado(self, producto_id, volumen_cc):
        caudal = config.CAUDAL_CC_SEG.get(producto_id)
        if not caudal or caudal <= 0:
            raise ValueError(f"Caudal no definido para {producto_id}")
        return volumen_cc / caudal

    def dispensar(self, producto_id, volumen_cc):
        return self.dispensar_controlable(
            producto_id, volumen_cc, threading.Event(), threading.Event())

    def dispensar_controlable(self, producto_id, volumen_cc,
                                evento_pausa, evento_cancelar, on_progreso=None):
        try:
            t_total = self.calcular_tiempo_dispensado(producto_id, volumen_cc)
        except ValueError as e:
            log.error("dispensar: %s", e)
            return False

        log.info("Dispensando %scc de %s (%.1fs)",
                  volumen_cc, producto_id, t_total)

        if not self.encender_bomba(producto_id):
            return False

        transcurrido = 0.0
        paso = 0.1
        pausado_ahora = False
        try:
            while transcurrido < t_total:
                if evento_cancelar.is_set():
                    log.info("Dispensado de %s CANCELADO en %.1fs de %.1fs",
                             producto_id, transcurrido, t_total)
                    return False

                if evento_pausa.is_set():
                    if not pausado_ahora:
                        bomba = self._bombas.get(producto_id)
                        if bomba is not None:
                            bomba.off()
                        pausado_ahora = True
                        log.info("Dispensado de %s PAUSADO en %.1fs",
                                 producto_id, transcurrido)
                    time.sleep(paso)
                    continue

                if pausado_ahora:
                    bomba = self._bombas.get(producto_id)
                    if bomba is not None:
                        bomba.on()
                    pausado_ahora = False
                    log.info("Dispensado de %s REANUDADO", producto_id)

                time.sleep(paso)
                transcurrido += paso
                if on_progreso:
                    on_progreso(min(transcurrido / t_total, 1.0))
        finally:
            self.apagar_bomba(producto_id)
            log.info("Dispensado de %s finalizado", producto_id)
        return True

    def set_led(self, nombre, estado):
        led = self._leds.get(nombre)
        if led is None:
            log.debug("LED desconocido: %s", nombre)
            return
        if estado:
            led.on()
        else:
            led.off()

    def cleanup(self):
        with self._lock:
            if self._bomba_activa:
                self.apagar_bomba(self._bomba_activa)
        for led in self._leds.values():
            led.off()
        for bomba in self._bombas.values():
            bomba.close()
        for led in self._leds.values():
            led.close()
        log.info("GpioHardware cleanup")
