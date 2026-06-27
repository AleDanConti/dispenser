# ui/screen_pin.py
import tkinter as tk
from ui.base_screen import BaseScreen
from ui.theme import COLORS, FONTS

class ScreenPin(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self, text="Acceso propietario",
            font=FONTS["subtitle"], bg=COLORS["bg"], fg=COLORS["text"]
        ).pack(pady=(60, 20))

        self._pin = ""

        self.lbl_pin = tk.Label(self, text="  ",
            font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["primary"])
        self.lbl_pin.pack(pady=10)

        self.lbl_error = tk.Label(self, text="",
            font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["error"])
        self.lbl_error.pack(pady=5)

        teclado = tk.Frame(self, bg=COLORS["bg"])
        teclado.pack(pady=10)

        teclas = ["1","2","3","4","5","6","7","8","9","←","0","✓"]

        for idx, tecla in enumerate(teclas):
            row, col = divmod(idx, 3)
            if tecla == "←":
                cmd = self._borrar
                color = COLORS["border"]
                fg = COLORS["text"]
            elif tecla == "✓":
                cmd = self._confirmar
                color = COLORS["primary"]
                fg = COLORS["text_light"]
            else:
                cmd = lambda t=tecla: self._agregar(t)
                color = COLORS["card"]
                fg = COLORS["text"]

            tk.Button(teclado, text=tecla, font=FONTS["button"],
                bg=color, fg=fg, activebackground=color,
                relief="flat", width=4, height=2, command=cmd,
            ).grid(row=row, column=col, padx=8, pady=8)

        tk.Button(self, text="← Cancelar", font=FONTS["small"],
            bg=COLORS["border"], fg=COLORS["text"], relief="flat",
            command=lambda: controller.show_frame("ScreenProducto"),
        ).pack(pady=15)

    def on_show(self, **kwargs):
        self._pin = ""
        self._actualizar_display()
        self.lbl_error.config(text="")

    def _agregar(self, digito):
        if len(self._pin) < 6:
            self._pin += digito
            self._actualizar_display()

    def _borrar(self):
        self._pin = self._pin[:-1]
        self._actualizar_display()

    def _actualizar_display(self):
        self.lbl_pin.config(text="● " * len(self._pin) or "  ")

    def _confirmar(self):
        import config
        if self._pin == config.PIN_PROPIETARIO:
            self.controller.show_frame("ScreenConfig")
        else:
            self.lbl_error.config(text="PIN incorrecto")
            self._pin = ""
            self._actualizar_display()
