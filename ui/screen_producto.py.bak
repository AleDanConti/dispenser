# ui/screen_producto.py
import tkinter as tk
from ui.base_screen import BaseScreen
from ui.theme import COLORS, FONTS
from core.settings import load_settings

PRODUCTOS = [
    {"id": "jabon_verde", "nombre": "Jabón Verde",        "color": "#43A047"},
    {"id": "jabon_azul",  "nombre": "Jabón Azul",          "color": "#1E88E5"},
    {"id": "suavizante",  "nombre": "Suavizante",          "color": "#8E24AA"},
    {"id": "limpiador",   "nombre": "Limpiador de Pisos",  "color": "#FB8C00"},
]

def get_productos():
    nombres = load_settings().get("nombres_productos", {})
    return [
        {**p, "nombre": nombres.get(p["id"], p["nombre"])}
        for p in PRODUCTOS
    ]

class ScreenProducto(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self, text="Seleccione un producto",
                 font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["text"]
                 ).pack(pady=(30, 20))

        self._grid = tk.Frame(self, bg=COLORS["bg"])
        self._grid.pack(expand=True, fill="both", padx=40, pady=10)

        for i in range(2):
            self._grid.rowconfigure(i, weight=1)
            self._grid.columnconfigure(i, weight=1)

        self._botones = []
        for idx in range(4):
            row, col = divmod(idx, 2)
            btn = tk.Button(
                self._grid, text="", font=FONTS["button"],
                fg=COLORS["text_light"], relief="flat",
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)
            self._botones.append(btn)

        cfg_btn = tk.Button(
            self, text="", bg=COLORS["bg"],
            activebackground=COLORS["border"],
            relief="flat", bd=0, width=2, height=1,
            command=lambda: controller.show_frame("ScreenPin"),
        )
        cfg_btn.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)

    def on_show(self, **kwargs):
        self.controller.state.update({
            "producto": None, "volumen": None, "precio": None,
            "orden_id": None, "qr_path": None,
        })
        productos = get_productos()
        for btn, prod in zip(self._botones, productos):
            btn.config(
                text=prod["nombre"],
                bg=prod["color"],
                activebackground=prod["color"],
                activeforeground=COLORS["text_light"],
                fg=COLORS["text_light"],
                command=lambda p=prod: self.seleccionar(p),
            )

    def seleccionar(self, producto):
        self.controller.state["producto"] = producto
        self.controller.show_frame("ScreenVolumen")
