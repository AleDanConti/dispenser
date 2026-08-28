# ui/screen_saver.py
import os
import tkinter as tk
import vlc
import logging
from ui.base_screen import BaseScreen
from ui.theme import COLORS

log = logging.getLogger(__name__)

VIDEO_PATH = os.path.expanduser("~/dispenser/assets/screensaver.mp4")


class ScreenSaver(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.configure(bg="black")

        self._video_frame = tk.Frame(self, bg="black")
        self._video_frame.pack(fill="both", expand=True)
        self._video_frame.bind("<Button-1>", self._salir)

        self._instance = None
        self._player = None
        self._activo = False

        try:
            self._instance = vlc.Instance("--no-xlib", "--quiet")
            self._player = self._instance.media_player_new()
        except Exception as e:
            log.error("No se pudo inicializar VLC: %s", e)

    def on_show(self, **kwargs):
        if not self._player or not os.path.exists(VIDEO_PATH):
            log.warning("Screensaver no disponible (sin VLC o sin video)")
            self.controller.show_frame("ScreenProducto")
            return

        self._activo = True
        media = self._instance.media_new(VIDEO_PATH)
        media.add_option("input-repeat=-1")  # loop infinito
        self._player.set_media(media)
        self._player.audio_set_mute(True)

        self.update_idletasks()
        self._player.set_xwindow(self._video_frame.winfo_id())
        self._player.play()
        self._player.event_manager().event_attach(
            vlc.EventType.MediaPlayerEndReached, self._on_fin_video)
        log.info("Screensaver iniciado")

    def _salir(self, event=None):
        if not self._activo:
            return
        self._activo = False
        if self._player:
            self._player.stop()
        log.info("Screensaver detenido por toque de pantalla")
        self.controller.show_frame("ScreenProducto")

    def detener(self):
        """Llamado externamente si hace falta cortar el video sin pasar por _salir."""
        self._salir()
    def _on_fin_video(self, event):
        # Este callback corre en el hilo de VLC, no en el de Tkinter —
        # hay que pasar el reinicio al hilo principal con after(0, ...)
        if self._activo:
            self.after(0, self._reiniciar_video)

    def _reiniciar_video(self):
        if self._activo and self._player:
            self._player.stop()
            self._player.play()
