# scripts/probar_qr_consola.py
"""
Prueba de MercadoPagoPaymentProvider por consola, sin UI.
No toca el proceso principal ni la pantalla.
Correr: python3 scripts/probar_qr_consola.py
"""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/dispenser"))

from payments.mercadopago_provider import MercadoPagoPaymentProvider

pagos = MercadoPagoPaymentProvider()

orden = pagos.crear_orden(total=100, descripcion="Prueba consola")
print(f"\nOrden creada: {orden['orden_id']}")
print(f"QR guardado en: {orden['qr_path']}")
print(f"Expira en: {orden['expira_en']} segundos")
print("\nDescargá esa imagen a tu PC para escanearla con el celular")
print("(o abrila con: scp admin@192.168.0.7:" + orden['qr_path'] + " .)")
print("\nEsperando pago... (Ctrl+C para cancelar)\n")

try:
    while True:
        estado = pagos.consultar_estado(orden["orden_id"])
        print(f"Estado: {estado}")
        if estado in ("approved", "rejected"):
            break
        time.sleep(3)
except KeyboardInterrupt:
    print("\nCancelado manualmente, liberando orden...")
    pagos.cancelar_orden(orden["orden_id"])
    print("Listo.")
