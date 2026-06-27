# config.py
import os
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/dispenser/.env"))

EQUIPO_ID   = "DISP-CENTRO-01"
APP_VERSION = "1.0.0"

DEBUG           = False
SIMULATION_MODE = True
MOBBEX_SANDBOX  = True

SCREEN_W = 1024
SCREEN_H = 600
PIN_PROPIETARIO = os.environ.get("PIN_PROPIETARIO", "1234")

VOLUMENES = [500, 800, 2000, 5000]

PRECIOS = {
    "jabon_verde": {500: 350,  800: 520,  2000: 1200, 5000: 2800},
    "jabon_azul":  {500: 350,  800: 520,  2000: 1200, 5000: 2800},
    "suavizante":  {500: 400,  800: 600,  2000: 1400, 5000: 3200},
    "limpiador":   {500: 300,  800: 450,  2000: 1000, 5000: 2300},
}

TIEMPO_ESPERA_PAGO = 300

MOBBEX_API_KEY      = os.environ.get("MOBBEX_API_KEY_TEST", "")
MOBBEX_ACCESS_TOKEN = os.environ.get("MOBBEX_ACCESS_TOKEN_TEST", "")

GPIO_BOMBA = {
    "jabon_verde": 22,
    "jabon_azul":  23,
    "suavizante":  24,
    "limpiador":   27,
}

GPIO_LED_QR      = 17
GPIO_LED_BOOT    = 18
GPIO_LED_PAGO    = 25
GPIO_BTN_REBOOT  = 4

PWM_FRECUENCIA_HZ = 100

PWM_DUTY_CYCLE = {
    "jabon_verde": 70,
    "jabon_azul":  70,
    "suavizante":  65,
    "limpiador":   25,
}

CAUDAL_CC_SEG = {
    "jabon_verde": 4.65,
    "jabon_azul":  4.70,
    "suavizante":  4.10,
    "limpiador":   12.50,
}

GPIO_SENSOR = {
    "jabon_verde": {"trig": 5,  "echo": 6},
    "jabon_azul":  {"trig": 13, "echo": 19},
    "suavizante":  {"trig": 26, "echo": 21},
    "limpiador":   {"trig": 20, "echo": 16},
}

NIVEL_CALIBRACION = {
    "jabon_verde": {"vacio": 38.5, "lleno": 5.0},
    "jabon_azul":  {"vacio": 38.5, "lleno": 5.0},
    "suavizante":  {"vacio": 38.5, "lleno": 5.0},
    "limpiador":   {"vacio": 42.0, "lleno": 6.0},
}

MONITOREO_INTERVALO_SEG = 300

ALERTAS_WHATSAPP_NUMERO = os.environ.get("ALERTAS_WHATSAPP_NUMERO", "")
ALERTAS_WHATSAPP_APIKEY = os.environ.get("ALERTAS_WHATSAPP_APIKEY", "")
ALERTAS_EMAIL_DESTINO   = os.environ.get("ALERTAS_EMAIL_DESTINO", "")
ALERTAS_EMAIL_REMITENTE = os.environ.get("ALERTAS_SMTP_USER", "")
ALERTAS_SMTP_HOST       = "smtp.gmail.com"
ALERTAS_SMTP_PORT       = 465
ALERTAS_SMTP_USER       = os.environ.get("ALERTAS_SMTP_USER", "")
ALERTAS_SMTP_PASSWORD   = os.environ.get("ALERTAS_SMTP_PASSWORD", "")
ALERTAS_COOLDOWN_SEG    = 3600
