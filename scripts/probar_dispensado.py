# scripts/probar_dispensado.py
"""
Prueba de dispensar() con tiempo real cronometrado.
Uso: python3 scripts/probar_dispensado.py <producto> <ml>
Ejemplo: python3 scripts/probar_dispensado.py jabon_verde 500
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import logging
logging.basicConfig(level=logging.INFO)

from hardware.gpio_hardware import GpioHardware

if len(sys.argv) != 3:
    print("Uso: python3 scripts/probar_dispensado.py <producto> <ml>")
    sys.exit(1)

producto = sys.argv[1]
ml = float(sys.argv[2])

hw = GpioHardware()

esperado = hw.calcular_tiempo_dispensado(producto, ml)
print(f"\nProducto: {producto} | Cantidad: {ml} ml")
print(f"Tiempo esperado: {esperado:.1f} seg\n")

inicio = time.time()
hw.dispensar(producto, ml)
real = time.time() - inicio

print(f"\nTiempo real cronometrado: {real:.1f} seg")
print(f"Diferencia: {real - esperado:.2f} seg")

hw.cleanup()
