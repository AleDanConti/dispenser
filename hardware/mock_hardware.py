# hardware/mock_hardware.py
import time
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
        try:
            t_real = self.calcular_tiempo_dispensado(producto_id, volumen_cc)
        except ValueError as e:
            log.error(f"dispensar: {e}")
            return False
        log.info(f"[MOCK] {volumen_cc}cc de {producto_id} (real={t_real:.1f}s, mock={self.MOCK_DISPENSE_SEG}s)")
        if not self.encender_bomba(producto_id):
            return False
        try:
            time.sleep(self.MOCK_DISPENSE_SEG)
        finally:
            self.apagar_bomba(producto_id)
            log.info(f"[MOCK] Dispensado de {producto_id} finalizado")
        return True

    def set_led(self, nombre, estado):
        log.debug(f"[MOCK] LED {nombre}: {'ON' if estado else 'OFF'}")

    def cleanup(self):
        self._bomba_activa = None
        log.info("[MOCK] Hardware cleanup")
