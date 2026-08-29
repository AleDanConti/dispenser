# scripts/main_completo_real.py
"""
Prueba con Mercado Pago REAL (dinero real) + los 4 productos con
GpioHardware/HcSr04Sensors reales completos.
Correr: DISPLAY=:0 python3 scripts/main_completo_real.py
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from payments.mercadopago_provider import MercadoPagoPaymentProvider as PP
from hardware.gpio_hardware import GpioHardware as HW
from sensors.hc_sr04 import HcSr04Sensors as SS

hardware = HW()
sensores = SS(hardware=hardware, on_alerta=lambda a, n: log.warning(f"ALERTA: {a}"))
pagos = PP()

from ui.app import DispenserApp
app = DispenserApp()
app.iniciar_normal(pagos, hardware, sensores)
log.info("=== MERCADO PAGO REAL (dinero real) + los 4 productos ===")
app.mainloop()
