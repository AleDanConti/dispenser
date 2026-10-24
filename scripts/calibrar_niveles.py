import sys, time, statistics
sys.path.insert(0, ".")
import config
from gpiozero import DistanceSensor

if len(sys.argv) != 2 or sys.argv[1] not in config.GPIO_SENSOR:
    raise SystemExit("Uso: python3 scripts/calibrar_niveles.py <" + "|".join(config.GPIO_SENSOR) + ">")
prod = sys.argv[1]
p = config.GPIO_SENSOR[prod]
s = DistanceSensor(echo=p["echo"], trigger=p["trig"], max_distance=1.0)

def punto(nombre):
    input(f"\nBidon {nombre}, quieto y sin espuma. Enter para medir... ")
    v = []
    for _ in range(20):
        v.append(s.distance * 100)
        time.sleep(0.3)
    med, dev = statistics.median(v), statistics.pstdev(v)
    print(f"{nombre}: mediana {med:.1f} cm | min {min(v):.1f} | max {max(v):.1f} | desvio {dev:.2f}")
    if max(v) - min(v) > 2:
        print("ATENCION: lecturas dispersas (posible eco de pared o espuma)")
    if max(v) >= 99:
        print("ATENCION: hubo lecturas sin eco (100 cm)")
    return med

vacio = punto("VACIO")
lleno = punto("LLENO (30 L)")
if lleno < 3:
    print("ATENCION: lleno a menos de 3 cm del sensor, zona poco confiable")
print("\nValores medidos:")
print(f"    producto={prod}  vacio={vacio:.1f}  lleno={lleno:.1f}")
s.close()
