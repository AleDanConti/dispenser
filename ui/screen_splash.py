# ui/screen_splash.py
import os
import tkinter as tk
from PIL import Image, ImageTk
from ui.base_screen import BaseScreen
from ui.theme import COLORS, FONTS, SCREEN_W, SCREEN_H

LOGO_PATH = os.path.expanduser("~/dispenser/assets/logo.png")


class ScreenSplash(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.configure(bg="#0D1117")

        self._logo_img = None
        try:
            img = Image.open(LOGO_PATH)
            self._logo_img = ImageTk.PhotoImage(img)
            lbl_logo = tk.Label(self, image=self._logo_img, bg="#0D1117")
            lbl_logo.pack(pady=(40, 20))
        except Exception:
            tk.Label(self, text="Dispenser Inteligente", font=FONTS["title"],
                bg="#0D1117", fg="white").pack(pady=(60, 20))

        self.lbl_estado = tk.Label(self, text="Iniciando...",
            font=FONTS["small"], bg="#0D1117", fg="#8B949E")
        self.lbl_estado.pack(pady=(0, 5))

        frame_consola = tk.Frame(self, bg="#161B22",
            highlightbackground="#30363D", highlightthickness=1)
        frame_consola.pack(pady=10, padx=40, fill="both", expand=True)

        self.txt_consola = tk.Text(frame_consola, bg="#161B22", fg="#58A6FF",
            font=("Consolas", 11), relief="flat", wrap="none",
            state="disabled", height=12)
        self.txt_consola.pack(fill="both", expand=True, padx=8, pady=8)

    def on_show(self, **kwargs):
        pass

    def agregar_linea(self, texto, tipo="info"):
        color = {
            "info": "#58A6FF",
            "ok":   "#3FB950",
            "warn": "#D29922",
            "error":"#F85149",
        }.get(tipo, "#58A6FF")

        self.txt_consola.configure(state="normal")
        tag = f"tag_{tipo}"
        self.txt_consola.tag_configure(tag, foreground=color)
        self.txt_consola.insert("end", f"> {texto}\n", tag)
        self.txt_consola.see("end")
        self.txt_consola.configure(state="disabled")

    def set_estado(self, texto):
        self.lbl_estado.configure(text=texto)
