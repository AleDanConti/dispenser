# ui/teclado_virtual.py
import tkinter as tk
from ui.theme import COLORS, FONTS

TECLAS_NUM = [
    ["7", "8", "9"],
    ["4", "5", "6"],
    ["1", "2", "3"],
    ["←", "0", "✓"],
]

TECLAS_ALFA = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "@"],
    ["z", "x", "c", "v", "b", "n", "m", ".", "_", "←"],
    ["MAYÚS", "ESPACIO", "✓"],
]

class TecladoVirtual(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#1E1E2E", **kwargs)
        self._var        = None
        self._on_confirm = None
        self._mayus      = False
        self._modo       = "num"

        self.lbl_preview = tk.Label(self, text="", font=FONTS["button"],
            bg="#2A2A3E", fg="white", anchor="e", padx=10)
        self.lbl_preview.pack(fill="x", pady=(6, 2), padx=6)

        self._frame_teclas = tk.Frame(self, bg="#1E1E2E")
        self._frame_teclas.pack(fill="both", expand=True, padx=4, pady=(0, 6))

    def abrir(self, var, modo="num", on_confirm=None):
        self._var        = var
        self._on_confirm = on_confirm
        self._modo       = modo
        self._mayus      = False
        self._construir_teclas()
        self._actualizar_preview()

    def _actualizar_preview(self):
        if self._var:
            self.lbl_preview.config(text=self._var.get())

    def _construir_teclas(self):
        for w in self._frame_teclas.winfo_children():
            w.destroy()
        teclas = TECLAS_NUM if self._modo == "num" else TECLAS_ALFA
        for fila in teclas:
            ff = tk.Frame(self._frame_teclas, bg="#1E1E2E")
            ff.pack(fill="x", pady=2)
            for t in fila:
                self._crear_boton(ff, t)

    def _crear_boton(self, parent, tecla):
        if tecla == "✓":
            bg, fg, w = COLORS["success"], "white", 6
        elif tecla == "←":
            bg, fg, w = COLORS["error"], "white", 4
        elif tecla in ("MAYÚS", "ESPACIO"):
            bg, fg, w = "#3A3A5E", "white", 10
        else:
            bg, fg, w = "#2A2A3E", "white", 4

        if self._modo == "alfa" and tecla not in (
                "←", "✓", "MAYÚS", "ESPACIO", "@", ".", "_", *"0123456789"):
            label = tecla.upper() if self._mayus else tecla.lower()
        else:
            label = tecla

        tk.Button(parent, text=label, font=FONTS["small"],
            bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
            relief="flat", width=w, height=2,
            command=lambda t=tecla: self._tecla(t)
        ).pack(side="left", padx=2)

    def _tecla(self, tecla):
        if self._var is None:
            return
        val = self._var.get()
        if tecla == "←":
            self._var.set(val[:-1])
        elif tecla == "✓":
            self.place_forget()
            if self._on_confirm:
                self._on_confirm()
        elif tecla == "MAYÚS":
            self._mayus = not self._mayus
            self._construir_teclas()
        elif tecla == "ESPACIO":
            self._var.set(val + " ")
        else:
            if self._modo == "alfa" and tecla not in (
                    "@", ".", "_", *"0123456789"):
                c = tecla.upper() if self._mayus else tecla.lower()
            else:
                c = tecla
            self._var.set(val + c)
        self._actualizar_preview()
