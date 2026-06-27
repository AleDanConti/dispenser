# ui/screen_volumen.py
import tkinter as tk
from ui.base_screen import BaseScreen
from ui.theme import COLORS, FONTS
from core.settings import load_settings

VOLUMENES = [
    {"cc": "500",  "label": "500 cc"},
    {"cc": "800",  "label": "800 cc"},
    {"cc": "2000", "label": "2 litros"},
    {"cc": "5000", "label": "5 litros"},
]

class ScreenVolumen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.lbl_producto = tk.Label(
            self, text="", font=FONTS["subtitle"],
            bg=COLORS["bg"], fg=COLORS["text"])
        self.lbl_producto.pack(pady=(25, 5))

        tk.Label(self, text="Seleccione la cantidad",
            font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["text"]
        ).pack(pady=(0, 10))

        grid = tk.Frame(self, bg=COLORS["bg"])
        grid.pack(expand=True, fill="both", padx=40, pady=5)
        for i in range(2):
            grid.rowconfigure(i, weight=1)
            grid.columnconfigure(i, weight=1)

        self.botones = []
        self._vol_seleccionado = None
        self._color_producto = COLORS["primary"]

        for idx, vol in enumerate(VOLUMENES):
            row, col = divmod(idx, 2)
            frame_btn = tk.Frame(grid, bg=COLORS["bg"])
            frame_btn.grid(row=row, column=col, sticky="nsew", padx=15, pady=10)
            frame_btn.rowconfigure(0, weight=1)
            frame_btn.columnconfigure(0, weight=1)
            btn = tk.Button(frame_btn, text="", font=FONTS["button"],
                bg=COLORS["primary"], fg=COLORS["text_light"],
                activebackground=COLORS["primary_dark"],
                activeforeground=COLORS["text_light"],
                relief="flat",
                command=lambda v=vol: self.seleccionar(v))
            btn.grid(sticky="nsew")
            self.botones.append((btn, vol))

        acciones = tk.Frame(self, bg=COLORS["bg"])
        acciones.pack(fill="x", padx=40, pady=(5, 15))
        acciones.columnconfigure(0, weight=1)
        acciones.columnconfigure(1, weight=1)
        acciones.columnconfigure(2, weight=1)

        tk.Button(acciones, text="← Volver", font=FONTS["button"],
            bg=COLORS["border"], fg=COLORS["text"],
            activebackground=COLORS["border"],
            activeforeground=COLORS["text"], relief="flat",
            command=lambda: controller.show_frame("ScreenProducto"),
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 5), ipady=10)

        self.btn_cancelar = tk.Button(acciones, text="✗ Cancelar",
            font=FONTS["button"], bg=COLORS["border"], fg=COLORS["text"],
            activebackground=COLORS["border"], activeforeground=COLORS["text"],
            relief="flat", state="disabled", command=self._cancelar)
        self.btn_cancelar.grid(row=0, column=1, sticky="nsew", padx=5, ipady=10)

        self.btn_pagar = tk.Button(acciones, text="Pagar →",
            font=FONTS["button"], bg=COLORS["border"], fg=COLORS["text"],
            activebackground=COLORS["border"], activeforeground=COLORS["text"],
            relief="flat", state="disabled", command=self._ir_a_pagar)
        self.btn_pagar.grid(row=0, column=2, sticky="nsew", padx=(5, 0), ipady=10)

    def on_show(self, **kwargs):
        producto = self.controller.state.get("producto")
        if not producto:
            return
        self._color_producto = producto["color"]
        self.lbl_producto.config(text=producto["nombre"])
        self._resetear()

    def _resetear(self):
        self._vol_seleccionado = None
        self.controller.state["volumen"] = None
        self.controller.state["precio"] = None
        producto = self.controller.state.get("producto", {})
        settings = load_settings()
        precios = settings.get("precios", {}).get(producto.get("id", ""), {})
        for btn, vol in self.botones:
            precio = precios.get(vol["cc"], 0)
            btn.config(
                text=f"{vol['label']}\n$ {precio:,}".replace(",", "."),
                bg=self._color_producto, fg=COLORS["text_light"],
                activebackground=self._color_producto,
                activeforeground=COLORS["text_light"],
                relief="flat", bd=0, state="normal")
        self.btn_cancelar.config(state="disabled",
            bg=COLORS["border"], fg=COLORS["text"])
        self.btn_pagar.config(state="disabled",
            bg=COLORS["border"], fg=COLORS["text"], text="Pagar →")

    def seleccionar(self, vol):
        producto = self.controller.state.get("producto")
        settings = load_settings()
        precio = settings.get("precios", {}).get(
            producto["id"], {}).get(vol["cc"], 0)
        self._vol_seleccionado = vol
        self.controller.state["volumen"] = vol["cc"]
        self.controller.state["precio"] = precio
        for btn, v in self.botones:
            if v["cc"] == vol["cc"]:
                btn.config(relief="solid", bd=4,
                    bg=COLORS["text_light"], fg=self._color_producto,
                    activebackground=COLORS["text_light"],
                    activeforeground=self._color_producto)
            else:
                btn.config(relief="flat", bd=0,
                    bg=self._color_producto, fg=COLORS["text_light"],
                    activebackground=self._color_producto,
                    activeforeground=COLORS["text_light"])
        self.btn_cancelar.config(state="normal",
            bg=COLORS["error"], fg=COLORS["text_light"],
            activebackground=COLORS["error"],
            activeforeground=COLORS["text_light"])
        self.btn_pagar.config(state="normal",
            bg=COLORS["success"], fg=COLORS["text_light"],
            activebackground=COLORS["success"],
            activeforeground=COLORS["text_light"],
            text=f"Pagar  $ {precio:,}".replace(",", "."))

    def _cancelar(self):
        self._resetear()

    def _ir_a_pagar(self):
        if self._vol_seleccionado:
            self.controller.show_frame("ScreenQR")
