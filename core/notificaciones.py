# core/notificaciones.py
import logging
import urllib.parse
import requests
from core.settings import load_settings
import config

log = logging.getLogger(__name__)


def enviar_whatsapp(mensaje):
    """Envía un mensaje de WhatsApp vía CallMeBot al número
    guardado en settings.json. Devuelve True/False según éxito."""
    settings = load_settings()
    numero = settings.get("alertas_whatsapp_numero")
    apikey = config.CALLMEBOT_APIKEY

    if not numero:
        log.warning("WhatsApp: no hay número configurado en settings")
        return False
    if not apikey:
        log.warning("WhatsApp: falta CALLMEBOT_APIKEY en .env")
        return False

    texto_codificado = urllib.parse.quote(mensaje)
    url = (f"https://api.callmebot.com/whatsapp.php"
           f"?phone={numero}&text={texto_codificado}&apikey={apikey}")

    try:
        resp = requests.get(url, timeout=10)
        log.info(f"WhatsApp enviado a {numero}: {resp.status_code} — {resp.text[:100]}")
        return resp.status_code == 200
    except Exception as e:
        log.error(f"Error enviando WhatsApp: {e}")
        return False


def notificar_compra(producto_nombre, volumen_cc, precio):
    """Notifica una compra aprobada — usado para probar el canal
    de WhatsApp sin depender de simular niveles bajos."""
    mensaje = (
        f"✅ Compra realizada\n"
        f"Producto: {producto_nombre}\n"
        f"Volumen: {volumen_cc} cc\n"
        f"Monto: $ {int(precio):,}".replace(",", ".")
    )
    enviado = enviar_whatsapp(mensaje)
    if enviado:
        log.info("Notificación de compra enviada por WhatsApp")
    else:
        log.warning("No se pudo enviar la notificación de compra")
    return enviado


def enviar_alertas(alertas, niveles_actuales=None):
    """Notificaciones de nivel bajo (Etapa 6) — pendiente de
    implementación completa de email, ya armado el canal WhatsApp."""
    for alerta in alertas:
        log.warning(f"ALERTA: {alerta}")
        enviar_whatsapp(f"⚠️ Alerta de nivel bajo: {alerta}")
