# main.py
import logging
import sys
import os
import atexit
import signal
import threading
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


def cerrar(hardware):
    log.info("Cerrando aplicacion...")
    if hardware:
        hardware.cleanup()
    sys.exit(0)


def manejar_alertas(alertas, niveles_actuales=None):
    from core.notificaciones import enviar_alertas
    enviar_alertas(alertas, niveles_actuales)


def main():
    log.info("=== Iniciando Sistema Dispenser %s v%s ===",
             config.EQUIPO_ID, config.APP_VERSION)

    if config.SIMULATION_MODE:
        log.warning("SIMULATION_MODE activo — usando mocks")
        from payments.mock_provider import MockPaymentProvider as PP
        from hardware.mock_hardware import MockHardware as HW
        from sensors.mock_sensors   import MockSensors as SS
    else:
        from payments.mobbex_provider import MobbexPaymentProvider as PP
        from hardware.gpio_hardware   import GpioHardware as HW
        from sensors.hc_sr04          import HcSr04Sensors as SS

    hardware = HW()

    sensores = SS(
        hardware=hardware,
        on_alerta=lambda a, n: manejar_alertas(a, n))
    if not config.SIMULATION_MODE:
        sensores.iniciar_monitoreo(config.MONITOREO_INTERVALO_SEG)

    pagos = PP()

    atexit.register(lambda: cerrar(hardware))
    signal.signal(signal.SIGTERM, lambda *_: cerrar(hardware))
    signal.signal(signal.SIGINT,  lambda *_: cerrar(hardware))

    from ui.app import DispenserApp
    app = DispenserApp(
        payments=pagos,
        hardware=hardware,
        sensors=sensores,
    )

    log.info("=== Sistema listo — entrando a mainloop ===")
    try:
        app.mainloop()
    except Exception:
        log.critical("Error fatal en mainloop", exc_info=True)
    finally:
        cerrar(hardware)


if __name__ == "__main__":
    main()
