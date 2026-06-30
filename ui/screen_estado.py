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
        self.lbl_msg.pack(expand=True, pady=20)

        self.btn_volver = tk.Button(self, text="Volver al inicio",
            font=FONTS["button"], bg=COLORS["primary"],
            fg=COLORS["text_light"], relief="flat",
            command=self._volver)
        self.btn_volver.pack(pady=20)

        self._after_id = None
        self._orden_id = None

    def on_show(self, estado="error", **kwargs):
        self._cancelar_after()
        self._orden_id = self.controller.state.get("orden_id")
        cfg = ESTADOS.get(estado, ESTADOS["error"])
        self.configure(bg=cfg["color"])
        self.lbl_msg.configure(bg=cfg["color"], fg="white", text=cfg["texto"])
        self.btn_volver.configure(bg=COLORS["primary"])

        if estado == "aprobado":
            prod = self.controller.state.get("producto", {})
            vol  = self.controller.state.get("volumen", 0)
            orden_id = self._orden_id
            if self.controller.hardware:
                self.controller.hardware.set_led("pago", True)
            threading.Thread(target=self._dispensar_y_volver,
                args=(prod.get("id"), int(vol), orden_id), daemon=True).start()
        else:
            self._after_id = self.after(6000, self._volver)

    def _cancelar_after(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _volver(self):
        self._cancelar_after()
        self.controller.show_frame("ScreenProducto")

    def _dispensar_y_volver(self, producto_id, volumen_cc, orden_id):
        if self.controller.hardware:
            self.controller.hardware.dispensar(producto_id, volumen_cc)
            self.controller.hardware.set_led("pago", False)

        # Notificación de prueba — confirma que el canal de WhatsApp funciona
        try:
            from core.notificaciones import notificar_compra
            prod = self.controller.state.get("producto", {})
            precio = self.controller.state.get("precio", 0)
            notificar_compra(
                prod.get("nombre", producto_id), volumen_cc, precio)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f"No se pudo notificar la compra: {e}")

        if self.controller.state.get("orden_id") == orden_id:
            self.after(0, self._volver)
