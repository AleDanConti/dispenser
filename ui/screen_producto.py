# ui/screen_producto.py
import tkinter as tk
from PIL import Image, ImageTk
import os
import time
from ui.base_screen import BaseScreen
from core.settings import load_settings

BG         = "#0D1117"
CARD_BG    = "#161B22"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY  = "#8B949E"

FONT_TITLE  = ("DejaVu Sans", 30, "bold")
FONT_NAME   = ("DejaVu Sans", 24, "bold")
FONT_PRICE  = ("DejaVu Sans", 17)

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

PRODUCTOS = [
    {"id": "suavizante",  "nombre": "SUAVIZANTE",        "color": "#E040FB", "icon": "suavizante.png"},
    {"id": "jabon_verde", "nombre": "JABÓN VERDE",        "color": "#43A047", "icon": "jabon_verde.png"},
    {"id": "limpiador",   "nombre": "LIMPIADOR\nDE PISO", "color": "#FF8C00", "icon": "limpiador.png"},
    {"id": "jabon_azul",  "nombre": "JABÓN\nAZUL",        "color": "#29B6F6", "icon": "jabon_azul.png"},
]

def get_productos():
    nombres = load_settings().get("nombres_productos", {})
    return [
        {**p, "nombre": nombres.get(p["id"], p["nombre"])}
        for p in PRODUCTOS
    ]

def _precio_500(producto_id):
    precios = load_settings().get("precios", {})
    return precios.get(producto_id, {}).get("500", "—")


