# ui/screen_qr.py
import threading
import tkinter as tk
from PIL import Image, ImageTk
from ui.base_screen import BaseScreen
from ui.theme import COLORS, FONTS

class ScreenQR(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.lbl_producto = tk.Label(self, text="", font=FONTS["subtitle"],
            bg=COLORS["bg"], fg=COLORS["text"])
        self.lbl_producto.pack(pady=(20, 2))

        self.lbl_precio = tk.Label(self, text="", font=FONTS["price"],
            bg=COLORS["bg"], fg=COLORS["primary"])
        self.lbl_precio.pack(pady=(0, 10))

        self.lbl_qr = tk.Label(self, bg=COLORS["bg"])
        self.lbl_qr.pack(pady=5)

        self.lbl_estado = tk.Label(self, text="Generando QR...",
            font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"])
        self.lbl_estado.pack(pady=5)

        tk.Button(self, text="← Cancelar", font=FONTS["small"],
            bg=COLORS["border"], fg=COLORS["text"], relief="flat",
            command=self._cancelar).pack(pady=(5, 15))

        self._imagen_qr   = None
        self._polling     = False
        self._consultando = False
        self._restante    = 0
        self._tick_id     = None

    def on_show(self, **kwargs):
        self._detener()
        prod  = self.controller.state.get("producto", {})
        precio = self.controller.state.get("precio", 0)
        self.lbl_producto.config(text=prod.get("nombre", ""))
        self.lbl_precio.config(text=f"$ {int(precio):,}".replace(",", "."))
        self.lbl_estado.config(text="Generando QR...", fg=COLORS["text"])
        self.lbl_qr.config(image="")
        self._imagen_qr = None
        self._polling = True
        threading.Thread(target=self._generar_qr, daemon=True).start()

    def _detener(self):
        self._polling = False
        self._consultando = False
        if self._tick_id is not None:
            try:
                self.after_cancel(self._tick_id)
            except Exception:
                pass
            self._tick_id = None

    def _cancelar(self):
        self._detener()
        orden_id = self.controller.state.get("orden_id")
        if orden_id and self.controller.payments:
            try:
                self.controller.payments.cancelar_orden(orden_id)
            except Exception:
                pass
        if self.controller.hardware:
            self.controller.hardware.set_led("qr", False)
        self.controller.show_frame("ScreenProducto")

    def _generar_qr(self):
        try:
            orden = self.controller.payments.crear_orden(
                total=self.controller.state["precio"],
                descripcion=self.controller.state["producto"]["nombre"])
            self.controller.state["orden_id"] = orden["orden_id"]
            self.controller.state["qr_path"]  = orden["qr_path"]
            self.after(0, lambda: self._mostrar_qr(
                orden["qr_path"], orden["expira_en"]))
        except Exception as e:
            self.after(0, lambda: self.lbl_estado.config(
                text=f"Error de red: {e}", fg=COLORS["error"]))

    def _mostrar_qr(self, qr_path, expira_en):
        if not self._polling:
            return
        try:
            img = Image.open(qr_path).resize((280, 280))
            self._imagen_qr = ImageTk.PhotoImage(img)
            self.lbl_qr.config(image=self._imagen_qr)
        except Exception:
            pass
        self.lbl_estado.config(text="Escanee el QR para pagar", fg=COLORS["text"])
        if self.controller.hardware:
            self.controller.hardware.set_led("qr", True)
        self._restante = expira_en
        self._tick()

    def _tick(self):
        if not self._polling:
            self._tick_id = None
            return
        if self._restante % 3 == 0 and not self._consultando:
            self._consultando = True
            threading.Thread(target=self._consultar_async, daemon=True).start()
        mins, secs = divmod(max(self._restante, 0), 60)
        self.lbl_estado.config(text=f"Esperando pago... {mins:02d}:{secs:02d}")
        if self._restante <= 0:
            self._detener()
            orden_id = self.controller.state.get("orden_id")
            if orden_id and self.controller.payments:
                try:
                    self.controller.payments.cancelar_orden(orden_id)
                except Exception:
                    pass
            if self.controller.hardware:
                self.controller.hardware.set_led("qr", False)
            self.controller.show_frame("ScreenEstado", estado="timeout")
            return
        self._restante -= 1
        self._tick_id = self.after(1000, self._tick)

    def _consultar_async(self):
        try:
            estado = self.controller.payments.consultar_estado(
                self.controller.state["orden_id"])
        except Exception:
            estado = "pending"
        finally:
            self._consultando = False
        if self._polling:
            self.after(0, lambda: self._procesar_estado(estado))

    def _procesar_estado(self, estado):
        if not self._polling:
            return
        if estado == "approved":
            self._detener()
            if self.controller.hardware:
                self.controller.hardware.set_led("qr", False)
            self.controller.show_frame("ScreenEstado", estado="aprobado")
        elif estado == "rejected":
            self._detener()
            if self.controller.hardware:
                self.controller.hardware.set_led("qr", False)
            self.controller.show_frame("ScreenEstado", estado="rechazado")
