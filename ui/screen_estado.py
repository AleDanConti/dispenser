# ui/screen_estado.py
import threading
import tkinter as tk
from ui.base_screen import BaseScreen
from ui.theme import COLORS, FONTS

ESTADOS = {
    "aprobado":  {"color": "#2E7D32", "texto": "✓ Pago aprobado\nDispensando producto..."},
    "rechazado": {"color": "#C62828", "texto": "✗ Pago rechazado\nIntente nuevamente"},
    "timeout":   {"color": "#F9A825", "texto": "⏱ Tiempo agotado\nEl QR ha vencido"},
    "error":     {"color": "#C62828", "texto": "Error de conexión\nVerifique la señal 4G"},
}

class ScreenEstado(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.lbl_msg = tk.Label(self, text="", font=FONTS["subtitle"],
            bg=COLORS["bg"], fg=COLORS["text"], justify="center")
        self.lbl_msg.pack(expand=True, pady=(20, 5))

        self.lbl_cantidad = tk.Label(self, text="", font=FONTS["body"],
            bg=COLORS["bg"], fg="white")

        self.canvas_progreso = tk.Canvas(self, width=90, height=220,
            bg=COLORS["bg"], highlightthickness=0)
        self._rect_relleno = None
        self._progreso_coords = None

        self.frame_controles = tk.Frame(self, bg=COLORS["bg"])
        self.btn_pausa = tk.Button(self.frame_controles, text="⏸ Pausar",
            font=FONTS["small"], bg=COLORS["warning"], fg="white",
            relief="flat", width=12, command=self._toggle_pausa)
        self.btn_pausa.pack(side="left", padx=5)
        self.btn_cancelar_disp = tk.Button(self.frame_controles, text="✕ Cancelar",
            font=FONTS["small"], bg=COLORS["error"], fg="white",
            relief="flat", width=12, command=self._cancelar_dispensado)
        self.btn_cancelar_disp.pack(side="left", padx=5)

        self.btn_volver = tk.Button(self, text="Volver al inicio",
            font=FONTS["button"], bg=COLORS["primary"],
            fg=COLORS["text_light"], relief="flat",
            command=self._volver)
        self.btn_volver.pack(pady=20)

        self._after_id = None
        self._orden_id = None
        self._evento_pausa = None
        self._evento_cancelar = None
        self._pausado = False

    def on_show(self, estado="error", **kwargs):
        self._cancelar_after()
        self._orden_id = self.controller.state.get("orden_id")
        cfg = ESTADOS.get(estado, ESTADOS["error"])
        self.configure(bg=cfg["color"])
        self.lbl_msg.configure(bg=cfg["color"], fg="white", text=cfg["texto"])
        self.lbl_cantidad.configure(bg=cfg["color"])
        self.canvas_progreso.configure(bg=cfg["color"])
        self.frame_controles.configure(bg=cfg["color"])
        self.btn_pausa.configure(text="⏸ Pausar")
        self.btn_volver.configure(bg=COLORS["primary"])

        if estado == "aprobado":
            prod = self.controller.state.get("producto", {})
            vol  = self.controller.state.get("volumen", 0)
            orden_id = self._orden_id
            if self.controller.hardware:
                self.controller.hardware.set_led("pago", True)

            self.lbl_cantidad.configure(text=f"{int(vol)} ml")
            self.lbl_cantidad.pack(pady=(0, 5))
            self._iniciar_progreso()
            self.frame_controles.pack(pady=(5, 0))
            self.btn_volver.pack_forget()

            self._evento_pausa = threading.Event()
            self._evento_cancelar = threading.Event()
            self._pausado = False

            threading.Thread(target=self._dispensar_y_volver,
                args=(prod.get("id"), int(vol), orden_id), daemon=True).start()
        else:
            self.lbl_cantidad.pack_forget()
            self.canvas_progreso.pack_forget()
            self.frame_controles.pack_forget()
            self.btn_volver.pack(pady=20)
            self._after_id = self.after(6000, self._volver)

    def _iniciar_progreso(self):
        self.canvas_progreso.delete("all")
        w, h = 90, 220
        margen = 10
        x0, y0, x1, y1 = margen, margen, w - margen, h - margen

        self.canvas_progreso.create_rectangle(
            x0, y0, x1, y1, outline="white", width=3)
        self._rect_relleno = self.canvas_progreso.create_rectangle(
            x0 + 3, y1 - 3, x1 - 3, y1 - 3, fill="white", outline="")
        self._progreso_coords = (x0 + 3, y0 + 3, x1 - 3, y1 - 3)
        self.canvas_progreso.pack(pady=10)

    def _actualizar_progreso(self, frac):
        if self._progreso_coords is None:
            return
        cx0, cy0, cx1, cy1 = self._progreso_coords
        nuevo_y0 = cy1 - (cy1 - cy0) * frac
        self.after(0, lambda: self.canvas_progreso.coords(
            self._rect_relleno, cx0, nuevo_y0, cx1, cy1))

    def _toggle_pausa(self):
        if self._evento_pausa is None:
            return
        if self._pausado:
            self._evento_pausa.clear()
            self._pausado = False
            self.btn_pausa.configure(text="⏸ Pausar")
        else:
            self._evento_pausa.set()
            self._pausado = True
            self.btn_pausa.configure(text="▶ Reanudar")

    def _cancelar_dispensado(self):
        if self._evento_cancelar is not None:
            self._evento_cancelar.set()
        if self._evento_pausa is not None:
            self._evento_pausa.clear()
        self._pausado = False

    def _cancelar_after(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _volver(self):
        self._cancelar_after()
        self.frame_controles.pack_forget()
        self.canvas_progreso.pack_forget()
        self.lbl_cantidad.pack_forget()
        self.btn_volver.pack(pady=20)
        self.controller.show_frame("ScreenProducto")

    def _dispensar_y_volver(self, producto_id, volumen_cc, orden_id):
        completado = False
        if self.controller.hardware:
            completado = self.controller.hardware.dispensar_controlable(
                producto_id, volumen_cc,
                self._evento_pausa, self._evento_cancelar,
                on_progreso=self._actualizar_progreso)
            self.controller.hardware.set_led("pago", False)


        if self.controller.state.get("orden_id") == orden_id:
            self.after(0, self._volver)