def _rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Dibuja un rectángulo con esquinas redondeadas en un Canvas."""
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class ScreenProducto(BaseScreen):

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.configure(bg=BG)
        self._icon_refs    = []
        self._price_labels = {}

        self._toque_izq = 0.0
        self._toque_der = 0.0
        self._TIMEOUT   = 2.0

        # ── Encabezado con círculos ──────────────────────
        header = tk.Frame(self, bg=BG)
        header.pack(pady=(16, 2))

        c_izq = tk.Canvas(header, width=34, height=34,
                          bg=BG, highlightthickness=0)
        c_izq.pack(side="left", padx=(0, 14))
        c_izq.create_oval(3, 3, 31, 31, fill=BG, outline="#3D5066", width=2)
        c_izq.bind("<Button-1>", self._toque_izquierdo)

        tk.Label(
            header, text="SELECCIONE PRODUCTO",
            font=FONT_TITLE, bg=BG, fg=TEXT_WHITE,
        ).pack(side="left")

        c_der = tk.Canvas(header, width=34, height=34,
                          bg=BG, highlightthickness=0)
        c_der.pack(side="left", padx=(14, 0))
        c_der.create_oval(3, 3, 31, 31, fill=BG, outline="#3D5066", width=2)
        c_der.bind("<Button-1>", self._toque_derecho)

        sep = tk.Frame(self, bg="#1E90FF", height=2, width=220)
        sep.pack()

        # ── Grilla de tarjetas ────────────────────────────
        grid = tk.Frame(self, bg=BG)
        grid.pack(expand=True, fill="both", padx=18, pady=(10, 10))
        for i in range(2):
            grid.rowconfigure(i, weight=1)
            grid.columnconfigure(i, weight=1)

        self._cards = []
        for idx, (row, col) in enumerate([(0,0),(0,1),(1,0),(1,1)]):
            card = self._make_card(grid, idx)
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=8)
            self._cards.append(card)

    def _toque_izquierdo(self, event=None):
        self._toque_izq = time.time()
        self._verificar_acceso()

    def _toque_derecho(self, event=None):
        self._toque_der = time.time()
        self._verificar_acceso()

    def _verificar_acceso(self):
        if (self._toque_izq > 0 and self._toque_der > 0 and
                abs(self._toque_izq - self._toque_der) <= self._TIMEOUT):
            self._toque_izq = 0.0
            self._toque_der = 0.0
            self.controller.show_frame("ScreenPin")

    def _make_card(self, parent, idx):
        prod  = PRODUCTOS[idx]
        color = prod["color"]

        # Contenedor que define el tamaño de la celda
        wrapper = tk.Frame(parent, bg=BG)
        wrapper.pack_propagate(True)

        canvas = tk.Canvas(wrapper, bg=BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def redraw(event=None, canvas=canvas, color=color):
            canvas.delete("bg")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w < 10 or h < 10:
                return
            _rounded_rect(canvas, 2, 2, w-2, h-2, radius=22,
                          fill=CARD_BG, outline=color, width=2, tags="bg")
            canvas.tag_lower("bg")

        canvas.bind("<Configure>", redraw)

        # Contenido superpuesto sobre el canvas
        content = tk.Frame(canvas, bg=CARD_BG)
        canvas.create_window(0, 0, window=content, anchor="nw",
                             width=1, height=1, tags="content")

        def resize_content(event, canvas=canvas, content=content):
            w = max(event.width - 16, 1)
            h = max(event.height - 16, 1)
            canvas.coords("content", 8, 8)
            canvas.itemconfig("content", width=w, height=h)
        canvas.bind("<Configure>", resize_content, add="+")

        left = tk.Frame(content, bg=CARD_BG, width=150)
        left.pack(side="left", fill="y", padx=(10, 0), pady=8)
        left.pack_propagate(False)

        right = tk.Frame(content, bg=CARD_BG)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        lbl_icon = tk.Label(left, bg=CARD_BG)
        lbl_icon.pack(expand=True)
        icon_path = os.path.join(ICON_DIR, prod["icon"])
        try:
            pil_img = Image.open(icon_path).resize((130, 130), Image.LANCZOS)
            tk_img  = ImageTk.PhotoImage(pil_img)
            lbl_icon.configure(image=tk_img)
            self._icon_refs.append(tk_img)
        except Exception:
            lbl_icon.configure(text="?", fg=color,
                               font=("DejaVu Sans", 40, "bold"))

        tk.Label(
            right, text=prod["nombre"],
            font=FONT_NAME, bg=CARD_BG, fg=color,
            justify="left", anchor="w",
        ).pack(anchor="w", pady=(8, 4))

        tk.Frame(right, bg=color, height=1).pack(fill="x", pady=(0, 8))

        lbl_precio = tk.Label(
            right, text="",
            font=FONT_PRICE, bg=CARD_BG, fg=TEXT_WHITE, anchor="w")
        lbl_precio.pack(anchor="w")
        self._price_labels[prod["id"]] = lbl_precio

        btn_frame = tk.Frame(right, bg=CARD_BG)
        btn_frame.pack(anchor="e", side="bottom", pady=(10, 4))
        btn_canvas = tk.Canvas(btn_frame, width=64, height=64,
                               bg=CARD_BG, highlightthickness=0)
        btn_canvas.pack()
        btn_canvas.create_oval(4, 4, 60, 60, fill=color, outline=color, width=2)
        btn_canvas.create_text(32, 32, text="▶", fill=CARD_BG,
                               font=("DejaVu Sans", 18, "bold"))

        for widget in (content, left, right, lbl_icon, btn_canvas, btn_frame, canvas):
            widget.bind("<Button-1>", lambda e, i=idx: self._on_card_click(i))

        return wrapper

    def _on_card_click(self, idx):
        self.seleccionar(get_productos()[idx])

    def on_show(self, **kwargs):
        self.controller.state.update({
            "producto": None, "volumen": None, "precio": None,
            "orden_id": None, "qr_path": None,
        })
        for prod in PRODUCTOS:
            precio = _precio_500(prod["id"])
            if isinstance(precio, (int, float)):
                texto = f"500 cm³  —  ${int(precio):,}".replace(",", ".")
            else:
                texto = f"500 cm³  —  ${precio}"
            lbl = self._price_labels.get(prod["id"])
            if lbl:
                lbl.config(text=texto)

    def seleccionar(self, producto):
        self.controller.state["producto"] = producto
        self.controller.show_frame("ScreenVolumen")
