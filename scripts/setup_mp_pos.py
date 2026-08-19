# scripts/setup_mp_pos.py
"""
Alta unica de Sucursal + Caja en Mercado Pago para este equipo.
Correr manualmente una vez por dispenser:
    python3 scripts/setup_mp_pos.py
Guarda los IDs resultantes en core/settings.json para que
mercadopago_provider.py los use en cada arranque.

Es idempotente: si la sucursal o la caja ya existen (por external_id),
las reutiliza en vez de crear duplicados.
"""
import sys
import os
sys.path.insert(0, os.path.expanduser("~/dispenser"))

import requests
import config
from core.settings import load_settings, save_settings

BASE = "https://api.mercadopago.com"
HEADERS = {
    "Authorization": f"Bearer {config.MP_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# external_id de la caja: solo alfanumerico, sin guiones
POS_EXTERNAL_ID = config.EQUIPO_ID.replace("-", "") + "POS"


def buscar_sucursal():
    resp = requests.get(
        f"{BASE}/users/{config.MP_USER_ID}/stores/search",
        headers=HEADERS,
        params={"external_id": config.EQUIPO_ID},
    )
    resp.raise_for_status()
    resultados = resp.json().get("results", [])
    return resultados[0] if resultados else None


def crear_sucursal():
    resp = requests.post(
        f"{BASE}/users/{config.MP_USER_ID}/stores",
        headers=HEADERS,
        json={
            "name": f"Sucursal {config.EQUIPO_ID}",
            "external_id": config.EQUIPO_ID,
            "location": {
                "street_number": "281",
                "street_name": "Colombres",
                "city_name": "Lomas de Zamora",
                "state_name": "Buenos Aires",
                "latitude": -34.7611823,
                "longitude": -58.4302476,
                "reference": config.EQUIPO_ID,
            },
        },
    )
    resp.raise_for_status()
    return resp.json()


def buscar_caja():
    resp = requests.get(
        f"{BASE}/pos",
        headers=HEADERS,
        params={"external_id": POS_EXTERNAL_ID},
    )
    resp.raise_for_status()
    resultados = resp.json().get("results", [])
    return resultados[0] if resultados else None


def crear_caja(store_id):
    resp = requests.post(
        f"{BASE}/pos",
        headers=HEADERS,
        json={
            "name": f"Caja {config.EQUIPO_ID}",
            "fixed_amount": False,   # False = monto variable por venta (QR dinamico)
            "store_id": store_id,
            "external_store_id": config.EQUIPO_ID,
            "external_id": POS_EXTERNAL_ID,
            "category": 621102,
        },
    )
    resp.raise_for_status()
    return resp.json()


def descargar_qr(url, destino):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    with open(destino, "wb") as f:
        f.write(resp.content)


def main():
    print(f"Dando de alta {config.EQUIPO_ID} en Mercado Pago...")

    sucursal = buscar_sucursal()
    if sucursal:
        store_id = sucursal["id"]
        print(f"Sucursal ya existia: store_id={store_id}")
    else:
        sucursal = crear_sucursal()
        store_id = sucursal["id"]
        print(f"Sucursal creada: store_id={store_id}")

    caja = buscar_caja()
    if caja:
        print(f"Caja ya existia: external_id={POS_EXTERNAL_ID}")
    else:
        caja = crear_caja(store_id)
        print(f"Caja creada: external_id={POS_EXTERNAL_ID}")

    qr_image_url = caja["qr"]["image"]
    qr_path = os.path.expanduser("~/dispenser/assets/qr_mp.png")
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    descargar_qr(qr_image_url, qr_path)
    print(f"QR fisico guardado en {qr_path}")

    data = load_settings()
    data["mp_store_id"] = store_id
    data["mp_external_pos_id"] = POS_EXTERNAL_ID
    data["mp_qr_path"] = qr_path
    save_settings(data)
    print("Setup completo. Los IDs quedaron guardados en core/settings.json")


if __name__ == "__main__":
    main()
