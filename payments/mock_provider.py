# payments/mock_provider.py
import os
import qrcode
import logging
log = logging.getLogger(__name__)

class MockPaymentProvider:
    def __init__(self):
        self._contador = 0
        self._estados = {}
        log.info("MockPaymentProvider inicializado")

    def crear_orden(self, total, descripcion):
        self._contador += 1
        orden_id = f"MOCK-{self._contador:04d}"
        self._estados[orden_id] = "pending"

        # Generar QR con datos de prueba
        qr_dir = os.path.expanduser("~/dispenser/tmp")
        os.makedirs(qr_dir, exist_ok=True)
        qr_path = os.path.join(qr_dir, f"{orden_id}.png")

        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(f"MOCK|{orden_id}|{total}|{descripcion}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_path)

        log.info(f"[MOCK] Orden creada: {orden_id} por ${total}")

        # Auto-aprobar a los 10 segundos
        import threading
        def aprobar():
            import time
            time.sleep(10)
            self._estados[orden_id] = "approved"
            log.info(f"[MOCK] Orden {orden_id} auto-aprobada")
        threading.Thread(target=aprobar, daemon=True).start()

        return {
            "orden_id":  orden_id,
            "qr_path":   qr_path,
            "expira_en": 300,
        }

    def consultar_estado(self, orden_id):
        estado = self._estados.get(orden_id, "pending")
        log.debug(f"[MOCK] Estado {orden_id}: {estado}")
        return estado
