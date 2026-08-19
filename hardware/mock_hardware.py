# hardware/mock_hardware.py
import time
import threading
import logging
log = logging.getLogger(__name__)

class MockHardware:
    MOCK_DISPENSE_SEG = 2

    def __init__(self):
        self._bomba_activa = None
        log.info("MockHardware inicializado")

    def encender_bomba(self, producto_id):
        if self._bomba_activa:
            log.warning(f"Bomba {self._bomba_activa} activa, ignorando {producto_id}")
            return False
        self._bomba_activa = producto_id
        log.info(f"[MOCK] Bomba {producto_id} ON")
        return True

    def apagar_bomba(self, producto_id):
        self._bomba_activa = None
        log.info(f"[MOCK] Bomba {producto_id} OFF")

    def calcular_tiempo_dispensado(self, producto_id, volumen_cc):
        import config
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
            log.error(f"dispensar: {e}")
            return False

        t_total_mock = min(t_total, self.MOCK_DISPENSE_SEG)
        log.info(f"[MOCK] {volumen_cc}cc de {producto_id} (real={t_total:.1f}s, mock={t_total_mock:.1f}s)")

        if not self.encender_bomba(producto_id):
            return False

        transcurrido = 0.0
        paso = 0.1
        try:
            while transcurrido < t_total_mock:
                if evento_cancelar.is_set():
                    log.info(f"[MOCK] Dispensado de {producto_id} CANCELADO")
                    return False
                if evento_pausa.is_set():
                    time.sleep(paso)
                    continue
                time.sleep(paso)
                transcurrido += paso
                if on_progreso:
                    on_progreso(min(transcurrido / t_total_mock, 1.0))
        finally:
            self.apagar_bomba(producto_id)
            log.info(f"[MOCK] Dispensado de {producto_id} finalizado")
        return True

    def set_led(self, nombre, estado):
        log.debug(f"[MOCK] LED {nombre}: {'ON' if estado else 'OFF'}")

    def cleanup(self):
        self._bomba_activa = None
        log.info("[MOCK] Hardware cleanup")
