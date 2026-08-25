# scripts/probar_sensor.py
"""
Prueba aislada de un sensor HC-SR04 individual.
Uso: python3 scripts/probar_sensor.py <producto>
Ejemplo: python3 scripts/probar_sensor.py jabon_verde
Lee distancia y nivel cada 1 segundo, 15 veces. Ctrl+C para cortar antes.
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import logging
logging.basicConfig(level=logging.INFO)

if len(sys.argv) != 2:
    print("Uso: python3 scripts/probar_sensor.py <producto>")
    sys.exit(1)

producto = sys.argv[1]

from sensors.hc_sr04 import HcSr04Sensors

sensores = HcSr04Sensors()

if producto not in sensores._sensores:
    print(f"Sensor '{producto}' no disponible. Sensores inicializados: {list(sensores._sensores.keys())}")
    sys.exit(1)

print(f"\nLeyendo sensor de {producto} (Ctrl+C para cortar)...\n")
try:
    for i in range(15):
        dist = sensores._distancia_cm(producto)
        nivel = sensores.leer_nivel(producto)
        print(f"[{i+1:2d}] Distancia: {dist:5.1f} cm  |  Nivel: {nivel:5.1f} %")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nCortado por el usuario.")
