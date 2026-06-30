# ui/screen_config.py
import tkinter as tk
import subprocess
from ui.base_screen import BaseScreen
from ui.theme import COLORS, FONTS
from ui.teclado_virtual import TecladoVirtual
from core import settings
import config

PRODUCTOS_DEFAULT = [
    {"id": "jabon_verde", "nombre": "Jabón Verde",       "color": "#43A047"},
    {"id": "jabon_azul",  "nombre": "Jabón Azul",         "color": "#1E88E5"},
    {"id": "suavizante",  "nombre": "Suavizante",         "color": "#8E24AA"},
    {"id": "limpiador",   "nombre": "Limpiador de Pisos", "color": "#FB8C00"},
]

class ScreenConfig(BaseScreen):

    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self, text="Configuración", font=FONTS["title"],
            bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(10, 3))

        tabs = tk.Frame(self, bg=COLORS["bg"])
        tabs.pack(pady=4)
        self.contenedor = tk.Frame(self, bg=COLORS["bg"])
        self.contenedor.pack(fill="both", expand=True, padx=20)

        self.secciones = {}
        for clave, texto in [
            ("productos", "Productos"),
            ("niveles",   "Niveles"),
            ("precios",   "Precios"),
            ("notif",     "Notificaciones"),
        ]:
            tk.Button(tabs, text=texto, font=FONTS["small"],
                bg=COLORS["border"], relief="flat",
                command=lambda c=clave: self._mostrar(c)
            ).pack(side="left", padx=4)

        sistema = tk.Frame(self, bg=COLORS["bg"])
        sistema.pack(fill="x", padx=20, pady=6)
        sistema.columnconfigure(0, weight=1)
        sistema.columnconfigure(1, weight=1)
        sistema.columnconfigure(2, weight=1)

        tk.Button(sistema, text="← Volver", font=FONTS["button"],
            bg=COLORS["primary"], fg=COLORS["text_light"],
            activebackground=COLORS["primary_dark"],
            activeforeground=COLORS["text_light"], relief="flat",
            command=lambda: controller.show_frame("ScreenProducto")
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 5), ipady=8)

        tk.Button(sistema, text="⟳ Reiniciar", font=FONTS["button"],
            bg=COLORS["warning"], fg=COLORS["text"],
            activebackground=COLORS["warning"],
            activeforeground=COLORS["text"], relief="flat",
            command=self._confirmar_reinicio
        ).grid(row=0, column=1, sticky="nsew", padx=5, ipady=8)

        tk.Button(sistema, text="⏻ Apagar", font=FONTS["button"],
            bg=COLORS["error"], fg=COLORS["text_light"],
            activebackground=COLORS["error"],
            activeforeground=COLORS["text_light"], relief="flat",
            command=self._confirmar_apagado
        ).grid(row=0, column=2, sticky="nsew", padx=(5, 0), ipady=8)

        self.msg_lbl = tk.Label(self, text="", font=FONTS["small"],
            bg=COLORS["bg"], fg=COLORS["success"])
        self.msg_lbl.pack()

        self.teclado = TecladoVirtual(self)

        self._construir_productos()
        self._construir_niveles()
        self._construir_precios()
        self._construir_notif()

    def on_show(self, **kwargs):
        self.teclado.place_forget()
        self._mostrar("productos")
        self._refrescar_productos()
        self._refrescar_niveles()
        self._refrescar_precios()
        self._refrescar_notif()

    def _mostrar(self, clave):
        self.teclado.place_forget()
        for f in self.secciones.values():
            f.pack_forget()
        self.secciones[clave].pack(fill="both", expand=True)
        self.msg_lbl.config(text="")

    def _abrir_teclado(self, var, modo="alfa", on_confirm=None):
        self.teclado.abrir(var, modo=modo, on_confirm=on_confirm)
        self.teclado.place(relx=0, rely=1.0, anchor="sw", relwidth=1.0)
        self.teclado.lift()

    def _confirmar_reinicio(self):
        self._dialogo("¿Reiniciar el sistema?",
            "El equipo se reiniciará ahora.", callback=self._reiniciar)

    def _confirmar_apagado(self):
        self._dialogo("¿Apagar el sistema?",
            "El equipo se apagará ahora.", callback=self._apagar)

    def _dialogo(self, titulo, mensaje, callback):
        overlay = tk.Frame(self, bg="#000000")
        overlay.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        overlay.lift()
        card = tk.Frame(overlay, bg=COLORS["card"], relief="solid", bd=1)
        card.place(relx=0.5, rely=0.4, anchor="center", width=420, height=200)
        tk.Label(card, text=titulo, font=FONTS["subtitle"],
            bg=COLORS["card"], fg=COLORS["text"]).pack(pady=(20, 5))
        tk.Label(card, text=mensaje, font=FONTS["body"],
            bg=COLORS["card"], fg=COLORS["text"]).pack(pady=(0, 15))
        btns = tk.Frame(card, bg=COLORS["card"])
        btns.pack()
        tk.Button(btns, text="Cancelar", font=FONTS["button"],
            bg=COLORS["border"], fg=COLORS["text"],
            relief="flat", width=10,
            command=overlay.destroy).pack(side="left", padx=10)
        tk.Button(btns, text="Confirmar", font=FONTS["button"],
            bg=COLORS["error"], fg=COLORS["text_light"],
            relief="flat", width=10,
            command=lambda: [overlay.destroy(), callback()]
        ).pack(side="left", padx=10)

    def _reiniciar(self):
        self.msg_lbl.config(text="Reiniciando...")
        self.after(500, lambda: subprocess.run(
            ["sudo", "/usr/sbin/reboot"], check=False))

    def _apagar(self):
        self.msg_lbl.config(text="Apagando...")
        self.after(500, lambda: subprocess.run(
            ["sudo", "/usr/sbin/poweroff"], check=False))

    def _construir_productos(self):
        frame = tk.Frame(self.contenedor, bg=COLORS["bg"])
        self.secciones["productos"] = frame
        self.nombre_vars = {}
        tk.Label(frame, text="Nombre visible en pantalla",
            font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text"]
        ).pack(anchor="w", pady=(5, 2))
        for prod in PRODUCTOS_DEFAULT:
            fila = tk.Frame(frame, bg=COLORS["bg"])
            fila.pack(fill="x", pady=5)
            tk.Label(fila, text="  ", bg=prod["color"],
                width=2).pack(side="left", padx=(0, 8))
            var = tk.StringVar(value=prod["nombre"])
            self.nombre_vars[prod["id"]] = var
            tk.Label(fila, textvariable=var, font=FONTS["body"],
                bg=COLORS["card"], fg=COLORS["text"],
                anchor="w", width=22, relief="solid", bd=1,
            ).pack(side="left")
            tk.Button(fila, text="✏ Editar", font=FONTS["small"],
                bg=COLORS["primary"], fg=COLORS["text_light"], relief="flat",
                command=lambda v=var: self._abrir_teclado(v, modo="alfa",
                    on_confirm=self._guardar_productos)
            ).pack(side="left", padx=8)
        tk.Button(frame, text="Guardar nombres", font=FONTS["body"],
            bg=COLORS["primary"], fg=COLORS["text_light"], relief="flat",
            command=self._guardar_productos).pack(pady=10)

    def _refrescar_productos(self):
        data = settings.load_settings()
        nombres = data.get("nombres_productos", {})
        for pid, var in self.nombre_vars.items():
            default = next((p["nombre"] for p in PRODUCTOS_DEFAULT
                if p["id"] == pid), pid)
            var.set(nombres.get(pid, default))

    def _guardar_productos(self):
        data = settings.load_settings()
        data["nombres_productos"] = {pid: var.get().strip()
            for pid, var in self.nombre_vars.items()}
        settings.save_settings(data)
        self.msg_lbl.config(text="Nombres guardados")
        self.after(1500, lambda: self.msg_lbl.config(text=""))

    def _construir_niveles(self):
        frame = tk.Frame(self.contenedor, bg=COLORS["bg"])
        self.secciones["niveles"] = frame
        self.umbral_vars = {}
        for prod in PRODUCTOS_DEFAULT:
            fila = tk.Frame(frame, bg=COLORS["bg"])
            fila.pack(fill="x", pady=6)
            tk.Label(fila, text="  ", bg=prod["color"],
                width=2).pack(side="left", padx=(0, 8))
            tk.Label(fila, text=prod["nombre"], font=FONTS["body"],
                width=16, anchor="w", bg=COLORS["bg"]).pack(side="left")
            tk.Label(fila, text="Alerta %:", font=FONTS["small"],
                bg=COLORS["bg"]).pack(side="left", padx=(10, 4))
            var = tk.StringVar()
            self.umbral_vars[prod["id"]] = var
            tk.Label(fila, textvariable=var, font=FONTS["body"],
                bg=COLORS["card"], fg=COLORS["text"],
                width=5, relief="solid", bd=1, anchor="center",
            ).pack(side="left")
            tk.Button(fila, text="✏", font=FONTS["small"],
                bg=COLORS["primary"], fg=COLORS["text_light"],
                relief="flat", width=2,
                command=lambda v=var: self._abrir_teclado(v, modo="num")
            ).pack(side="left", padx=6)
        tk.Button(frame, text="Guardar umbrales", font=FONTS["body"],
            bg=COLORS["primary"], fg=COLORS["text_light"], relief="flat",
            command=self._guardar_umbrales).pack(pady=10)

    def _refrescar_niveles(self):
        data = settings.load_settings()
        umbrales = data.get("umbrales_alerta", {})
        for pid, var in self.umbral_vars.items():
            var.set(str(umbrales.get(pid, 20)))

    def _guardar_umbrales(self):
        data = settings.load_settings()
        data["umbrales_alerta"] = {}
        for pid, var in self.umbral_vars.items():
            try:
                data["umbrales_alerta"][pid] = int(var.get())
            except ValueError:
                data["umbrales_alerta"][pid] = 20
        settings.save_settings(data)
        self.msg_lbl.config(text="Umbrales guardados")
        self.after(1500, lambda: self.msg_lbl.config(text=""))

    def _construir_precios(self):
        frame = tk.Frame(self.contenedor, bg=COLORS["bg"])
        self.secciones["precios"] = frame
        self.precio_vars = {}
        volumenes = ["500", "800", "2000", "5000"]
        etiquetas = ["500cc", "800cc", "2L", "5L"]

        # Header: misma estructura que las filas de datos
        # (placeholder color + nombre + N columnas de precio)
        header = tk.Frame(frame, bg=COLORS["bg"])
        header.pack(fill="x", pady=(5, 2))
        tk.Label(header, text="  ", bg=COLORS["bg"],
            width=2).pack(side="left", padx=(0, 4))
        tk.Label(header, text="Producto", font=FONTS["small"],
            bg=COLORS["bg"], width=16, anchor="w").pack(side="left")
        for etq in etiquetas:
            tk.Label(header, text=etq, font=FONTS["small"],
                bg=COLORS["bg"], width=6, anchor="e",
                padx=3).pack(side="left", padx=2)

        for prod in PRODUCTOS_DEFAULT:
            fila = tk.Frame(frame, bg=COLORS["bg"])
            fila.pack(fill="x", pady=4)
            tk.Label(fila, text="  ", bg=prod["color"],
                width=2).pack(side="left", padx=(0, 4))
            tk.Label(fila, text=prod["nombre"], font=FONTS["small"],
                width=16, anchor="w", bg=COLORS["bg"]).pack(side="left")
            self.precio_vars[prod["id"]] = {}
            for vol in volumenes:
                var = tk.StringVar()
                self.precio_vars[prod["id"]][vol] = var
                lbl = tk.Label(fila, textvariable=var, font=FONTS["small"],
                    bg=COLORS["card"], fg=COLORS["text"],
                    width=6, relief="solid", bd=1, anchor="e", padx=3)
                lbl.pack(side="left", padx=2)
                lbl.bind("<Button-1>",
                    lambda e, v=var: self._abrir_teclado(v, modo="num"))
        tk.Button(frame, text="Guardar precios", font=FONTS["body"],
            bg=COLORS["primary"], fg=COLORS["text_light"], relief="flat",
            command=self._guardar_precios).pack(pady=10)

    def _refrescar_precios(self):
        data = settings.load_settings()
        precios = data.get("precios", {})
        for pid, vols in self.precio_vars.items():
            for vol, var in vols.items():
                val = precios.get(pid, {}).get(vol, 0)
                var.set(str(val))

    def _guardar_precios(self):
        data = settings.load_settings()
        precios = {}
        for pid, vols in self.precio_vars.items():
            precios[pid] = {}
            for vol, var in vols.items():
                try:
                    precios[pid][vol] = int(var.get())
                except ValueError:
                    precios[pid][vol] = 0
        data["precios"] = precios
        settings.save_settings(data)
        self.msg_lbl.config(text="Precios guardados")
        self.after(1500, lambda: self.msg_lbl.config(text=""))

    def _construir_notif(self):
        frame = tk.Frame(self.contenedor, bg=COLORS["bg"])
        self.secciones["notif"] = frame
        self.notif_vars = {}
        for etq, clave in [
            ("Email destino",   "alertas_email"),
            ("WhatsApp número", "alertas_whatsapp_numero"),
        ]:
            fila = tk.Frame(frame, bg=COLORS["bg"])
            fila.pack(fill="x", pady=10)
            tk.Label(fila, text=etq, font=FONTS["body"],
                bg=COLORS["bg"], width=18, anchor="w").pack(side="left")
            var = tk.StringVar()
            self.notif_vars[clave] = var
            lbl = tk.Label(fila, textvariable=var, font=FONTS["body"],
                bg=COLORS["card"], fg=COLORS["text"],
                width=22, relief="solid", bd=1, anchor="w", padx=4)
            lbl.pack(side="left")
            lbl.bind("<Button-1>",
                lambda e, v=var: self._abrir_teclado(v, modo="alfa"))
            tk.Button(fila, text="✏", font=FONTS["small"],
                bg=COLORS["primary"], fg=COLORS["text_light"],
                relief="flat", width=2,
                command=lambda v=var: self._abrir_teclado(v, modo="alfa")
            ).pack(side="left", padx=6)
        tk.Button(frame, text="Guardar notificaciones", font=FONTS["body"],
            bg=COLORS["primary"], fg=COLORS["text_light"], relief="flat",
            command=self._guardar_notif).pack(pady=10)

    def _refrescar_notif(self):
        data = settings.load_settings()
        for clave, var in self.notif_vars.items():
            var.set(data.get(clave) or "")

    def _guardar_notif(self):
        data = settings.load_settings()
        for clave, var in self.notif_vars.items():
            val = var.get().strip()
            data[clave] = val if val else None
        settings.save_settings(data)
        self.msg_lbl.config(text="Notificaciones guardadas")
        self.after(1500, lambda: self.msg_lbl.config(text=""))
