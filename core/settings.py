# core/settings.py
import json
import os

SETTINGS_PATH = os.path.expanduser("~/dispenser/core/settings.json")

DEFAULTS = {
    "umbrales_alerta": {
        "jabon_verde": 20,
        "jabon_azul":  20,
        "suavizante":  20,
        "limpiador":   20,
    },
    "precios": {
        "jabon_verde": {"500": 500,  "800": 750,  "2000": 1500, "5000": 3200},
        "jabon_azul":  {"500": 450,  "800": 700,  "2000": 1400, "5000": 3000},
        "suavizante":  {"500": 600,  "800": 900,  "2000": 1800, "5000": 4000},
        "limpiador":   {"500": 400,  "800": 600,  "2000": 1200, "5000": 2800},
    },
    "nombres_productos": {},
    "alertas_email": None,
    "alertas_whatsapp_numero": None,
}

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return dict(DEFAULTS)
    try:
        with open(SETTINGS_PATH, "r") as f:
            data = json.load(f)
        for k, v in DEFAULTS.items():
            if k not in data:
                data[k] = v
        if data.get("precios"):
            for prod, volumenes in DEFAULTS["precios"].items():
                if prod not in data["precios"]:
                    data["precios"][prod] = volumenes
                else:
                    for vol, precio in volumenes.items():
                        if vol not in data["precios"][prod]:
                            data["precios"][prod][vol] = precio
        else:
            data["precios"] = DEFAULTS["precios"]
        return data
    except Exception:
        return dict(DEFAULTS)

def save_settings(data):
    tmp = SETTINGS_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, SETTINGS_PATH)
