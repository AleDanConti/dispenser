# ui/app.py
import tkinter as tk
from ui.theme import COLORS, SCREEN_W, SCREEN_H


class DispenserApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.payments = None
        self.hardware = None
        self.sensors  = None

        self.state = {
            "producto":  None,
            "volumen":   None,
            "precio":    None,
            "orden_id":  None,
            "qr_path":   None,
        }

        self.title("Dispenser Inteligente")
        self.configure(bg=COLORS["bg"])
        self.resizable(False, False)
        self.overrideredirect(True)
        self.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")

        contenedor = tk.Frame(self, bg=COLORS["bg"])
        contenedor.pack(fill="both", expand=True)
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        self._frames = {}
        self._cargar_pantallas(contenedor)
        self.show_frame("ScreenSplash")

    def _cargar_pantallas(self, contenedor):
        from ui.screen_splash   import ScreenSplash
        from ui.screen_producto import ScreenProducto
        from ui.screen_volumen  import ScreenVolumen
        from ui.screen_qr       import ScreenQR
        from ui.screen_estado   import ScreenEstado
        from ui.screen_pin      import ScreenPin
        from ui.screen_config   import ScreenConfig

        for PantallaCls in (
            ScreenSplash, ScreenProducto, ScreenVolumen, ScreenQR,
            ScreenEstado, ScreenPin, ScreenConfig,
        ):
            nombre = PantallaCls.__name__
            frame = PantallaCls(contenedor, self)
            self._frames[nombre] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    @property
    def splash(self):
        return self._frames["ScreenSplash"]

    def iniciar_normal(self, payments, hardware, sensors):
        """Llamado una vez que el arranque (Etapa 5/6/pagos) termino."""
        self.payments = payments
        self.hardware = hardware
        self.sensors  = sensors
        self.show_frame("ScreenProducto")

    def show_frame(self, nombre, **kwargs):
        frame = self._frames[nombre]
        frame.tkraise()
        frame.on_show(**kwargs)
