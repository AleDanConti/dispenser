# payments/mercadopago_provider.py
import os
import time
import logging
import uuid
import qrcode
import requests

import config
from core.settings import load_settings

log = logging.getLogger(__name__)

BASE_URL = "https://api.mercadopago.com"


class MercadoPagoPaymentProvider:
    def __init__(self):
        settings = load_settings()
        self._external_pos_id = settings.get("mp_external_pos_id")

        if not self._external_pos_id:
            raise RuntimeError(
                "No hay mp_external_pos_id en settings.json. "
                "Correr scripts/setup_mp_pos.py antes de iniciar en modo real."
            )

        self._headers = {
            "Authorization": f"Bearer {config.MP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        self._qr_dir = os.path.expanduser("~/dispenser/tmp")
        os.makedirs(self._qr_dir, exist_ok=True)
        log.info("MercadoPagoPaymentProvider inicializado (pos=%s)",
                  self._external_pos_id)

    def _url_qrs(self):
        return (f"{BASE_URL}/instore/orders/qr/seller/collectors/"
                f"{config.MP_USER_ID}/pos/{self._external_pos_id}/qrs")

    def _url_orders(self):
        return (f"{BASE_URL}/instore/qr/seller/collectors/"
                f"{config.MP_USER_ID}/pos/{self._external_pos_id}/orders")

    def crear_orden(self, total, descripcion):
        orden_id = f"{config.EQUIPO_ID}-{uuid.uuid4().hex[:10]}"
        body = {
            "external_reference": orden_id,
            "title": "Dispenser Inteligente",
            "description": descripcion,
            "total_amount": float(total),
            "items": [{
                "sku_number": orden_id,
                "category": "services",
                "title": descripcion,
                "description": descripcion,
                "unit_price": float(total),
                "quantity": 1,
                "unit_measure": "unit",
                "total_amount": float(total),
            }],
        }

        resp = requests.put(self._url_qrs(), headers=self._headers,
                             json=body, timeout=15)
        if resp.status_code not in (200, 201):
            log.error("Error creando orden MP: %s %s",
                       resp.status_code, resp.text)
            raise RuntimeError(f"MP crear_orden fallo: {resp.status_code}")

        qr_data = resp.json()["qr_data"]

        # Generar la imagen del QR localmente, igual que el mock
        qr_path = os.path.join(self._qr_dir, f"{orden_id}.png")
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(qr_path)

        log.info("Orden MP creada: %s por $%s", orden_id, total)

        return {
            "orden_id":  orden_id,
            "qr_path":   qr_path,
            "expira_en": config.TIEMPO_ESPERA_PAGO_MP,
        }

    def consultar_estado(self, orden_id):
        try:
            resp = requests.get(
                f"{BASE_URL}/v1/payments/search",
                headers=self._headers,
                params={"external_reference": orden_id, "sort": "date_created",
                        "criteria": "desc"},
                timeout=10,
            )
            resp.raise_for_status()
            resultados = resp.json().get("results", [])
        except Exception as e:
            log.warning("Error consultando estado MP para %s: %s", orden_id, e)
            return "pending"

        if not resultados:
            return "pending"

        pago = resultados[0]
        estado_mp = pago.get("status")  # approved | rejected | in_process | cancelled

        if estado_mp == "approved":
            return "approved"
        if estado_mp in ("rejected", "cancelled"):
            return "rejected"
        return "pending"

    def cancelar_orden(self, orden_id=None):
        """Limpia la(s) orden(es) activa(s) de la caja. No falla el flujo
        si la llamada tiene algun problema: es un best-effort."""
        try:
            requests.delete(self._url_orders(), headers=self._headers, timeout=10)
        except Exception as e:
            log.debug("No se pudo liberar orden en MP (no bloqueante): %s", e)
