# main.py
import logging
import sys
import os
import atexit
import signal
import threading
import time
import traceback
from logging.handlers import RotatingFileHandler

import config

# Logs rotativos: max 5 archivos de 5MB cada uno
log_path = os.path.expanduser("~/dispenser/app.log")
file_handler = RotatingFileHandler(
    log_path, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s: %(message)s"))

logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    handlers=[file_handler, logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("main")


def excepthook_global(exc_type, exc_value, exc_tb):
    log.critical(
        "Excepcion no capturada:\n%s",
        "".join(traceback.format_exception(
            exc_type, exc_value, exc_tb)))

sys.excepthook = excepthook_global


def excepthook_hilos(args):
    log.critical(
        "Excepcion no capturada en hilo '%s':\n%s",
        args.thread.name,
        "".join(traceback.format_exception(
            args.exc_type, args.exc_value,
            args.exc_traceback)))

threading.excepthook = excepthook_hilos

_hardware_global = {"hw": None}


def cerrar(hardware=None):
    log.info("Cerrando aplicacion...")
    hw = hardware or _hardware_global["hw"]
    if hw:
        hw.cleanup()
    sys.exit(0)


def manejar_alertas(alertas, niveles_actuales=None):
    from core.notificaciones import enviar_alertas
    enviar_alertas(alertas, niveles_actuales)


def _log_splash(app, texto, tipo="info"):
    log.info(texto)
    app.after(0, lambda: app.splash.agregar_linea(texto, tipo))


def _inicializar_en_hilo(app):
    """Corre en un hilo aparte: arma hardware/sensores/pagos y va
    empujando cada paso a la consola del splash en pantalla."""
    try:
        app.after(0, lambda: app.splash.set_estado("Iniciando sistema..."))
        _log_splash(app, f"Equipo: {config.EQUIPO_ID}  v{config.APP_VERSION}")
        time.sleep(0.3)

        if config.SIMULATION_MODE:
            _log_splash(app, "SIMULATION_MODE activo — usando mocks", "warn")
            from payments.mock_provider import MockPaymentProvider as PP
            from hardware.mock_hardware import MockHardware as HW
            from sensors.mock_sensors   import MockSensors as SS
        else:
            from payments.mercadopago_provider import MercadoPagoPaymentProvider as PP
            from hardware.gpio_hardware   import GpioHardware as HW
            from sensors.hc_sr04          import HcSr04Sensors as SS

        _log_splash(app, "Inicializando hardware (GPIO)...")
        hardware = HW()
        _hardware_global["hw"] = hardware
        _log_splash(app, "Hardware OK", "ok")
        time.sleep(0.2)

        _log_splash(app, "Inicializando sensores...")
        sensores = SS(
            hardware=hardware,
            on_alerta=lambda a, n: manejar_alertas(a, n))
        if not config.SIMULATION_MODE:
            sensores.iniciar_monitoreo(config.MONITOREO_INTERVALO_SEG)
        _log_splash(app, "Sensores OK", "ok")
        time.sleep(0.2)

        _log_splash(app, "Conectando proveedor de pagos...")
        pagos = PP()
        _log_splash(app, "Pagos OK", "ok")
        time.sleep(0.2)

        atexit.register(lambda: cerrar(hardware))

        _log_splash(app, "Sistema listo", "ok")
        time.sleep(0.5)

        app.after(0, lambda: app.iniciar_normal(pagos, hardware, sensores))

    except Exception as e:
        log.critical("Error fatal durante inicializacion", exc_info=True)
        app.after(0, lambda: app.splash.agregar_linea(
            f"ERROR FATAL: {e}", "error"))
        app.after(0, lambda: app.splash.set_estado(
            "Fallo el inicio — revisar app.log"))


def main():
    log.info("=== Iniciando Sistema Dispenser %s v%s ===",
             config.EQUIPO_ID, config.APP_VERSION)

    signal.signal(signal.SIGTERM, lambda *_: cerrar())
    signal.signal(signal.SIGINT,  lambda *_: cerrar())

    from ui.app import DispenserApp
    app = DispenserApp()

    threading.Thread(target=_inicializar_en_hilo, args=(app,),
                      daemon=True).start()

    log.info("=== Splash en pantalla — entrando a mainloop ===")
    try:
        app.mainloop()
    except Exception:
        log.critical("Error fatal en mainloop", exc_info=True)
    finally:
        cerrar()


if __name__ == "__main__":
    main()
