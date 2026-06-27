# ui/app.py
import tkinter as tk
from ui.theme import COLORS, SCREEN_W, SCREEN_H


class DispenserApp(tk.Tk):
    def __init__(self, payments=None, hardware=None, sensors=None):
        super().__init__()

        self.payments = payments
        self.hardware = hardware
        self.sensors  = sensors

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
        self.show_frame("ScreenProducto")

    def _cargar_pantallas(self, contenedor):
        from ui.screen_producto import ScreenProducto
        from ui.screen_volumen  import ScreenVolumen
        from ui.screen_qr       import ScreenQR
        from ui.screen_estado   import ScreenEstado
        from ui.screen_pin      import ScreenPin
        from ui.screen_config   import ScreenConfig

        for PantallaCls in (
            ScreenProducto, ScreenVolumen, ScreenQR,
            ScreenEstado, ScreenPin, ScreenConfig,
        ):
            nombre = PantallaCls.__name__
            frame = PantallaCls(contenedor, self)
            self._frames[nombre] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, nombre, **kwargs):
        frame = self._frames[nombre]
        frame.tkraise()
        frame.on_show(**kwargs)
