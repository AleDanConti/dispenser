# core/reintentos.py
import time
import logging
log = logging.getLogger(__name__)

def con_reintentos(fn, intentos=3, espera=2):
    for i in range(intentos):
        try:
            return fn()
        except Exception as e:
            log.warning(f"Intento {i+1}/{intentos} fallido: {e}")
            if i < intentos - 1:
                time.sleep(espera)
    raise Exception(f"Fallaron {intentos} intentos")
