# scripts/main_prueba_completo.py
"""
Prueba de la UI completa con GpioHardware + HcSr04Sensors reales
(los 4 productos), pero pagos simulados (MockPaymentProvider).
No toca config.py ni main.py.
Correr: DISPLAY=:0 python3 scripts/main_prueba_completo.py
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from payments.mock_provider import MockPaymentProvider as PP
from hardware.gpio_hardware import GpioHardware as HW
from sensors.hc_sr04 import HcSr04Sensors as SS

hardware = HW()
sensores = SS(hardware=hardware, on_alerta=lambda a, n: log.warning(f"ALERTA: {a}"))
pagos = PP()

from ui.app import DispenserApp
app = DispenserApp()
app.iniciar_normal(pagos, hardware, sensores)
log.info("=== Prueba UI completa (GPIO + sensores reales x4, pagos mock) ===")
app.mainloop()
