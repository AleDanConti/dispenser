import sys, subprocess, time
sys.path.insert(0, ".")
if subprocess.run(["pgrep", "-f", "python3 main.py"], capture_output=True).stdout.strip():
    raise SystemExit("La app esta corriendo y tiene los pines GPIO. Detenela (pkill -f 'python3 main.py') y volve a correr.")
from sensors.hc_sr04 import HcSr04Sensors
ss = HcSr04Sensors()
time.sleep(0.5)
for p in ss._sensores:
    d = ss._distancia_cm(p)
    print(f"{p:12s}: distancia {d:5.1f} cm | nivel {ss.leer_nivel(p):5.1f} %")
