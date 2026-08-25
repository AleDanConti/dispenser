# scripts/main_prueba_jv.py
"""
Prueba de la UI completa con SOLO jabon_verde real (bomba + sensor),
los otros 3 productos deshabilitados para no arriesgar el arranque
por hardware sin cablear todavia. Pagos simulados (mock).
Correr: DISPLAY=:0 python3 scripts/main_prueba_jv.py
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

import config
from gpiozero import LED, DistanceSensor

from payments.mock_provider import MockPaymentProvider as PP


class HardwareSoloJV:
    """Version reducida de GpioHardware: solo controla jabon_verde,
    ignora los otros 3 productos (todavia sin cablear)."""
    def __init__(self):
        self._bomba = LED(config.GPIO_BOMBA["jabon_verde"])
        self._leds = {
            "qr":   LED(config.GPIO_LED_QR),
            "boot": LED(config.GPIO_LED_BOOT),
            "pago": LED(config.GPIO_LED_PAGO),
        }
        self._leds["boot"].on()
        self._bomba_activa = None
        log.info("HardwareSoloJV inicializado")

    def encender_bomba(self, producto_id):
        if producto_id != "jabon_verde":
            log.warning("Producto %s no disponible en esta prueba", producto_id)
            return False
        if self._bomba_activa:
            return False
        self._bomba_activa = producto_id
        self._bomba.on()
        log.info("Bomba jabon_verde ON")
        return True

    def apagar_bomba(self, producto_id):
        self._bomba.off()
        self._bomba_activa = None
        log.info("Bomba jabon_verde OFF")

    def calcular_tiempo_dispensado(self, producto_id, volumen_cc):
        caudal = config.CAUDAL_CC_SEG.get(producto_id)
        return volumen_cc / caudal

    def dispensar(self, producto_id, volumen_cc):
        return self.dispensar_controlable(
            producto_id, volumen_cc, __import__("threading").Event(),
            __import__("threading").Event())

    def dispensar_controlable(self, producto_id, volumen_cc,
                                evento_pausa, evento_cancelar, on_progreso=None):
        import time
        if producto_id != "jabon_verde":
            log.warning("Producto %s no disponible, simulando OK", producto_id)
            return True
        t_total = self.calcular_tiempo_dispensado(producto_id, volumen_cc)
        if not self.encender_bomba(producto_id):
            return False
        transcurrido = 0.0
        paso = 0.1
        pausado_ahora = False
        try:
            while transcurrido < t_total:
                if evento_cancelar.is_set():
                    return False
                if evento_pausa.is_set():
                    if not pausado_ahora:
                        self._bomba.off()
                        pausado_ahora = True
                        log.info("Bomba jabon_verde PAUSADA")
                    time.sleep(paso)
                    continue
                if pausado_ahora:
                    self._bomba.on()
                    pausado_ahora = False
                    log.info("Bomba jabon_verde REANUDADA")
                time.sleep(paso)
                transcurrido += paso
                if on_progreso:
                    on_progreso(min(transcurrido / t_total, 1.0))
        finally:
            self.apagar_bomba(producto_id)
        return True

    def set_led(self, nombre, estado):
        led = self._leds.get(nombre)
        if led is None:
            return
        led.on() if estado else led.off()

    def cleanup(self):
        self._bomba.off()
        for led in self._leds.values():
            led.off()


class SensoresSoloJV:
    """Version reducida: solo lee jabon_verde, el resto devuelve
    un valor fijo sin tocar hardware sin cablear."""
    def __init__(self, hardware=None, on_alerta=None):
        pines = config.GPIO_SENSOR["jabon_verde"]
        self._sensor_jv = DistanceSensor(
            echo=pines["echo"], trigger=pines["trig"], max_distance=1.0)
        log.info("SensoresSoloJV inicializado")

    def leer_nivel(self, producto_id):
        if producto_id != "jabon_verde":
            return 50.0
        cal = config.NIVEL_CALIBRACION["jabon_verde"]
        distancia = self._sensor_jv.distance * 100
        pct = (cal["vacio"] - distancia) / (cal["vacio"] - cal["lleno"]) * 100
        return max(0.0, min(100.0, pct))

    def leer_todos(self):
        return {"jabon_verde": self.leer_nivel("jabon_verde")}

    def iniciar_monitoreo(self, intervalo_seg=300):
        log.info("Monitoreo no iniciado en esta prueba reducida")


hardware = HardwareSoloJV()
sensores = SensoresSoloJV()
pagos = PP()

from ui.app import DispenserApp
app = DispenserApp()
app.iniciar_normal(pagos, hardware, sensores)
log.info("=== Prueba SOLO jabon_verde (bomba + sensor reales, pagos mock) ===")
app.mainloop()
