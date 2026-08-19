# scripts/main_prueba_gpio.py
"""
Prueba de la UI completa con GpioHardware real (bombas/LEDs)
pero pagos simulados (MockPaymentProvider), para no depender
de Mercado Pago en esta prueba. No toca config.py ni main.py.
Correr: DISPLAY=:0 python3 scripts/main_prueba_gpio.py
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from payments.mock_provider import MockPaymentProvider as PP
from hardware.gpio_hardware import GpioHardware as HW
from sensors.mock_sensors import MockSensors as SS

hardware = HW()
sensores = SS(hardware=hardware, on_alerta=lambda a, n: None)
pagos = PP()

from ui.app import DispenserApp
app = DispenserApp(payments=pagos, hardware=hardware, sensors=sensores)
log.info("=== Prueba UI + GPIO real (pagos mock) — entrando a mainloop ===")
app.mainloop()
