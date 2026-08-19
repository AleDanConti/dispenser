# scripts/main_prueba_mp.py
"""
Version de main.py para probar la UI completa con Mercado Pago real
(sandbox), pero SIN tocar GPIO/sensores reales todavia.
No modifica config.py ni SIMULATION_MODE.
Correr: python3 scripts/main_prueba_mp.py
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

import config
from payments.mercadopago_provider import MercadoPagoPaymentProvider as PP
from hardware.mock_hardware import MockHardware as HW
from sensors.mock_sensors import MockSensors as SS

hardware = HW()
sensores = SS(hardware=hardware, on_alerta=lambda a, n: None)
pagos = PP()

from ui.app import DispenserApp
app = DispenserApp(payments=pagos, hardware=hardware, sensors=sensores)
log.info("=== Prueba UI + Mercado Pago real — entrando a mainloop ===")
app.mainloop()
