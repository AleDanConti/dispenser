# scripts/probar_gpio.py
"""
Prueba aislada de GpioHardware: prende y apaga cada LED
por turno, 1 segundo cada uno, para confirmar el mapeo de pines.
No toca la UI ni el proceso principal.
Correr: python3 scripts/probar_gpio.py
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import logging
logging.basicConfig(level=logging.INFO)

from hardware.gpio_hardware import GpioHardware

hw = GpioHardware()

print("\n--- Probando LEDs de bombas (2 seg cada uno) ---")
for producto in ["jabon_verde", "jabon_azul", "suavizante", "limpiador"]:
    print(f"Encendiendo: {producto}")
    hw.encender_bomba(producto)
    time.sleep(2)
    hw.apagar_bomba(producto)
    time.sleep(0.5)

print("\n--- Probando LEDs de estado (1 seg cada uno) ---")
for nombre in ["qr", "pago"]:
    print(f"LED {nombre} ON")
    hw.set_led(nombre, True)
    time.sleep(1)
    hw.set_led(nombre, False)
    time.sleep(0.5)

print("\nLimpiando...")
hw.cleanup()
print("Prueba terminada.")
